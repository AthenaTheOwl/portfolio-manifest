# Acceptance — 0001 Foundation

"v0 done" means the following hold simultaneously.

## Artifacts present

- `schemas/manifest.schema.json` validates
- `schemas/snapshot.schema.json` validates
- `schemas/check-result.schema.json` validates
- `manifests/example.yaml` parses against the manifest schema and
  declares at least three fixture repos
- `decisions/DEC-PM-001-contracts-closure.md` exists
- `templates/snapshot.md.j2` renders without errors

## Gates pass

Run from the repo root:

```
python -m pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py
python scripts/validate_manifests.py
python scripts/validate_decisions.py
```

All five exit zero.

## CLI smoke

```
python -m portfolio_manifest validate --manifest manifests/example.yaml
```

Exits zero on the example manifest. The CLI prints a per-repo
summary noting that all checks return `warn` (the v0 skeleton
behaviour).

## Manual review

- A reader can read the example manifest and name the three repos
  and their declared contracts within thirty seconds.
- The DEC names the six contracts and explains why each made the
  v0 cut.
- The snapshot template renders a recognisable weekly health card.

## Out of v0 acceptance

- Live audit against real repos is spec 0002. v0 ships skeletons
  for all six checks; only `decision-freshness` and
  `voice-lint-banlist` have real behaviour by spec 0001 end.
- Drift events between snapshots require two snapshots to exist.
  v0 ships the first; the drift mechanic activates in spec 0003.
- No GitHub App wrapper.
