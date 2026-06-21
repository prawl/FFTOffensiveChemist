# FFT Offensive Chemist

A Reloaded-II mod for **Final Fantasy Tactics: The Ivalice Chronicles** (`fft_enhanced.exe`),
shipped as the Reloaded mod id `prawl.fft.offensivechemist`. It loads on Nenkai's
[`fftivc.utility.modloader`](https://github.com/Nenkai/fftivc.utility.modloader).

## What it does

Vanilla has five single-status cure items that Remedy already makes redundant -- Antidote,
Eye Drops, Echo Herbs, Maiden's Kiss, and Gold Needle. This mod recycles those five into
**offensive status grenades** the Chemist throws with the **Item** command:

| Item id | Grenade | Inflicts | Shop | Price |
|--------:|---------|----------|------|------:|
| 246 | **Venom Flask** | Poison  | Chapter 1 | 100 |
| 247 | **Smoke Bomb**  | Blind   | Chapter 1 | 150 |
| 249 | **Oil Flask**   | Oil (doubles Fire damage taken) | Chapter 2 | 250 |
| 248 | **Hush Vial**   | Silence | Chapter 3 | 500 |
| 250 | **Sludge Bomb** | Slow    | Chapter 4 | 800 |

Each grenade is a guaranteed (100%) single-target status throw. Because the five cures are
gone, **Remedy** (which already cures every status) is bumped to **Chapter 1** *and* its Chemist
learn cost is cut from **700 JP to 150 JP**, so early status-healing stays reachable without a
brutal JP gate -- vanilla locked all five replaced cures (70-250 JP each) behind one 700 JP
ability, the single priciest cure on the Chemist's list.

This is a **data-only** mod -- no DLL, no in-process code. The Chemist throws the grenades
through the vanilla engine's Item command; the mod just repoints what those five item ids do,
renames them, renames the matching learn-menu abilities, and recolors their icons.

## How it works (the data layers)

The five grenades touch four game tables, all derived from one source:

1. **`ItemConsumableData.xml`** -- the behavior. Each grenade's ItemConsumable row gets
   `Formula 56` (inflict-status-on-target), `Z 100` (success rate out of 100), and a
   `StatusEffectId` (the status to apply). Sparse override; the modloader merges it onto
   vanilla.
2. **`ItemData.xml`** -- shop availability + price for each grenade, plus Remedy's Chapter 1
   bump.
3. **`item.en.nxd`** -- renames items 246-250 (name + description) so the menu reads
   "Venom Flask", not "Antidote". Full-table file; only those five rows differ from vanilla.
4. **`ability.en.nxd`** -- renames the Chemist's Item-command use-abilities (Keys 374-378) so
   the ability-learn menu matches, and restamps **Remedy**'s learn cost (Key 380) from 700 JP to
   150 JP (JP is a 16-bit value stored as `JpCost1` + 256*`JpCost2` in this same table -- so, like
   the names, the cut applies to English installs). Full-table file; only those six rows differ
   from vanilla.

Plus 10 recolored menu icons (a 100x100 + a 48x48 per grenade) under
`mod/FFTIVC/data/enhanced/ui/ffto/icon/`.

## Architecture: single source of truth -> generated outputs

**`data/grenades.json` is the only hand-edited source.** Never hand-edit the XML tables, the
`.en.nxd` files, or the icons -- they are regenerated and your edits get clobbered.

```
data/grenades.json ──gate.py──────────────▶ THE GATE: ids/keys consistent, statuses sane, ASCII text
       │           ──generate.py───────────▶ mod/FFTIVC/tables/enhanced/ItemConsumableData.xml + ItemData.xml
       │           ──patch_names.py─────────▶ mod/FFTIVC/data/enhanced/nxd/item.en.nxd      (self-verifying)
       │           ──patch_ability_names.py─▶ mod/FFTIVC/data/enhanced/nxd/ability.en.nxd   (self-verifying)
       └───────────  recolor_icons.py───────▶ mod/FFTIVC/data/enhanced/ui/ffto/icon/*.tex
```

The two `.en.nxd` builders are **self-verifying**: each rebuilds the whole table from the
pristine vanilla decode, changes only the grenade rows (plus Remedy's JP cells in the ability
table), re-encodes, then decodes the result back and asserts that *only* those cells differ
from vanilla. A red verify
refuses to deploy -- the modloader merges nxd tables cell-level, so any stray cell would
silently override vanilla for every player.

That guarantee is only as good as the baseline, so the builders **re-derive the pristine
vanilla tables straight from the game's base pac** (`data/enhanced/0004.en.pac`) on every run --
they never trust a hand-placed `working/` cache. (An earlier release shipped with the baseline
accidentally decoded from a *modded* install, which silently renamed ~11 unrelated weapons/armor,
e.g. Longsword showing as "Chaosbringer". Sourcing from the encrypted base pac removes that
footgun.)

## Commands

Environment note: use `python` (not `python3`). PowerShell scripts.

```powershell
python tools\gate.py                  # THE GATE: validate data/grenades.json (exit 1 on any violation)
python tools\generate.py              # grenades.json -> the two table XMLs
python tools\patch_names.py           # grenades.json -> item.en.nxd     (FF16Tools; self-verify)
python tools\patch_ability_names.py   # grenades.json -> ability.en.nxd  (FF16Tools; self-verify)
python tools\recolor_icons.py         # grenades.json -> recolored icons (FF16Tools + vanilla icon dump)

.\BuildLinked.ps1   # gate + generate, then deploy the mod tree into the live Reloaded Mods folder
.\Publish.ps1       # gate + generate, then stage + zip the release package
```

`BuildLinked.ps1` (local dev, deploys into the live Mods folder) and `Publish.ps1` (release
zip) are the two halves of the pipeline; their shared prefix (gate -> generate, plus the
required-file manifest) lives in `tools/pipeline.ps1` (dot-sourced by both) so the copies
cannot drift. Both are pure-Python and run on CI.

The game is **data-only at the table level**: table/nxd/icon changes take effect on game
**restart**, not live.

### Rebuilding the name tables + icons

`BuildLinked.ps1` / `Publish.ps1` regenerate the two table XMLs and ship the committed
`item.en.nxd` / `ability.en.nxd` / icons as-is (the nxd build needs FF16Tools and is kept a
manual step, same split the sibling FFT mods use). **When you edit a grenade's name,
description, or icon in `grenades.json`, re-run the matching FF16Tools step and commit the
result:**

```powershell
python tools\patch_names.py           # after any name/itemDesc change
python tools\patch_ability_names.py   # after any name/abilityDesc or remedy.jpCost change
python tools\recolor_icons.py         # after any iconTint/iconSource change
```

(Status / shop / price changes are picked up automatically by `generate.py` -- no nxd rebuild
needed.)

### Pristine caches

The two `.en.nxd` builders diff their output against the **vanilla** decode, which they re-derive
from the game's base localized pac on every run -- **do not hand-populate the baseline.** Both
`item.en.nxd` and `ability.en.nxd` live inside `data/enhanced/0004.en.pac`; `refresh_pristine()`
in each builder extracts them with FF16Tools (`-g fft`) into `working/vanilla_pac/` and decodes
the item table to `working/item.en.sqlite`. All of that is gitignored and regenerated, so there
is nothing to copy between checkouts.

This matters: a hand-placed cache decoded from a *modded* install (easy on a box that runs other
item mods) silently poisons every other row of the shipped name table, since the modloader merges
nxd cell-level. Sourcing the baseline from the encrypted base pac makes that impossible. The
builders need the game installed; point `FFT_VANILLA_EN_PAC` at `0004.en.pac` for a non-default
install. The pure-Python gate + generate + the committed mod tree do **not** need the pac, so a
clean clone still builds and packages the tables.

## Requirements

- **Players:** [`fftivc.utility.modloader`](https://github.com/Nenkai/fftivc.utility.modloader)
  (declared as a dependency; Reloaded fetches it). Load this mod *after* any other item mod so
  its table rows win.
- **Building the nxds/icons:** [FF16Tools](https://github.com/Nenkai/FF16Tools) CLI (point
  `FF16TOOLS_CLI` at it, or edit `tools/lib/paths.py`) + Pillow (`pip install pillow`) for the
  icon recolor.

## Data-layer gotchas

- **Formula/effect ids in the XML are DECIMAL.** Every FFT reference lists them in hex; always
  hex->dec convert. `<Formula>56</Formula>` is decimal 56 (inflict status).
- **`StatusEffectId` is the ItemOptions status id (decimal):** 22 = Poison, 9 = Blind,
  10 = Silence, 101 = Oil, 18 = Slow.
- **NXD overrides are full-table files** but the modloader merges them cell-level, so shipping a
  vanilla-faithful table with only the grenade rows (and Remedy's JP cells) changed coexists with
  other installed `item.en.nxd` / `ability.en.nxd` mods.

See `docs/DESIGN.md` for the design rationale.
