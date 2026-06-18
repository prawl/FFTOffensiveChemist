#!/usr/bin/env python
"""
Recolor the 5 grenade menu icons from the vanilla originals to per-grenade tints.

Pipeline per item (both the 100x100 full icon and the 48x48 small icon):
  vanilla BC7 .tex (Pac Files/0008) -> FF16Tools tex-conv -> DDS -> Pillow recolor
  (HSV: fix hue + saturation, scale value to preserve shading) -> img-conv --no-chunk-compression
  -> .tex placed in the mod tree.

Tints + source shapes come from data/grenades.json (iconTint = [hue, sat, value_mult] in 0..1
with value a brightness multiplier; iconSource = the vanilla icon id to borrow the shape from,
or null to keep the item's own). Needs FF16Tools + the decrypted vanilla icon dump.

Run: python tools/recolor_icons.py            # all 5
     python tools/recolor_icons.py 246 250     # only the listed ids
"""
import subprocess, shutil, colorsys, sys
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.grenades import load_grenades
from lib.paths import ROOT, FF16, VANILLA_ICONS, MOD_ICON_DIR

WORK = ROOT / "working" / "icons"


def recolor(im, hue, sat, val_mult):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 8:
                continue
            _, _, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            nr, ng, nb = colorsys.hsv_to_rgb(hue, sat, min(1.0, v * val_mult))
            px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return im


def process(item_id, hue, sat, val_mult, src_id=None):
    WORK.mkdir(parents=True, exist_ok=True)
    sid = item_id if src_id is None else src_id
    for sub, pfx in [("equip_item", "ei"), ("equip_item_s", "ei_s")]:
        src_name = f"{pfx}_{sid:03d}_uitx"
        out_name = f"{pfx}_{item_id:03d}_uitx"
        src = VANILLA_ICONS / sub / "texture" / f"{src_name}.tex"
        if not src.exists():
            print(f"  MISSING {src}"); continue
        work_tex = WORK / f"{src_name}.tex"
        shutil.copy(src, work_tex)
        subprocess.run([str(FF16), "tex-conv", "-i", str(work_tex)], capture_output=True)
        im = Image.open(WORK / f"{src_name}.dds").convert("RGBA")
        recolor(im, hue, sat, val_mult)
        png = WORK / f"{out_name}.png"
        im.save(png)
        work_tex.unlink(missing_ok=True)
        subprocess.run([str(FF16), "img-conv", "-i", str(png), "--no-chunk-compression"], capture_output=True)
        dst = MOD_ICON_DIR / sub / "texture"
        dst.mkdir(parents=True, exist_ok=True)
        shutil.move(str(WORK / f"{out_name}.tex"), str(dst / f"{out_name}.tex"))
        print(f"  {out_name}" + (f" (from {src_name})" if src_id is not None else "") + f" -> {sub}")


def main():
    only = set(int(a) for a in sys.argv[1:] if a.isdigit())
    for g in load_grenades()["grenades"]:
        if only and g["id"] not in only:
            continue
        h, s, v = g["iconTint"]
        print(f"id{g['id']} ({g['name']}):")
        process(g["id"], h, s, v, g.get("iconSource"))
    print("Done. Recolored icons placed in the mod tree.")


if __name__ == "__main__":
    main()
