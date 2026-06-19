# PortfolioManifest

Cross-repo health dashboard as a service. The hosted shape of athena-site's `ops/portfolio-manifest.yml` plus the weekly `scripts/portfolio_audit.py` cron, productized for any developer or organization maintaining ten or more repos that need cross-repo consistency on schemas, voice, decisions, and evals.

## What this is

A manifest format plus an audit runner plus a published weekly health
snapshot. Each tracked repo declares its artifact contracts (decision
schema version, spec schema version, dream schema version, voice-lint
banlist version). The runner walks the manifest weekly, checks each
repo against the declared contracts, and emits a single health snapshot.

The audit answers questions a multi-repo maintainer otherwise has to
answer by hand:

- Which repos drifted off the current decision schema?
- Which repos are using a voice-lint banlist that is six weeks behind?
- Which repos have stale eval coverage?
- Which repos have not produced a decision in ninety days?

The manifest is the contract. The runner is the script. The snapshot is
the artifact.

## Who uses it

Multi-repo open-source maintainers (cloud-native foundations,
scientific-computing orgs). Platform teams at firms with one hundred or
more internal services. VPEs who treat cross-repo drift as a real cost
and have no GitHub-native answer.

## Why now

Multi-repo orgs have rediscovered that monorepo-or-bust is wrong.
Cross-repo schema drift and voice drift are real costs. Existing
dependency-graph tools (Backstage, OpenSSF Scorecard) cover security
and ownership; they do not cover artifact-contract consistency.
athena-site already runs the pattern for the user's portfolio; this
repo extracts it as a primitive.

## Status

v0 scaffold; no implementation yet. The specs ledger names the first
set of requirements (R-PM-001 through R-PM-010). The first PR after
this scaffold lands the manifest schema and the audit-runner skeleton.

## How to run

Placeholder; will land in spec 0002. v0 ships the manifest schema,
an example manifest covering three repos as a fixture, and the audit
runner skeleton. No live audit yet.

The eventual CLI shape (target for spec 0003):

```
python -m portfolio_manifest audit --manifest manifests/example.yaml --out reports/2026-W34.md
python -m portfolio_manifest validate --manifest manifests/example.yaml
```

## Layout

```
portfolio-manifest/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
```

Future directories (named in specs, not created yet):

- `src/portfolio_manifest/` — runtime
- `src/portfolio_manifest/checks/` — one module per contract check
- `manifests/` — example manifests
- `schemas/` — manifest, snapshot, check-result schemas
- `reports/` — weekly health snapshots

## License

MIT. See [LICENSE](LICENSE).
