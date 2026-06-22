# STATUS

Operational state of portfolio-manifest as of 2026-W25 (2026-06-22).
This file is the single source of truth for "what works, what does
not, what is next." Updated each cut.

## Current state

- v0.1 ships. The Python CLI runs end-to-end against the example
  manifest and emits a Markdown snapshot.
- Manifest, snapshot, and check-result JSON Schemas (draft 2020-12)
  are checked in under `schemas/` and validated by
  `scripts/validate_schemas.py`.
- `manifests/example.yaml` declares three fixture repos and validates
  against the manifest schema. All six declared contracts resolve to
  Python modules under `portfolio_manifest/checks/`.
- Two of six checks have real behaviour: `decision-freshness` (reads
  the most recent decision-file mtime and compares to the declared
  max age) and `voice-lint-banlist` (compares declared banlist hash
  to the manifest's pinned hash). The other four return `warn` with
  a "skeleton, not yet implemented" note — explicit by R-PM-007.
- The first weekly snapshot is checked in at `reports/2026-W34.md`.
  It is the first row of the cross-repo ledger and the artifact a
  reviewer reads to judge whether v0.1 is useful.
- `DEC-PM-001` records the v0 closure to six contracts and names
  three contracts deferred (security posture, dependency freshness,
  ownership) with a one-line reason each.
- Gates: `pytest`, `validate_schemas.py`, `validate_manifests.py`,
  `validate_decisions.py`, and `voice_lint.py` all exit zero.
- Tests cover the manifest loader, check dispatcher, snapshot
  renderer, and drift differ. `pytest -q` runs in under two seconds
  on the example fixture.

## Known limits

- Four of six checks (`decision-schema`, `spec-schema`,
  `dream-schema`, `eval-coverage`) are skeletons. They emit `warn`
  with a stable note. Spec 0002 fills them in.
- The walker does not actually clone repos in v0.1. It treats the
  manifest's `clone_url` as opaque and reads check inputs from
  per-repo fixture directories under `tests/fixtures/repos/`.
  Real git clone-or-fetch lands in spec 0002.
- Drift events require two snapshots. `reports/2026-W34.md` is the
  first snapshot; the drift differ has tests against a synthetic
  pair but no real cross-snapshot row is checked in yet.
- No GitHub App wrapper. No web dashboard. No multi-manifest
  hosting. All three are explicitly deferred to spec 0004 and
  beyond per AGENTS.md.
- `voice_lint.py` runs on `reports/*.md` with a small banned-words
  set. The set is intentionally narrow in v0.1; the production
  banlist is governed by spec 0003.
- The CLI exposes `validate` and `audit`. There is no `init`,
  `diff`, or `dashboard` subcommand yet.
- No CI configuration is checked in. The factory's contract gate is
  the only enforcement so far. A GitHub Actions matrix is spec 0003
  scope.

## Next feature queue

- **R-PM-011 (spec 0002):** Real `decision-schema` check. Read the
  target repo's `decisions/SCHEMA.md` or `decisions/_meta.yaml`,
  extract the declared schema version, compare to
  `contracts.decision_schema.latest`. Compute `days_behind` from
  the manifest's schema-release table.
- **R-PM-012 (spec 0002):** Real `spec-schema` and `dream-schema`
  checks. Same shape as `decision-schema`; pull declared version
  from `specs/_meta.yaml` and `dreams/_meta.yaml` respectively.
- **R-PM-013 (spec 0002):** Real `eval-coverage` check. Read
  `ops/eval-coverage.json` from the target repo; compare to the
  manifest's `contracts.eval_coverage.min_ratio`. Status is
  `fail` if below `min_ratio - 0.10`, `warn` if below `min_ratio`,
  else `pass`.
- **R-PM-014 (spec 0002):** Walker actually clones. Use
  `git clone --depth 1` into `.cache/<repo-name>/` and
  `git fetch` if already present. The walker honours a
  `--offline` flag that re-uses whatever is in `.cache/`.
- **R-PM-015 (spec 0003):** Drift-event ledger. Write a
  cross-snapshot ledger at `reports/_drift.jsonl` so weekly
  snapshots can be diffed without re-rendering. Each line is one
  drift event keyed by `(manifest_id, repo, contract, week)`.
- **R-PM-016 (spec 0003):** Calibration pass. Once two full
  snapshots exist, recompute the drift-score weights from the
  observed distribution of statuses. Pin the calibrated weights
  in `decisions/DEC-PM-002-drift-weights.md`.
- **R-PM-017 (spec 0003):** GitHub Actions workflow at
  `.github/workflows/weekly-audit.yml` that runs `audit` on a
  cron and commits the snapshot back to `reports/`.
- **R-PM-018 (spec 0004):** GitHub App wrapper. Receive
  installation webhook, run the manifest's audit on push to the
  configured branch, post a check-run with the snapshot URL.

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing data/ledger/*.jsonl
- Resolve factory defect: METHODOLOGY.md missing revisit section
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'portfolio_manifest/cli.py' is missing
- Resolve factory defect: expected file 'portfolio_manifest/score.py' is missing
- Resolve factory defect: expected file 'portfolio_manifest/ledger.py' is missing
- Resolve factory defect: expected glob 'data/ledger/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'portfolio_manifest/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'portfolio_manifest/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'portfolio_manifest/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'portfolio_manifest/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
- Resolve factory defect: expected file 'portfolio_manifest/cli.py' is missing
- Resolve factory defect: expected file 'portfolio_manifest/score.py' is missing
- Resolve factory defect: expected file 'portfolio_manifest/ledger.py' is missing
- Resolve factory defect: module 'cli' declares source 'portfolio_manifest/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'portfolio_manifest/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'portfolio_manifest/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'portfolio_manifest/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
