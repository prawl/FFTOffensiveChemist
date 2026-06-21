#!/usr/bin/env python
"""
Build ability.en.nxd: rename the 5 Chemist Item-command USE-abilities (Keys 374-378) to match
the grenades (so the ability-learn menu shows "Venom Flask" instead of "Antidote"), and -- when
grenades.json sets remedy.jpCost -- restamp Remedy's learn cost (Key 380 = item id 252 + 128).

The Chemist's learn menu shows the item-USE ability names, which live in the Ability-en table
(ability.en.nxd) -- a SEPARATE table from the item names (item.en.nxd, built by patch_names.py).
Keys 374-378 are the use-abilities for items 246-250. The SAME table holds each ability's JP learn
cost as a 16-bit value split across two byte columns (JpCost1 low + 256*JpCost2 high; vanilla
Remedy = 188 + 512 = 700), so Remedy's JP override is just two more cells in this one file.

Same self-verifying full-table round-trip as patch_names.py: decode the PRISTINE vanilla
ability.en.nxd, rewrite ONLY the 5 grenade rows (Name + Description) plus Remedy's JpCost cells,
re-encode, then decode the build back and assert exactly those cells differ from vanilla. The modloader merges nxd tables
cell-level, so a vanilla-faithful rebuild with only our rows changed coexists with other installed
ability.en.nxd mods. A red verify refuses to deploy.

Needs FF16Tools + the pristine vanilla nxd at working/nxd_ability/ability.en.nxd (see README).

Usage:
  python tools/patch_ability_names.py          # build + verify + deploy into the mod tree
  python tools/patch_ability_names.py --dry    # print the planned renames, no writes
"""
import shutil
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.grenades import load_grenades
from lib.nxd import encode_sqlite_to_nxd, decode_nxd_to_sqlite, deploy_nxd, extract_from_pac
from lib.paths import ROOT, PRISTINE_ABILITY_NXD, MOD_ABILITY_NXD, VANILLA_EN_PAC, VANILLA_PAC_DIR

PRISTINE_SQLITE = ROOT / "working" / "nxd_out_ability" / "ability_pristine.sqlite"
BUILD = ROOT / "working" / "nxd_out_ability" / "ability_build.sqlite"
ENC_DIR = ROOT / "working" / "nxd_out_ability"
VERIFY_SQLITE = ROOT / "working" / "nxd_out_ability" / "ability_verify.sqlite"


def planned():
    """ability Key -> {col: value}: the 5 grenade use-abilities (Name + Description), plus -- when
    grenades.json sets remedy.jpCost -- Remedy's learn cost split into its two byte columns
    (JpCost1 = low byte, JpCost2 = high byte; e.g. 150 -> JpCost1 150, JpCost2 0)."""
    doc = load_grenades()
    patches = {g["abilityKey"]: {"Name": g["name"], "Description": g["abilityDesc"]}
               for g in doc["grenades"]}
    remedy = doc.get("remedy")
    if remedy and remedy.get("jpCost") is not None:
        jp = remedy["jpCost"]
        patches[remedy["abilityKey"]] = {"JpCost1": jp & 0xFF, "JpCost2": (jp >> 8) & 0xFF}
    return patches


def refresh_pristine():
    """Extract the pristine vanilla ability table STRAIGHT FROM the game pac to PRISTINE_ABILITY_NXD.

    Same reason as patch_names.py: the verify only proves "rebuilt == pristine + the 5 grenade
    rows", so the baseline MUST be true vanilla. A hand-placed working/ copy from a modded install
    silently poisons every other ability name (the modloader merges nxd cell-level). Re-deriving
    from the encrypted base pac on every build removes that footgun."""
    if not VANILLA_EN_PAC.exists():
        sys.exit(f"FAIL: vanilla pac missing at {VANILLA_EN_PAC} -- need the game installed "
                 f"(or point FFT_VANILLA_EN_PAC at 0004.en.pac). The nxd build will not trust a "
                 f"hand-placed working/ cache as the vanilla baseline.")
    extract_from_pac(VANILLA_EN_PAC, "nxd/ability.en.nxd", VANILLA_PAC_DIR)  # -> PRISTINE_ABILITY_NXD
    print(f"  pristine baseline refreshed from {VANILLA_EN_PAC.name} -> {PRISTINE_ABILITY_NXD.name}")


def apply_patches(db, patches):
    con = sqlite3.connect(db)
    for key, cols in patches.items():
        sets = ", ".join(f'"{c}" = ?' for c in cols)
        con.execute(f'UPDATE "Ability-en" SET {sets} WHERE Key = ?', [*cols.values(), key])
        if con.execute("SELECT changes()").fetchone()[0] != 1:
            sys.exit(f"FAIL: ability Key {key} did not update exactly one row")
    con.commit()
    con.close()


def rows(db):
    con = sqlite3.connect(db)
    cols = [r[1] for r in con.execute('PRAGMA table_info("Ability-en")')]
    data = {r[0]: dict(zip(cols, r)) for r in con.execute('SELECT * FROM "Ability-en"')}
    con.close()
    return data


def verify(built_nxd, patches):
    decode_nxd_to_sqlite(built_nxd, VERIFY_SQLITE)
    vanilla, rebuilt = rows(PRISTINE_SQLITE), rows(VERIFY_SQLITE)
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
        print(f"Key {key}: " + ", ".join(f"{c}={v!r}" for c, v in cols.items()))
    if "--dry" in sys.argv:
        return
    ENC_DIR.mkdir(parents=True, exist_ok=True)
    refresh_pristine()
    decode_nxd_to_sqlite(PRISTINE_ABILITY_NXD, PRISTINE_SQLITE)
    shutil.copy(PRISTINE_SQLITE, BUILD)
    apply_patches(BUILD, patches)
    out_nxd = encode_sqlite_to_nxd(BUILD, ENC_DIR, "ability.en.nxd")
    verify(out_nxd, patches)
    deploy_nxd(out_nxd, MOD_ABILITY_NXD)
    print(f"deployed -> {MOD_ABILITY_NXD} ({out_nxd.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
