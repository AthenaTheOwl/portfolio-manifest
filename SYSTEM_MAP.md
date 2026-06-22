# System map

How portfolio-manifest is wired together. Read this once and you
can predict where any new piece of code goes.

A longer narrative version of this doc lives at `docs/system-map.md`;
this root-level file is the canonical entry point referenced by the
factory contract.

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
   | score.compute_drift_score(check_results) -> int          |
   |                 |                                        |
   |                 v                                        |
   | snapshot.build_snapshot -> dict                          |
   |                 |                                        |
   |                 v                                        |
   | drift.attach_drift_events(previous_snapshot)             |
   |                 |                                        |
   |                 v                                        |
   | ledger.append_run(snapshot) -> data/ledger/<run>.jsonl   |
   |                 |                                        |
   |                 v                                        |
   | report.render_markdown via templates/snapshot.md.j2      |
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
| Score | `portfolio_manifest/score.py` | Compute the per-repo drift score (1×warn + 3×fail). |
| Snapshot | `portfolio_manifest/snapshot.py` | Compose per-repo results into the snapshot dict |
| Ledger | `portfolio_manifest/ledger.py` | Append one JSONL row per audit run to `data/ledger/<run>.jsonl` |
| Report | `portfolio_manifest/report.py` | Render the Markdown snapshot via Jinja2 |
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
- **New snapshot?** The CLI writes it to `reports/<iso-week>.md`
  *and* appends one JSONL row to `data/ledger/<run>.jsonl`.
  Hand-edit only the surrounding prose, not the table data or the
  ledger row.
- **New decision?** `decisions/DEC-PM-NNN-<slug>.md`. Run
  `scripts/validate_decisions.py`.

## Cross-snapshot artifacts

- `reports/<iso-week>.md` is the human-readable snapshot. One per
  ISO week per manifest.
- `data/ledger/<run-id>.jsonl` is the machine-readable ledger. One
  JSON object per line, one line per repo per audit run. Append-only.
- The drift differ reads the previous Markdown snapshot's YAML
  front-matter, not the ledger. The ledger is the audit trail; the
  diff is the news.

## Boundaries (what this is not)

- Not a service catalog. Backstage owns ownership and service
  metadata.
- Not a security scanner. OpenSSF Scorecard owns security signal.
- Not a dashboard. The Markdown snapshot is the artifact.
