# System map

How portfolio-manifest is wired together. Read this once and you
can predict where any new piece of code goes.

## One picture

```
                   manifests/<id>.yaml
                            |
                            v
                  manifest.load_manifest
                            |
                            v
                       Manifest object
                            |
                            v
   +-----------------+      |      +--------------------------+
   |                 v      v      v                          |
   | walker.ensure_local(repo) -> Path                        |
   |                 |                                        |
   |                 v                                        |
   | checks.run_all(path, repo, contracts)                    |
   |     -> list[CheckResult]                                 |
   |                 |                                        |
   |                 v                                        |
   | snapshot.build_snapshot -> dict                          |
   |                 |                                        |
   |                 v                                        |
   | drift.attach_drift_events(previous_snapshot)             |
   |                 |                                        |
   |                 v                                        |
   | snapshot.render_markdown via templates/snapshot.md.j2    |
   +-----------------+----------------------------------------+
                            |
                            v
                  reports/<iso-week>.md
                            |
                            v
                  scripts/voice_lint.py
```

## Layers

| Layer | File | Responsibility |
|---|---|---|
| Manifest | `portfolio_manifest/manifest.py` | Parse YAML, validate against schema, expose `Manifest` and `RepoEntry` dataclasses |
| Walker | `portfolio_manifest/walker.py` | Produce a local `Path` per repo (fixture in v0.1, git clone in v0.2) |
| Checks | `portfolio_manifest/checks/<contract>.py` | One module per contract; expose `run(repo_path, manifest_entry, manifest_contract) -> CheckResult` |
| Snapshot | `portfolio_manifest/snapshot.py` | Compose per-repo results, render Markdown via Jinja2 |
| Drift | `portfolio_manifest/drift.py` | Diff two snapshots, emit drift events on status transitions |
| CLI | `portfolio_manifest/cli.py` | `validate` and `audit` subcommands via Click |
| Templates | `templates/snapshot.md.j2` | The single Markdown template |
| Schemas | `schemas/*.schema.json` | Draft 2020-12 JSON Schemas for manifest, snapshot, check-result |
| Scripts | `scripts/*.py` | Local gates: schema/manifest/decision validators, voice lint |

## What lives where

- **New contract?** Add the module under
  `portfolio_manifest/checks/`. Add the contract name to
  `SUPPORTED_CONTRACTS` in `manifest.py`. Bump
  `schemas/manifest.schema.json` to require the new key under
  `contracts`. Add a DEC. Update the snapshot template only if
  the new contract emits a field the table does not already have.
- **New manifest?** Drop a YAML under `manifests/`. Run
  `scripts/validate_manifests.py`.
- **New snapshot?** The CLI writes it. Hand-edit only the
  surrounding prose, not the table data.
- **New decision?** `decisions/DEC-PM-NNN-<slug>.md`. Run
  `scripts/validate_decisions.py`.

## Boundaries (what this is not)

- Not a service catalog. Backstage owns ownership and service
  metadata.
- Not a security scanner. OpenSSF Scorecard owns security signal.
- Not a dashboard. The Markdown snapshot is the artifact.
