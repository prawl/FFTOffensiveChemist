"""FF16Tools nxd encode/decode + deploy helpers.

NXD overrides are full-table replace and the base game pacs are encrypted, so every
FF16Tools call carries -g fft. A failed encode leaves no output file (or a partial set),
which the modloader would treat as "no override" -- so encode_sqlite_to_nxd refuses to
return without the expected file.
"""
import shutil
import subprocess

from .paths import FF16


def encode_sqlite_to_nxd(sqlite, out_dir, nxd_name):
    """Encode a working sqlite to nxd via FF16Tools; return the built nxd Path.

    SystemExit (with the encoder's output) if the expected file does not appear."""
    out_dir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(FF16), "sqlite-to-nxd", "-i", str(sqlite), "-o", str(out_dir), "-g", "fft"],
                       capture_output=True, text=True)
    out = out_dir / nxd_name
    if r.returncode != 0 or not out.exists():
        produced = [f.name for f in out_dir.glob("*.nxd")]
        raise SystemExit(f"ENCODE FAILED (expected {nxd_name}, encoder produced {produced}):\n"
                         + r.stdout + r.stderr)
    return out


def extract_from_pac(pac, internal_path, out_dir):
    """Extract one file (e.g. 'nxd/item.en.nxd') out of an FF16 pac via FF16Tools; return its Path.

    The base game pacs are encrypted, hence -g fft. FF16Tools preserves the internal directory
    structure under out_dir (so 'nxd/item.en.nxd' lands at out_dir/nxd/item.en.nxd). SystemExit
    (with the tool's output) if the expected file does not appear."""
    out_dir.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(FF16), "unpack", "-i", str(pac), "-f", internal_path,
                        "-o", str(out_dir), "-g", "fft"], capture_output=True, text=True)
    out = out_dir / internal_path
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f"PAC EXTRACT FAILED ({internal_path} from {pac}):\n" + r.stdout + r.stderr)
    return out


def decode_nxd_to_sqlite(nxd, out_sqlite):
    """Decode a single .en.nxd into a sqlite via FF16Tools; return the sqlite Path.

    FF16Tools takes an INPUT DIRECTORY, so the nxd is staged into a temp 'in' folder next
    to the output. SystemExit (with the decoder's output) if the sqlite does not appear."""
    out_sqlite.parent.mkdir(parents=True, exist_ok=True)
    if out_sqlite.exists():          # FF16Tools appends to an existing db; start clean every time
        out_sqlite.unlink()
    in_dir = out_sqlite.parent / (out_sqlite.stem + "_in")
    if in_dir.exists():
        shutil.rmtree(in_dir)
    in_dir.mkdir(parents=True)
    shutil.copy(nxd, in_dir / nxd.name)
    r = subprocess.run([str(FF16), "nxd-to-sqlite", "-i", str(in_dir), "-o", str(out_sqlite), "-g", "fft"],
                       capture_output=True, text=True)
    shutil.rmtree(in_dir, ignore_errors=True)
    if r.returncode != 0 or not out_sqlite.exists():
        raise SystemExit(f"DECODE FAILED (expected {out_sqlite.name}):\n" + r.stdout + r.stderr)
    return out_sqlite


def deploy_nxd(built, dest):
    """Copy a built nxd into place (mod tree or the live Reloaded folder), creating dirs."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(built, dest)
    return dest
