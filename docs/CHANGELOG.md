# Changelog (work-ledger exits)

STATUS: CONTRACT (machine-checked by TodoContractTests)

Where docs/TODO.md items land when they ship, die, or retract; newest first within a cycle.
Entry first line: `- [OC-<n>] SHIPPED <hash> YYYY-MM-DD: <summary>`, or WONTFIX / RETRACTED
with a date and no hash.

## 1.2.0 cycle

- [OC-6] WONTFIX 2026-10-16: A player reported the game crashing when entering a battle from the
  overworld after the September game update that removed Denuvo, and asked for a mod update. The
  crash was the mod loader's, not this mod's: Nenkai's fftivc.utility.modloader 1.7.3 (2026-09-20)
  added support for the Denuvo free exe but fetched the ItemConsumableData table wrongly, and
  1.7.4 (2026-09-29, the day after the report) fixed exactly that. Offensive Chemist is the one
  mod here that edits ItemConsumableData, so it was the visible victim. On the owner's box with
  loader 1.7.5 and game buildid 24304444, two battles entered from the world map with this mod
  loaded were crash free and every one of its 19 table cells was applied (Reloaded logs
  2026-10-16 03:58 and 04:42). No change to this mod; players update the loader, which Reloaded
  does automatically.

- [OC-4] SHIPPED f83f9d5 2026-07-21: the build scripts now speak with one shared voice, so
  every line says which stage is talking and a failure reads the same as in the sibling
  mods; the runtime logger and flight recorder are recorded WONTFIX because this data-only
  mod has no code running in the game to log. (Tech: tools/lib/say.py with the closed
  8-verb set, Write-OcSay in tools/pipeline.ps1, docs/LOGGING.md pinned to the code by the
  new LogContractTests inside the existing test gate; proven non-vacuous by a deliberate
  sabotage going red, then full BuildLinked and Publish runs printing only tagged lines.)
- [OC-1] SHIPPED b0042ce 2026-07-21: the repo now tracks its work the same way the sibling
  mods do, in one machine-checked ledger, so planned work stops living in chat logs and a
  malformed ledger refuses to deploy or package. (Tech: docs/TODO.md + docs/CHANGELOG.md +
  docs/RELEASE_SCOPE.md under the 35 TodoContractTests in the new FFTOffensiveChemist.Tests
  project, run as a hard gate by BuildLinked.ps1, Publish.ps1, and CI; proven non-vacuous by
  two deliberate sabotages going red.)

## Pre-ledger history (backfilled)

- [OC-0] SHIPPED 07f50f3 2026-06-21: version 1.1.0 keeps curing affordable while the five
  single-cure items become grenades: Remedy, the cure-all item, now appears in shops from
  Chapter 1 and its Chemist learn cost drops from 700 JP to 150 JP, so players are never
  priced out of curing. (Tech: the remedy block in data/grenades.json; the JP cost is
  restamped by tools/patch_ability_names.py on ability Key 380; the follow-up gate
  hardening landed in 19cb2d4.)
