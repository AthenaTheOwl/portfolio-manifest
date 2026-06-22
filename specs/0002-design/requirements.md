# Requirements — 0002 Design

Numbered requirements for filling out the four skeleton checks,
landing the real walker, and shipping a cross-snapshot drift ledger.

## Real checks

- **R-PM-011** `decision-schema` reads
  `<repo>/decisions/_meta.yaml`, extracts `schema_version`, and
  compares to `contracts.decision_schema.latest`. Status is `pass`
  on match, `warn` on a single major behind, `fail` on two or
  more.
- **R-PM-012** `spec-schema` and `dream-schema` follow the same
  shape against `<repo>/specs/_meta.yaml` and
  `<repo>/dreams/_meta.yaml` respectively.
- **R-PM-013** `eval-coverage` reads
  `<repo>/ops/eval-coverage.json` (a number under the
  `coverage_ratio` key) and compares to
  `contracts.eval_coverage.min_ratio`. Status is `fail` below
  `min_ratio - 0.10`, `warn` below `min_ratio`, `pass` at or
  above.

## Real walker

- **R-PM-014** The walker performs `git clone --depth 1` on the
  manifest's `clone_url` into `.cache/<repo-name>/` when the cache
  directory does not exist. When it exists, the walker runs
  `git fetch --depth 1 origin <branch>` and resets to the fetched
  head. An `--offline` flag re-uses whatever is on disk.

## Cross-snapshot drift

- **R-PM-015** A drift-event ledger is written at
  `reports/_drift.jsonl`. Each line is one drift event keyed by
  `(manifest_id, repo, contract, iso_week)`. The audit command
  appends to this file at the end of each run.
- **R-PM-016** Once two snapshots exist, recalibrate the drift
  weights. The default weights (warn=1, fail=3) are recorded in
  DEC-PM-002. A calibration pass that materially changes weights
  must also update the DEC.

## Reporting hooks

- **R-PM-017** A `.github/workflows/weekly-audit.yml` runs the
  audit on a cron, writes a new snapshot, and commits it back to
  `reports/` on the same branch.

## Acceptance

- The example manifest produces zero `warn` rows in 2026-W35 once
  all six checks are real. Any `warn` then represents real drift,
  not skeleton behaviour.
- `reports/_drift.jsonl` is appended (not rewritten) on each
  audit.
- The weekly workflow commits a snapshot at the expected path
  with no manual step.
