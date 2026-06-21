# Design

## Thesis

The Chemist's Item command is a delivery system with almost nothing worth delivering. By the
time you can field one, Remedy cures every status the five single-cures (Antidote, Eye Drops,
Echo Herbs, Maiden's Kiss, Gold Needle) handle individually -- so those five items are dead
inventory the moment Remedy shows up.

This mod recycles that dead inventory into **offensive** consumables. Curing capability is
unchanged (Remedy still covers everything), but the Chemist gains a reason to throw things: a
spread of guaranteed status grenades that scale in disruption and cost across the chapters.

## The grenades

Each grenade is a guaranteed (`Z 100`) single-target status throw via the consumable
status-infliction formula (`Formula 56`). The status spread is chosen so each grenade answers a
different problem and earns its slot:

| Grenade | Status | Why it earns a throw |
|---------|--------|----------------------|
| Venom Flask | Poison  | Early, spammable chip damage; closes out wounded targets. |
| Smoke Bomb  | Blind   | Early; neuters a physical attacker's accuracy without killing it. |
| Oil Flask   | Oil     | Setup: doubles the Fire damage the target takes -- pays off with a mage or a Fire weapon. |
| Hush Vial   | Silence | A *guaranteed* Silence, where the spell version lands ~65% of the time. |
| Sludge Bomb | Slow    | Steals turns outright; the premium late-game disruptor. |

### Pricing + availability

Prices scale with disruption power and chapter wealth, and are kept cheap enough that you
actually throw them -- a hoarded consumable is a dead consumable.

- **Venom Flask / Smoke Bomb** -- Chapter 1, 100 / 150 g. Cheap chip and accuracy denial from
  the start.
- **Oil Flask** -- Chapter 2, 250 g. A combo enabler; worthless alone, strong with Fire.
- **Hush Vial** -- Chapter 3, 500 g. A guaranteed answer to enemy casters, priced above the
  unreliable spell.
- **Sludge Bomb** -- Chapter 4, 800 g. Turn theft is the strongest effect, gated latest and
  priced highest.

### Remedy moves up

Repurposing the five single-cures removes early single-status healing. Remedy already cures every
one of those statuses, so two adjustments keep early curing whole:

- **Availability** -- the Remedy *item* is bumped to **Chapter 1** (vanilla gates it to Chapter 2,
  around Lionel Castle), so it is buyable from the start.
- **Learn cost** -- the Chemist learns each Item consumable as its own JP ability, and vanilla
  Remedy costs **700 JP**: the single priciest cure, versus the **70 / 80 / 120 / 200 / 250 JP**
  the five single-cures it replaces cost individually. Collapsing five cheap on-demand cures into
  one 700 JP gate is a real early-game tax, so Remedy's learn cost drops to **150 JP** -- about
  twice the old Antidote, still under the old top single-cure.

Curing is consolidated and re-priced to stay reachable, not made more expensive. (The 350 gil shop
price is already cheap and is left untouched -- the cost that bit was JP, not gil.)

## Why data-only

Everything here is achievable with vanilla engine behavior:

- The Chemist already throws consumables with the Item command. Repointing five existing
  consumable rows to inflict a status (instead of cure one) changes what they *do* with no code.
- The status-infliction formula (`Formula 56`) and the per-status ids are vanilla engine
  features; the mod only fills in table cells.

So there is no DLL and no in-process code -- just four merged table edits and ten recolored
icons. This keeps the mod tiny, restart-only, and trivially compatible with anything that
isn't also editing those exact rows.

## Compatibility

Load **after** other item mods so the five grenade rows win. The `.en.nxd` name tables are
built vanilla-faithful (only the five grenade rows differ from stock), and the modloader merges
nxd tables cell-level, so this mod coexists with other `item.en.nxd` / `ability.en.nxd` mods
unless one of them also edits items 246-250 or abilities 374-378.
