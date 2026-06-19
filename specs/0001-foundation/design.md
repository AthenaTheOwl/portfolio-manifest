# Design — 0001 Foundation

## Shape

portfolio-manifest is a Python CLI that walks a manifest of N repos,
runs a fixed set of contract checks against each repo, and emits a
weekly snapshot Markdown file.

The architecture has four layers:

1. **Manifest.** `manifests/<id>.yaml` declares the repos to audit
   and the contracts each repo claims to honour.
2. **Walker.** `src/portfolio_manifest/walker.py` ensures each
   repo is locally available (clone if missing, fetch if stale).
3. **Checks.** `src/portfolio_manifest/checks/<contract>.py` is one
   module per contract. Each module exposes a single `run` function.
4. **Snapshot.** `src/portfolio_manifest/snapshot.py` composes the
   per-repo check results into a Markdown snapshot.

## Data flow

```
manifests/<id>.yaml
   |
   v
[walker.ensure_local]  ->  ./.cache/<repo-name>/
   |
   v
for each repo, for each declared contract:
    [checks.<contract>.run]  ->  CheckResult
   |
   v
[snapshot.render]  ->  reports/<iso-week>.md
   |
   v
[drift.diff_against_previous]  ->  drift_events[]
```

## Contracts in v0

- `decision-schema`: the repo declares the version of decision
  schema it follows. The check compares against the latest version
  in the manifest's `contracts.decision_schema.latest`.
- `spec-schema`: same shape for spec schema.
- `dream-schema`: same shape for dream schema.
- `voice-lint-banlist`: the repo declares a banlist version. The
  check compares hashes.
- `eval-coverage`: the repo publishes an eval-coverage number under
  `ops/eval-coverage.json`. The check reads it and compares to a
  declared minimum.
- `decision-freshness`: the check reads the most recent decision
  file mtime and compares to a declared maximum age.

The closure to six contracts is a v0 simplification. Schema-version
checks and freshness checks are the two shapes; adding a seventh
contract is mostly a question of declaring a target version or
target threshold.

## Drift event mechanics

A drift event is emitted only on a status transition between
consecutive snapshots. A repo that has been `fail` on
`decision-schema` for three weeks produces a drift event in week 1
and no drift event in weeks 2 and 3. This keeps the snapshot
focused on new news.

## Manifest validation

`scripts/validate_manifests.py` confirms that every declared
contract resolves to a check module, every clone URL is well-
formed, and every repo entry has the required fields. Manifests
that fail this gate cannot be audited.

## Out of v0 scope

- A GitHub App wrapper
- A web dashboard
- Per-customer multi-manifest hosting
- Auto-fix suggestions when a check fails
