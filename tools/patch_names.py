#!/usr/bin/env python
"""
Build item.en.nxd: rename the 5 recycled cure items (ids 246-250) into the grenades.

Full-table round-trip from the PRISTINE vanilla item.en decode: copy it, rewrite ONLY the 5
grenade rows (Name / NameSingular / NamePlural / Name2 / Description), re-encode the whole nxd,
then VERIFY the build by decoding it back and asserting that exactly those rows' name/description
cells differ from vanilla. A red verify refuses to deploy -- the modloader merges nxd tables
cell-level, so any unintended cell we shipped would silently override vanilla for every player.

Needs FF16Tools + the pristine decode at working/item.en.sqlite (see README "Pristine caches").

Usage:
  python tools/patch_names.py          # build + verify + deploy into the mod tree
  python tools/patch_names.py --dry    # print the planned renames, no writes
"""
import shutil
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.grenades import load_grenades, plural
from lib.nxd import encode_sqlite_to_nxd, decode_nxd_to_sqlite, deploy_nxd
from lib.paths import ROOT, PRISTINE_ITEM_SQLITE, MOD_ITEM_NXD

BUILD = ROOT / "working" / "nxd_out" / "item_build.sqlite"
ENC_DIR = ROOT / "working" / "nxd_out"
VERIFY_SQLITE = ROOT / "working" / "nxd_out" / "item_verify.sqlite"

NAME_COLS = ("Name", "NameSingular", "NamePlural", "Name2", "Description")


def planned():
    """item Key -> {col: value} for the 5 grenade rows."""
    out = {}
    for g in load_grenades()["grenades"]:
        out[g["id"]] = {
            "Name": g["name"],
            "NameSingular": g["name"].lower(),
            "NamePlural": plural(g["name"]),
            "Name2": g["name"],
            "Description": g["itemDesc"],
        }
    return out


def apply_patches(db, patches):
    con = sqlite3.connect(db)
    for key, cols in patches.items():
        sets = ", ".join(f'"{c}" = ?' for c in cols)
        con.execute(f'UPDATE "Item-en" SET {sets} WHERE Key = ?', [*cols.values(), key])
        if con.execute("SELECT changes()").fetchone()[0] != 1:
            sys.exit(f"FAIL: item Key {key} did not update exactly one row (is working/item.en.sqlite the vanilla decode?)")
    con.commit()
    con.close()


def rows(db):
    con = sqlite3.connect(db)
    cols = [r[1] for r in con.execute('PRAGMA table_info("Item-en")')]
    data = {r[0]: dict(zip(cols, r)) for r in con.execute('SELECT * FROM "Item-en"')}
    con.close()
    return data


def verify(built_nxd, patches):
    decode_nxd_to_sqlite(built_nxd, VERIFY_SQLITE)
    vanilla, rebuilt = rows(PRISTINE_ITEM_SQLITE), rows(VERIFY_SQLITE)
    if set(vanilla) != set(rebuilt):
        sys.exit(f"FAIL: row-key sets differ (vanilla {len(vanilla)} vs rebuilt {len(rebuilt)})")
    unexpected = []
    for key, vrow in vanilla.items():
        for col, vval in vrow.items():
            nval = rebuilt[key][col]
            if nval == vval:
                continue
            if col in patches.get(key, {}) and nval == patches[key][col]:
                continue
            unexpected.append((key, col, vval, nval))
    if unexpected:
        for key, col, vval, nval in unexpected[:20]:
            print(f"  UNEXPECTED diff Key {key} {col}: {vval!r} -> {nval!r}")
        sys.exit(f"FAIL: {len(unexpected)} unexpected cell diffs -- refusing to deploy")
    for key, cols in patches.items():
        for col, val in cols.items():
            if rebuilt[key][col] != val:
                sys.exit(f"FAIL: Key {key} {col} did not land in the rebuilt table")
    print(f"  verify PASS: only the intended {sum(len(c) for c in patches.values())} cells differ from vanilla")


def main():
    patches = planned()
    for key, cols in sorted(patches.items()):
        print(f"id{key}: {cols['Name']!r} -- {cols['Description']!r}")
    if "--dry" in sys.argv:
        return
    if not PRISTINE_ITEM_SQLITE.exists():
        sys.exit(f"FAIL: pristine vanilla decode missing at {PRISTINE_ITEM_SQLITE} (see README 'Pristine caches')")
    ENC_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(PRISTINE_ITEM_SQLITE, BUILD)
    apply_patches(BUILD, patches)
    out_nxd = encode_sqlite_to_nxd(BUILD, ENC_DIR, "item.en.nxd")
    verify(out_nxd, patches)
    deploy_nxd(out_nxd, MOD_ITEM_NXD)
    print(f"deployed -> {MOD_ITEM_NXD} ({out_nxd.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
