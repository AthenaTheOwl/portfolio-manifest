# Tasks — 0002 Design

Tasks for spec 0002, ordered for the first three PRs after the
v0.1 cut.

## PR 4 — Real walker

- [ ] Implement `git clone --depth 1` in `walker.ensure_local`
- [ ] Add `--offline` flag wired through to the walker
- [ ] Persist a small `.cache/_state.json` recording the SHA we
      last fetched per repo
- [ ] Add walker tests against a local fixture repo (use
      `tmp_path` and `git init`)

## PR 5 — Real checks

- [ ] Implement `decision-schema` against `<repo>/decisions/_meta.yaml`
- [ ] Implement `spec-schema` against `<repo>/specs/_meta.yaml`
- [ ] Implement `dream-schema` against `<repo>/dreams/_meta.yaml`
- [ ] Implement `eval-coverage` against
      `<repo>/ops/eval-coverage.json`
- [ ] Update STATUS.md current state and known limits
- [ ] Regenerate `reports/2026-W34.md` (or land 2026-W35 with
      real numbers)

## PR 6 — Drift ledger and calibration

- [ ] Append-only writer for `reports/_drift.jsonl`
- [ ] Discover previous snapshot from `reports/` and diff
- [ ] Add `scripts/calibrate.py` reading the drift ledger
- [ ] Add DEC-PM-002 recording the v0.2 drift weights
- [ ] Land the second snapshot at `reports/2026-W35.md`
