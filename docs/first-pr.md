# First PR

The literal first PR after this scaffold. The goal is the schemas,
the example manifest, and the decision record closing the contract
set — no runtime yet.

## Files this PR adds

- `schemas/manifest.schema.json`
  - JSON Schema draft 2020-12
  - Required: `id`, `owner`, `repos[]`, `contracts`, `schedule`
  - `repos[]` each: `name`, `clone_url`, `branch`,
    `declared_contracts`
  - `contracts`: object with one key per supported contract, each
    naming the `latest` version
- `schemas/snapshot.schema.json`
  - Required: `manifest_id`, `iso_week`, `repos[]`
  - Each repo entry: `name`, `check_results[]`, `drift_score`,
    optional `drift_events[]`
- `schemas/check-result.schema.json`
  - Required: `contract`, `status`, `current_version`,
    `expected_version`
  - Optional: `days_behind`, `notes`
  - `status` enum: `pass`, `warn`, `fail`
- `manifests/example.yaml`
  - `id: example-portfolio`
  - `owner: vignesh`
  - Three fixture repos with placeholder clone URLs and declared
    contracts
  - `contracts.decision_schema.latest: v3`, similar for the other
    five
- `decisions/DEC-PM-001-contracts-closure.md`
  - Lists the six v0 contracts: `decision-schema`, `spec-schema`,
    `dream-schema`, `voice-lint-banlist`, `eval-coverage`,
    `decision-freshness`
  - Names three contracts considered and deferred (security
    posture, dependency freshness, ownership), with a one-line
    reason each
- `scripts/validate_schemas.py`
  - Loads every file under `schemas/` and confirms it parses as
    JSON Schema
- `scripts/validate_manifests.py`
  - Loads every file under `manifests/`, validates against the
    manifest schema, confirms each declared contract resolves to
    a planned check module path

## Verification

```
python -m pytest        # no tests yet; runner exits clean
python scripts/validate_schemas.py
python scripts/validate_manifests.py
```

All three exit zero. The example manifest validates.

## What this PR does not do

- No CLI commands. PR 2 adds `validate` against the manifest.
- No check modules. PR 2 adds the six skeletons.
- No snapshot renderer. PR 3 lands the template and renderer.
- No voice-lint script. That lands in PR 2.
