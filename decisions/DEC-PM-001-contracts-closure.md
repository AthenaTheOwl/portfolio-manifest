# DEC-PM-001 — Contracts closure at six

- Status: accepted
- Date: 2026-06-22
- Spec: 0001-foundation
- Requirement: R-PM-003, R-PM-010

## Context

A manifest declares which contracts each tracked repo honours. The
runner can only check what the contract list names. Opening the list
to an arbitrary plugin surface in v0 would mean every contract check
has to negotiate its own data shape, versioning, and `days_behind`
semantics. We picked six contracts for v0 instead, closed the list,
and named extension via DEC entries.

## Decision

v0 ships with exactly six contracts:

| Contract | Shape | Source of truth in the repo |
|---|---|---|
| `decision-schema` | version compare | `decisions/_meta.yaml` schema version |
| `spec-schema` | version compare | `specs/_meta.yaml` schema version |
| `dream-schema` | version compare | `dreams/_meta.yaml` schema version |
| `voice-lint-banlist` | sha256 hash compare | declared banlist hash |
| `eval-coverage` | ratio compare to floor | `ops/eval-coverage.json` |
| `decision-freshness` | mtime compare to max age | newest decision file mtime |

All six reduce to one of two underlying check shapes: "is the
declared version current" or "is the declared metric within a
declared threshold". A seventh contract that does not reduce to one
of these two shapes requires a new DEC, not just a manifest entry.

## Contracts considered and deferred

- **Security posture.** OpenSSF Scorecard already covers this and
  scores at the commit level, not at the contract-version level.
  Adding it would duplicate Scorecard without adding signal.
- **Dependency freshness.** Dependabot, Renovate, and equivalent
  bots already raise per-dependency PRs. The cross-repo view would
  be a roll-up of those bots, not new signal.
- **Ownership / CODEOWNERS.** Backstage and similar service-catalog
  tools own this surface. Cross-repo CODEOWNERS drift is a real
  problem but is one full product, not a contract check.

## Consequences

- The manifest schema enumerates the six contracts as required
  keys. A manifest that omits any of them is invalid.
- Adding a seventh contract is a DEC, a schema bump, and a new
  check module. It is not a one-line manifest edit.
- The three deferred contracts can come back later if signal from
  the named tools turns out to be insufficient. The cost of saying
  "not yet" is one entry in this DEC.
