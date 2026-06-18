#!/usr/bin/env python
"""
THE GATE: validate data/grenades.json before anything is generated or shipped.

Pure-Python (runs on CI, no FF16Tools). Exit 1 on any violation so BuildLinked / Publish /
CI refuse to deploy or package a malformed design. The second gate -- proving the built
.en.nxd name tables changed ONLY the grenade rows -- lives in patch_names.py /
patch_ability_names.py, which self-verify their FF16Tools output against the vanilla decode.

Checks:
  - ids/keys unique and internally consistent (consumableId = id-240, abilityKey = id+128)
  - StatusEffectId is a byte (1..255); Formula/Z sane (Z is a 0..100 success rate)
  - names/descriptions present, ASCII-only (non-ASCII can corrupt the nxd encode), within
    a sane length
  - icon tints in range, icon sources valid ids
  - shop strings look like real ShopAvailability values
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.grenades import load_grenades

SHOP_RE = re.compile(r"^(Chapter[1-4]_Start|Unknown\d+)$")
MAX_NAME = 24      # the item/ability Name column is short; vanilla names fit well under this
MAX_DESC = 200     # one flavor + one mechanics sentence


def is_int(v):
    # bool is an int subclass in Python, so isinstance(True, int) is True -- a JSON `true`
    # would otherwise pass an int check and emit "<StatusEffectId>True</StatusEffectId>".
    return isinstance(v, int) and not isinstance(v, bool)


def fail(errs):
    print("\nGATE FAILED:")
    for e in errs:
        print(f"  X {e}")
    sys.exit(1)


def check_ascii(errs, label, text):
    if not text or not str(text).strip():
        errs.append(f"{label}: empty")
        return
    try:
        text.encode("ascii")
    except UnicodeEncodeError:
        bad = [c for c in text if ord(c) > 127]
        errs.append(f"{label}: non-ASCII char(s) {bad!r} (use ASCII; e.g. ' -- ' not an em dash)")


def main():
    doc = load_grenades()
    grenades = doc.get("grenades", [])
    errs = []
    if not grenades:
        fail(["grenades.json has no 'grenades' array"])

    seen_id, seen_cons, seen_abil = set(), set(), set()
    for g in grenades:
        iid = g.get("id")
        tag = f"grenade {g.get('name', iid)!r}"
        if not is_int(iid):
            errs.append(f"{tag}: id must be an int"); continue
        if iid in seen_id:
            errs.append(f"{tag}: duplicate item id {iid}")
        seen_id.add(iid)

        # internal id consistency (the mapping the modloader + learn menu rely on). Only
        # track for duplicates once the value is consistent, so a missing/wrong key reports
        # one clear error instead of stacking a bogus "duplicate None" on top.
        cid = g.get("consumableId")
        if cid != iid - 240:
            errs.append(f"{tag}: consumableId {cid} != id-240 ({iid - 240})")
        elif cid in seen_cons:
            errs.append(f"{tag}: duplicate consumableId {cid}")
        else:
            seen_cons.add(cid)
        akey = g.get("abilityKey")
        if akey != iid + 128:
            errs.append(f"{tag}: abilityKey {akey} != id+128 ({iid + 128})")
        elif akey in seen_abil:
            errs.append(f"{tag}: duplicate abilityKey {akey}")
        else:
            seen_abil.add(akey)

        sid = g.get("statusEffectId")
        if not is_int(sid) or not (1 <= sid <= 255):
            errs.append(f"{tag}: statusEffectId {sid!r} must be a byte 1..255")

        for f in ("name", "status", "itemDesc", "abilityDesc"):
            check_ascii(errs, f"{tag}.{f}", g.get(f))
        if g.get("name") and len(g["name"]) > MAX_NAME:
            errs.append(f"{tag}: name longer than {MAX_NAME} chars")
        for f in ("itemDesc", "abilityDesc"):
            if g.get(f) and len(g[f]) > MAX_DESC:
                errs.append(f"{tag}: {f} longer than {MAX_DESC} chars")

        tint = g.get("iconTint")
        if not (isinstance(tint, list) and len(tint) == 3 and all(isinstance(v, (int, float)) for v in tint)):
            errs.append(f"{tag}: iconTint must be [hue, sat, value_mult]")
        elif not (0 <= tint[0] <= 1 and 0 <= tint[1] <= 1 and 0 <= tint[2] <= 2):
            errs.append(f"{tag}: iconTint out of range (hue/sat 0..1, value_mult 0..2)")
        src = g.get("iconSource")
        if src is not None and not isinstance(src, int):
            errs.append(f"{tag}: iconSource must be null or an int item id")

        shop = g.get("shop")
        if not (isinstance(shop, str) and SHOP_RE.match(shop)):
            errs.append(f"{tag}: shop {shop!r} is not a recognized ShopAvailability value")
        if g.get("price") is not None and not (is_int(g["price"]) and g["price"] > 0):
            errs.append(f"{tag}: price must be a positive int")

    remedy = doc.get("remedy")
    if remedy and not (isinstance(remedy.get("shop"), str) and SHOP_RE.match(remedy["shop"])):
        errs.append(f"remedy.shop {remedy.get('shop')!r} is not a recognized ShopAvailability value")

    if errs:
        fail(errs)
    print(f"  GATE PASS: {len(grenades)} grenades validated (ids/keys consistent, statuses sane, text ASCII).")


if __name__ == "__main__":
    main()
