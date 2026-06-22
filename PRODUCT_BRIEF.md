# PortfolioManifest — Product brief

Operator-facing brief. The marketing pitch lives in `README.md`; this
doc is what the person responsible for running the audit reads before
they touch the manifest.

## Who this is for

A multi-repo maintainer responsible for ten or more repos in the same
org that share artifact contracts: a decision-schema version, a
spec-schema version, a dream-schema version, a voice-lint banlist
hash, an eval-coverage floor, and a decision-freshness ceiling. The
canonical user is the maintainer of athena-site's portfolio (six
repos today, projected fifteen in twelve months). The general user
is a platform engineer or VPE at a 100+ service org who has tried
Backstage, Scorecard, and Renovate and found that none of them
answer "is repo X still on the current contract version?"

## The problem this solves

Cross-repo contract drift is invisible until something breaks. A
maintainer who owns ten repos cannot eyeball ten READMEs each week
and notice that three of them are running last quarter's voice-lint
banlist. The same maintainer cannot afford to write a one-off audit
script per contract per quarter.

Existing tools cover adjacent surfaces:

- OpenSSF Scorecard scores security posture per commit. Out of scope.
- Dependabot/Renovate raise per-dependency PRs. Out of scope.
- Backstage tracks ownership and service metadata. Out of scope.

None of them check "the artifact contracts this repo claims to
honour are actually current". That is the gap.

## v0 success criterion

A single command — `python -m portfolio_manifest audit --manifest
manifests/example.yaml --out reports/<iso-week>.md` — produces a
Markdown snapshot that:

1. Lists every tracked repo with one row per contract.
2. Assigns each row a status of `pass`, `warn`, or `fail`.
3. Sums a drift score per repo using the 1:3 weight (warn:fail)
   pinned in DEC-PM-002.
4. Reads in under thirty seconds.
5. Names at least one real signal — not just skeleton warnings —
   so the snapshot is worth checking in.

v0.1 ships with two of six contracts doing real work
(`decision-freshness`, `voice-lint-banlist`) and four skeletons that
explicit `warn` until spec 0002 fills them in. The first checked-in
snapshot (`reports/2026-W34.md`) catches two real signals: a 113-day
stale decision-freshness on `dream-ledger`, and a banlist hash
mismatch on `decision-store`. That is the v0.1 acceptance shape.

## What v0 deliberately does not ship

- No GitHub App. The runner is a Python CLI.
- No web dashboard. The Markdown snapshot is the artifact.
- No multi-manifest hosting. One manifest at a time.
- No real `git clone` walking. v0.1 reads fixtures; spec 0002 lands
  the real walker.
- No notifications. The snapshot lands in the repo as a commit; a
  human reads it.

Each deferral is named in `STATUS.md` under "Known limits" with a
spec or DEC pointer.

## How to read this brief

- If you are deciding whether to adopt this tool, read this file
  plus `README.md` and stop there.
- If you are extending the manifest, read `SYSTEM_MAP.md` and
  `docs/METHODOLOGY.md` next.
- If you are picking up where the last engineer left off, read
  `STATUS.md` for the live state.
