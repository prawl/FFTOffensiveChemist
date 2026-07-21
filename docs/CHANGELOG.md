# Changelog (work-ledger exits)

STATUS: CONTRACT (machine-checked by TodoContractTests)

Where docs/TODO.md items land when they ship, die, or retract; newest first within a cycle.
Entry first line: `- [OC-<n>] SHIPPED <hash> YYYY-MM-DD: <summary>`, or WONTFIX / RETRACTED
with a date and no hash.

## Pre-ledger history (backfilled)

- [OC-0] SHIPPED 07f50f3 2026-06-21: version 1.1.0 keeps curing affordable while the five
  single-cure items become grenades: Remedy, the cure-all item, now appears in shops from
  Chapter 1 and its Chemist learn cost drops from 700 JP to 150 JP, so players are never
  priced out of curing. (Tech: the remedy block in data/grenades.json; the JP cost is
  restamped by tools/patch_ability_names.py on ability Key 380; the follow-up gate
  hardening landed in 19cb2d4.)
