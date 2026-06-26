# portfolio-manifest

A repo declares its decision schema is current. The auditor walks it and finds the
last decision was filed 113 days ago, against a 90-day rule. The repo was telling
the truth about the form and lying about the work. portfolio-manifest scores that
gap across a whole portfolio.

## What it does

Once you maintain more than a handful of repos, they drift apart quietly. One falls
behind the current decision schema. Another runs a voice-lint banlist six weeks
stale. A third hasn't produced a decision in three months but still passes every
green checkmark, because no checkmark was ever pointed at decisions. Nobody added it
up, so nobody saw it.

portfolio-manifest adds it up. Each tracked repo declares its artifact contracts in
a manifest — decision schema version, spec schema version, dream schema version,
voice-lint banlist version. The runner walks the manifest, checks every repo against
what it claimed, scores the drift, and writes one health snapshot. The manifest is
the contract, the runner is the script, the snapshot is the receipt.

v0.1 ships two contracts that do real work — `decision-freshness` and
`voice-lint-banlist`. The other four are honest skeletons that emit `warn` until
spec 0002 fills them in. The full live state is in [STATUS.md](STATUS.md).

## Try it

```
python -m portfolio_manifest show
```

```
portfolio health -- 2026-W34  (manifest: example-portfolio)
generated 2026-06-22T00:00:00+00:00  |  3 repos  |  total drift 19

   #  repo            drift  signal  bar
  --  --------------  -----  ------  ------------
   1  dream-ledger        7       1  ############
   2  decision-store      7       1  ############
   3  athena-site         5       0  #########...

real findings (2):
  - dream-ledger | decision-freshness | fail: 2025-12-01 (expected <= 90 days)  [113 days behind]
  - decision-store | voice-lint-banlist | fail: banlist hash drift: repo is using a banlist that does not match the manifest

headline: dream-ledger carries the most drift (7); its sharpest signal is decision-freshness (fail).
note: 12 of the warnings are skeleton placeholders (not signal).
```

`show` reads the latest committed snapshot under `reports/`, ranks repos by drift,
strips the skeleton placeholders out of the signal, and stamps a one-line headline.
Read-only and offline.

## Live demo

A Streamlit page renders the same committed snapshot as an interactive cross-repo
health view: repos ranked by drift, a toggle to hide the skeleton-only repos, and the
headline finding. It reads `reports/*.md` directly — no network, no secrets.

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: New app -> repo
`AthenaTheOwl/portfolio-manifest`, branch `main`, main file
`streamlit_app.py`.

<!-- live-url: -->

## How it connects

This repo is the extraction of a pattern that already runs in production. The weekly
audit, the manifest format, and the portfolio cron originated in
[athena-site](https://github.com/AthenaTheOwl/athena-site) as
`ops/portfolio-manifest.yml` plus `scripts/portfolio_audit.py`. portfolio-manifest
pulls that out as a standalone primitive any multi-repo maintainer can point at their
own tree.

## How to run

```
python -m portfolio_manifest show
python -m portfolio_manifest validate --manifest manifests/example.yaml
python -m portfolio_manifest audit --manifest manifests/example.yaml --out reports/2026-W34.md
```

`validate` checks the manifest against the schema and confirms each declared contract
has a check module on disk. `audit` runs every check, writes the Markdown snapshot,
and prints the per-repo drift score. Spec 0002 lands the real `git clone` walker; for
now v0.1 reads from per-repo fixtures under `tests/fixtures/repos/`.

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
