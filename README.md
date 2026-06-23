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

v0.1 ships. The Python CLI runs end-to-end against the example
manifest, emits the Markdown snapshot under `reports/<iso-week>.md`,
and appends one JSONL row per repo to `data/ledger/<run-id>.jsonl`.
Two of six contracts do real work (`decision-freshness`,
`voice-lint-banlist`); the other four are explicit skeletons that
emit `warn` until spec 0002 fills them in. The full live state —
what works, what does not, and what is next — is in
[STATUS.md](STATUS.md).

## How to run

```
python -m portfolio_manifest show
python -m portfolio_manifest validate --manifest manifests/example.yaml
python -m portfolio_manifest audit --manifest manifests/example.yaml --out reports/2026-W34.md
```

`show` reads the latest committed snapshot under `reports/` and prints
a ranked, readable view: repos ordered by drift score, the real
findings (skeleton placeholders excluded), and a one-line headline. It
is read-only and offline. `validate` checks the manifest against the
schema and confirms each declared contract has a check module on disk.
`audit` runs every check, writes the Markdown snapshot, and prints the
per-repo drift score. Spec 0002 lands the real `git clone` walker;
v0.1 reads from per-repo fixtures under `tests/fixtures/repos/`.

## live demo

A Streamlit page renders the same committed snapshot as an interactive
cross-repo health view: repos ranked by drift, a toggle to hide
skeleton-only repos, and a headline finding. It reads
`reports/*.md` directly — no network, no secrets.

Run locally:

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: New app -> repo
`AthenaTheOwl/portfolio-manifest`, branch `main`, main file
`streamlit_app.py`.

<!-- live-url: -->


## Layout

```
portfolio-manifest/
  README.md
  PRODUCT_BRIEF.md          # operator-facing brief
  SYSTEM_MAP.md             # canonical wiring diagram
  STATUS.md                 # live state, known limits, next queue
  LICENSE
  AGENTS.md
  pyproject.toml
  docs/
    METHODOLOGY.md          # the "why" behind drift scoring
    system-map.md           # longer narrative version of SYSTEM_MAP
    first-pr.md
  decisions/
    DEC-PM-001-contracts-closure.md
  specs/
    0001-foundation/{requirements,design,tasks,acceptance}.md
    0002-design/{requirements,design,tasks,acceptance}.md
  portfolio_manifest/
    manifest.py walker.py snapshot.py drift.py
    score.py ledger.py report.py
    cli.py __main__.py
    checks/<contract>.py
  manifests/example.yaml
  schemas/{manifest,snapshot,check-result}.schema.json
  templates/snapshot.md.j2
  scripts/{validate_*,voice_lint}.py
  reports/2026-W34.md       # first weekly snapshot (human-readable)
  data/ledger/2026-W25.jsonl  # first audit run (machine-readable)
  tests/
```

## License

MIT. See [LICENSE](LICENSE).
