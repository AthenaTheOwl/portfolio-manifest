# Acceptance — 0002 Design

"v0.2 done" means the following hold simultaneously.

## Artifacts present

- `reports/2026-W34.md` exists (lands in v0.1; remains the first
  row).
- `reports/2026-W35.md` exists with real numbers from the four
  newly-real checks.
- `reports/_drift.jsonl` exists with at least one drift event
  representing the transition from W34 to W35.
- `decisions/DEC-PM-002-drift-weights.md` exists and pins the
  current weights.

## Gates pass

```
python -m pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py
python scripts/validate_manifests.py
python scripts/validate_decisions.py
python scripts/validate_snapshots.py
```

All six exit zero.

## Walker behaviour

```
python -m portfolio_manifest audit --manifest manifests/example.yaml --out reports/_smoke.md
```

On a clean working directory, the walker clones each repo into
`.cache/<name>/`. On a subsequent run, the walker fetches and
resets to the configured branch.

```
python -m portfolio_manifest audit --manifest manifests/example.yaml --out reports/_smoke.md --offline
```

On `--offline`, the walker uses whatever is on disk and never
touches the network.

## Manual review

- Every `warn` in the snapshot now represents real drift, not a
  skeleton placeholder.
- A reader can scan the drift ledger and answer "which repos
  drifted off `decision-schema` in the last four weeks?" in one
  grep.

## Out of v0.2 acceptance

- No GitHub App wrapper. That is spec 0004.
- No web dashboard. The snapshot Markdown is the artifact.
- No notification fan-out (Slack, email). Drift events live in
  the JSONL ledger.
