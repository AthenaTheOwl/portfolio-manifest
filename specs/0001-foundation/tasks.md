# Tasks — 0001 Foundation

Checkbox tasks ordered for the first two to three PRs after the
scaffold.

## PR 1 — Schemas and example manifest

- [ ] Write `schemas/manifest.schema.json` per R-PM-001
- [ ] Write `schemas/snapshot.schema.json` per R-PM-004
- [ ] Write `schemas/check-result.schema.json` per R-PM-005
- [ ] Write `manifests/example.yaml` declaring three fixture repos
- [ ] Add `decisions/DEC-PM-001-contracts-closure.md`
- [ ] Add `scripts/validate_schemas.py` skeleton
- [ ] Add `scripts/validate_manifests.py` skeleton

## PR 2 — Walker and check module skeletons

- [ ] Implement `src/portfolio_manifest/walker.py` (clone or fetch
      into `.cache/`)
- [ ] Add six check module skeletons under
      `src/portfolio_manifest/checks/`
- [ ] Each skeleton returns a `CheckResult` with status `warn` and
      a TODO note; PR 3 fills in real behaviour
- [ ] Wire CLI entry: `python -m portfolio_manifest validate`
- [ ] Add `scripts/voice_lint.py` skeleton

## PR 3 — Snapshot renderer and first snapshot

- [ ] Implement `src/portfolio_manifest/snapshot.py`
- [ ] Add `templates/snapshot.md.j2`
- [ ] Implement two of the six checks fully:
      `decision-freshness` and `voice-lint-banlist`
- [ ] Render the first snapshot at `reports/2026-W34.md` against
      the example manifest
- [ ] Add `scripts/validate_snapshots.py` skeleton
- [ ] Update README install + run section once `audit` runs end-
      to-end on the example
