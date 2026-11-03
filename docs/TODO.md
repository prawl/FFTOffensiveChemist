# TODO

STATUS: CONTRACT (machine-checked by TodoContractTests; format grammar at the bottom of this file)

The work ledger, ported from the FFTLivingWeapons system with the OC id prefix. "Now" holds what
is actively being worked for the current release (hard cap 5, each entry carries Done means +
Verify). "Backlog" captures everything else at the cheapest possible entry cost. Items EXIT this
file only through docs/CHANGELOG.md, moved there in the commit that ships or kills them. The
release ship gate lives in docs/RELEASE_SCOPE.md; Now is the in-flight subset.

## Now (release: 1.2.0)

- **[OC-18] Take the shared rulebook so this mod builds under the same rules as the others** (opened 2026-11-02) [QUEUED]
  - Done means: the mod carries gates/ as a subtree with its rules.json, compiles the shared logger
    and tests in, imports the shared build settings and style file, and every gate runs green
    locally and in CI with today's numbers recorded as the floor. No gameplay code changes. (Tech:
    the hookup steps in gates/README.md; rules.json names prod, tests, projects and the OC prefix;
    floor.json and the comment budget baseline come from today's files.)
  - Verify: BuildLinked.ps1 and CI green on the hookup commit; the health numbers equal what the
    repo's own copy printed before the swap; the build log names the rulebook version.

## Backlog

- [OC-2] 2026-07-21: Give the mod its real Nexus identity before any Nexus upload. Parked 2026-11-02 by the owner's quality pause; it was QUEUED in Now.
  - Done means: the release zip is named so Vortex can read the mod's id and version instead of
    showing a warning icon with no version. (Tech: Publish.ps1's NexusModId parameter still
    defaults to the placeholder 0; register the mod on Nexus and bake in the real id.)
  - Verify: a zip built with the real id follows the Nexus filename convention and Vortex shows
    its version after a hand-install; the owner confirms on the first real upload.

- [OC-3] 2026-07-21: The release-zip check only asks "are the named files present", so a
  half-empty zip could still ship; evaluate porting the sibling mods' manifest-driven content
  gate with payload floors. (Tech: floors for the 10 grenade icon .tex files and the two full
  .en.nxd name tables, on top of the current $RequiredModFiles list in tools/pipeline.ps1.)
- [OC-5] 2026-07-21: A ledger row accidentally pasted after the Format section escapes every
  grammar and id-uniqueness scan, because the contract tests only read entries out of the
  Now, Backlog, and changelog sections; decide whether entry-shaped lines in Walled or
  Format should fail the contract. Found in the ColorCustomizer sibling (its CC-17); every
  repo sharing the ledger system has the same blind spot.
  Fixed in the TreasureMaster sibling 2026-07-21 (its TM-6, commit 5569e8e) and the decision
  there was yes, they fail the contract: an entry-shape regex swept over the non-entry
  sections, proven by a planted stray going red and the revert going green. The port is that
  one test with the id prefix swapped to OC.

- [OC-7] 2026-10-26: A Linux player who unzips a release built on the Windows desktop gets loose
  files named with backslashes instead of a prawl.fft.offensivechemist folder, so Reloaded never
  sees the mod; the GitHub CI zip is unaffected because pwsh writes forward slashes. Found live
  on the TreasureMaster sibling 2026-10-19 and fixed there as TM-9 (commit a7ee82b), the same
  fix ColorCustomizer carries. (Tech: Publish.ps1 line 165 uses ZipFile.CreateFromDirectory
  under Windows PowerShell 5.1, which writes backslash separators into entry names; write the
  entries by hand with '/' and make Verify-Package fail on any backslash.)

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
