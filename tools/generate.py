#!/usr/bin/env python
"""
Generate the modloader item tables from data/grenades.json (the only hand-edited source).

Emits into the deployable mod tree (mod/FFTIVC/tables/enhanced/), both sparse so load order yields
a clean winner against other item mods (load AFTER them):
  - ItemConsumableData.xml  (the behavior: each grenade row gets Formula 56 = inflict-status,
                             Z = success rate, StatusEffectId = the status to apply)
  - ItemData.xml            (shop timing + price for each grenade, plus Remedy bumped to Chapter 1)

This is the automated, pure-Python half of the pipeline (no FF16Tools, runs on CI). The .en.nxd
NAME tables and the recolored icons are built by the separate FF16Tools steps (patch_names.py,
patch_ability_names.py, recolor_icons.py) and shipped from their committed copies in the mod tree.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.grenades import load_grenades
from lib.paths import MOD_TABLES


def hdr(table):
    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<!-- built from data/grenades.json by tools/generate.py; edits get clobbered. load after other item mods. -->\n'
            f'<{table}>\n  <Version>1</Version>\n  <Entries>\n')


def write_table(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def consumable_entry(g, formula, z):
    return (f"    <ItemConsumable>\n"
            f"      <Id>{g['consumableId']}</Id> <!-- item {g['id']} {g['name']}: inflict {g['status']} (ItemOptions {g['statusEffectId']}) -->\n"
            f"      <Formula>{formula}</Formula>\n"
            f"      <Z>{z}</Z>\n"
            f"      <StatusEffectId>{g['statusEffectId']}</StatusEffectId>\n"
            f"    </ItemConsumable>\n")


def itemdata_entry(iid, shop, price=None, comment=None):
    body = f"      <ShopAvailability>{shop}</ShopAvailability>\n" if shop else ""
    if price:
        body += f"      <Price>{price}</Price>\n"
    tag = f" <!-- {comment} -->" if comment else ""
    return f"    <Item>\n      <Id>{iid}</Id>{tag}\n{body}    </Item>\n"


def main():
    doc = load_grenades()
    grenades = sorted(doc["grenades"], key=lambda g: g["id"])
    meta = doc.get("_meta", {})
    formula, z = meta.get("formula", 56), meta.get("z", 100)
    MOD_TABLES.mkdir(parents=True, exist_ok=True)

    # ItemConsumableData.xml -- the offensive behavior.
    body = "".join(consumable_entry(g, formula, z) for g in grenades)
    write_table(MOD_TABLES / "ItemConsumableData.xml",
                hdr("ItemConsumableTable") + body + "  </Entries>\n</ItemConsumableTable>\n")
    print(f"  wrote ItemConsumableData.xml ({len(grenades)} grenade rows)")

    # ItemData.xml -- shop timing + price (grenades), plus Remedy's early-buy bump.
    rows = "".join(itemdata_entry(g["id"], g["shop"], g.get("price"),
                                  f"{g['name']} ({g['status']}) -- {g.get('shopNote', '')}".strip(" -"))
                   for g in grenades)
    remedy = doc.get("remedy")
    if remedy:
        rows += itemdata_entry(remedy["id"], remedy.get("shop"), None,
                               "Remedy: now the only single cure, buyable in Chapter 1")
    write_table(MOD_TABLES / "ItemData.xml",
                hdr("ItemTable") + rows + "  </Entries>\n</ItemTable>\n")
    n_extra = 1 if remedy else 0
    print(f"  wrote ItemData.xml ({len(grenades)} grenade shop rows + {n_extra} Remedy override)")


if __name__ == "__main__":
    main()
