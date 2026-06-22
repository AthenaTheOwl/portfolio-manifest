# Design — 0002 Design

## What changes from 0001

Spec 0001 shipped the schemas, the example manifest, the runner
scaffolding, and skeleton checks. The runtime works end-to-end; what
it does not yet do is *read the target repo*. Spec 0002 lands the
four real checks, the real walker, and the first cross-snapshot
drift event.

## Walker shape

```
walker.ensure_local(repo) -> Path
    if offline_flag:
        return .cache/<name>
    if not .cache/<name>:
        git clone --depth 1 --branch <branch> <clone_url> .cache/<name>
    else:
        git -C .cache/<name> fetch --depth 1 origin <branch>
        git -C .cache/<name> reset --hard FETCH_HEAD
    return .cache/<name>
```

The walker shells out to git. It does not need a libgit2 binding;
shallow clones keep the disk footprint small enough that the cache
can live in CI runners.

## Check shape (real version)

Each check reads two things: a metadata file inside `repo_path` and
the manifest's contract section. The result types stay identical
to v0.1; only the bodies change. This means the snapshot template,
the schemas, and the drift differ continue to work unchanged.

For schema-version checks, the v0.1 manifest already declares the
expected `latest` version. The new code reads the actual version
out of `_meta.yaml` and compares.

For `eval-coverage`, the input file is `ops/eval-coverage.json`,
a single-key JSON file: `{"coverage_ratio": 0.82}`. Missing file
is a `fail`.

## Drift ledger

A drift ledger is a JSONL file at `reports/_drift.jsonl`. Each
line:

```json
{"manifest_id": "...", "iso_week": "...", "repo": "...", "contract": "...", "from": "warn", "to": "fail"}
```

The audit command discovers the previous snapshot by reading
`reports/<previous-week>.md`'s YAML front-matter (the
`manifest_id` and `iso_week` keys identify it). If no previous
snapshot exists for the manifest, no events are emitted.

Why JSONL instead of one MD per week: a Markdown ledger would
require parsing tables to compute trends. JSONL keeps the trend
view trivial — grep, group, count.

## Calibration

Once two full snapshots exist, run a calibration script that
counts the observed `warn` and `fail` rates per contract. If the
ratio is wildly off (e.g. every repo `fail`s a check, suggesting
the contract is set too tight), surface this in the calibration
report. The actual weight change is a DEC, not an automatic
adjustment.

## Out of 0002 scope

- The GitHub App wrapper (spec 0004).
- Multi-manifest hosting (spec 0004).
- Auto-fix suggestions when a check fails.
- Notifications to Slack or email.
