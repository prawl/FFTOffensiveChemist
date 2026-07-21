# Logging (the build-report contract)

STATUS: CONTRACT (machine-checked by LogContractTests; this file and tools/lib/say.py are
pinned to each other, so changing the verb set means changing both together)

This mod is data-only: it ships tables, nxd files, and icons that the game reads at startup,
and no code of ours runs while the game plays. So there is no runtime logger here and never
will be (see the WONTFIX record below). The mod's whole voice is its build pipeline, and this
contract governs that voice, adapted from the sibling FFT mods' runtime logging contract.

## The line format

Every headline the pipeline prints is one tagged line:

    [Offensive Chemist] [verb] message

Python tools speak through tools/lib/say.py, which offers exactly three calls: say (an
ordinary progress line), warn (prefixed WARN:, the run continues), and fail (prefixed FAIL:,
printed to stderr, exits 1). PowerShell scripts speak through Write-OcSay in
tools/pipeline.ps1. Bare print() anywhere under tools/ is a contract violation
(LogContractTests source-scans for it).

Indented lines that start with spaces (like "  -> Copying..." or "  X missing file") are
continuation detail under the previous headline and stay bare. Verify habits keep their
capitalized PASS token; a FAIL line means the run exits 1 and nothing after it is generated,
deployed, or packaged.

## The verb glossary (closed set, 8 verbs)

One verb per pipeline stage. LogContractTests pins this table one-for-one, in order, against
the VERBS tuple in tools/lib/say.py, so the doc and the code cannot drift. There is
deliberately no trace, startup, or battle verb: those describe a runtime this mod does not
have.

| Verb | Stage | Discipline |
|---|---|---|
| `[gate]` | tools/gate.py data validation | one PASS line, or FAIL and exit 1 |
| `[generate]` | tools/generate.py sparse table XMLs | one summary line per run |
| `[names]` | tools/patch_names.py item.en.nxd rebuild | PASS with the self-verify result, or FAIL |
| `[abilities]` | tools/patch_ability_names.py ability.en.nxd rebuild | PASS with the self-verify result, or FAIL |
| `[icons]` | tools/recolor_icons.py grenade icon recolor | one line per icon written; WARN when a vanilla source is missing |
| `[test]` | the contract-test gate (dotnet test) as reported by the pipeline | PASS or FAIL from the exit code |
| `[deploy]` | BuildLinked.ps1 staging into the live mods folder | one summary line naming the destination; WARN if the game is running |
| `[package]` | Publish.ps1 zip assembly | one line naming the zip and its size |

## Text rules

- Subject-first plain sentences after the verb bracket; full words, no invented shorthand.
- No em dashes anywhere in tools/ or this file, and no double-dash separators in emitted log
  text or this file (both test-enforced); use colons, commas, and parentheses instead.
- FF16Tools failures inside tools/lib/nxd.py raise SystemExit carrying the external tool's
  own output verbatim; that output is the diagnostic and is exempt from the line format.

## Decided WONTFIX (on the record, part of OC-4)

- No runtime logger facade and no logger seam: there is no runtime to host one.
- No log file or rotation in the mod folder: that folder holds game data, and no process of
  ours ever runs there.
- No flight recorder: nothing happens between builds to record; the nxd self-verify scripts
  already are the black box for the only failures this repo can have.
- No timestamps on console lines: a pipeline run lasts seconds.
- The optional timestamped tee of a build run into $env:TEMP stays unbuilt until a lost
  scrollback ever costs a real debug cycle.
