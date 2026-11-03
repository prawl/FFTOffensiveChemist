# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, ported from the FFTLivingWeapons system with the OC id prefix. "Now" holds what
is actively being worked for the current release (hard cap 5, each entry carries Done means +
Verify). "Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this
file only through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The
release ship gate lives in docs/RELEASE_SCOPE.md; Now is the in-flight subset.

## Now (release: 1.2.0)

- **[OC-7] Make a Windows built release zip unpack into the mod folder on Linux** (opened 2026-10-26) [QUEUED]
  - Done means: a Linux player who unzips a release built on the Windows desktop gets a
    prawl.fft.offensivechemist folder, not loose files with backslashes in their names, so
    Reloaded sees the mod; the GitHub CI zip is unaffected today because pwsh writes forward
    slashes. Found live on the TreasureMaster sibling 2026-10-19 and fixed there as TM-9 (commit
    a7ee82b), the same fix ColorCustomizer carries. (Tech: Publish.ps1 uses
    ZipFile.CreateFromDirectory under Windows PowerShell 5.1, which writes backslash separators
    into entry names; write the entries by hand with '/' and make Verify-Package fail on any
    backslash.)
  - Verify: a zip built with .\Publish.ps1 under PowerShell 5.1 lists only forward slash entry
    names and unzips on Linux into the mod folder; a zip with a planted backslash entry makes
    Verify-Package go red; CI green.

## Backlog

- [OC-19] 2026-11-02: Test what the mod ships, not only how its files are written. Today the C#
  tests check only the to-do ledger and the log lines, so nothing fails if the grenade tables come
  out wrong. Run generate.py and compare its XML files to committed golden copies, so a change to
  the output fails the build until the copies are updated on purpose. The per check refusal tests
  for gate.py are dropped: for a finished mod the golden copies catch the break that matters, and
  a refusal test for each check of a gate that is not changing is upkeep. Owner 2026-11-02,
  narrowed to the golden copies. (Tech: golden copies of ItemConsumableData.xml and ItemData.xml;
  run the compare from tools/pipeline.ps1 so CI fails on any difference.)
  - Done means: a change to generate.py's output fails the build until the golden copies are
    updated on purpose.
  - Verify: one hand edit to a generated XML fails the golden test and the revert passes; CI green.

- [OC-20] 2026-11-02: Once OC-19's golden tests land, audit the tests that check markdown and
  source text, and drop any that guard paperwork rather than the mod. Every gate is code to
  maintain, and today every test in this repo is that kind. (Tech: TodoContractTests and
  LogContractTests are the whole C# suite; keep what stops a real mistake and name each test
  dropped and why in the commit.)
- [OC-2] 2026-07-21: Give the mod its real Nexus identity before any Nexus upload. Parked
  2026-11-02 by the owner's quality pause; it was QUEUED in Now.
  - Done means: the release zip is named so Vortex can read the mod's id and version instead of
    showing a warning icon with no version. (Tech: Publish.ps1's NexusModId parameter still
    defaults to the placeholder 0; register the mod on Nexus and bake in the real id.)
  - Verify: a zip built with the real id follows the Nexus filename convention and Vortex shows
    its version after a hand-install; the owner confirms on the first real upload.

- [OC-3] 2026-07-21: The release-zip check only asks "are the named files present", so a
  half-empty zip could still ship; evaluate porting the sibling mods' manifest-driven content
  gate with payload floors. (Tech: floors for the 10 grenade icon .tex files and the two full
  .en.nxd name tables, on top of the current $RequiredModFiles list in tools/pipeline.ps1.)
## Walled (blocked by engine / external)

- Nothing is engine-walled yet; findings blocked by the game engine or external tooling land
  here when they surface.

## Format (enforced by TodoContractTests)

- Sections, in this order and no others: Now (with the release name in the header), Backlog,
  Walled, Format.
- Now: at most 5 entries. Entry first line: `- **[OC-<n>] <title>** (opened YYYY-MM-DD) [STATUS]`
  where STATUS is QUEUED, BUILDING, AWAITING-LIVE, or BLOCKED(reason). Every entry carries a
  `- Done means:` and a `- Verify:` sub-bullet. Promote from Backlog by filling those in; if Now
  is at cap, demote something first.
- Backlog: entry first line `- [OC-<n>] YYYY-MM-DD: <one sentence>`; indented continuation lines
  are free. Capture new items here in the session they surface.
- ELI5-first prose (owner rule, 2026-07-21): the first sentence of every entry, and the opening
  of every Done means / Verify, is plain language a non-programmer follows: what is broken or
  wanted, for whom, what done looks like. Technical detail (file names, script names, ids)
  comes AFTER that opening, in continuation lines or a "(Tech: ...)" tail, never instead of it.
- IDs are unique across this file and docs/CHANGELOG.md; never reuse a retired ID.
- Items exit ONLY by moving to docs/CHANGELOG.md when they ship or die: in the shipping commit
  itself, or in the immediately following commit when the exit row cites that commit's own hash.
- No em dashes and no double-dash separators anywhere in this file or the changelog.
- AWAITING-LIVE resolutions (flipping a row out of AWAITING-LIVE) are owner-only.
