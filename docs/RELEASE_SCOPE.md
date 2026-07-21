# Release Scope: 1.2.0 (infrastructure)

STATUS: DRAFT (scope not yet locked by the owner)

Current shipped version 1.1.0; proposed next **1.2.0** (owner confirms the bump). This doc is
the ship gate for the release named in docs/TODO.md's Now header; TodoContractTests keeps the
two in lockstep (the release name must appear here).

**Identity: "Adopt the sibling FFT mods' engineering infrastructure."** No gameplay changes are
in scope yet; the owner locks any player-facing scope separately.

## IN (ship gate; every box green = ship)

### 1. Work-ledger system (OC-1)
- [x] docs/TODO.md + docs/CHANGELOG.md + TodoContractTests enforce the ledger contract, wired
      into BuildLinked.ps1 / Publish.ps1 / CI as a hard gate; suite green (shipped b0042ce,
      2026-07-21).

### 2. Nexus identity (OC-2)
- [ ] The release zip carries the real Nexus mod id (the NexusModId placeholder 0 replaced) so
      Vortex shows the mod's version instead of a warning icon.

## OUT (deferred, tracked in the ledger)

- Manifest-driven zip content floors (OC-3).
