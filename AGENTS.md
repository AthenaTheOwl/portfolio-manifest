# AGENTS.md — portfolio-manifest

Operating contract for AI agents working in this repo. Conventions
match the AthenaTheOwl portfolio so an agent already trained on
athena-site's portfolio_audit.py recognizes the shape.

## What this repo is

A manifest format plus an audit runner. Given a manifest listing N
repos with their declared artifact contracts, the runner walks each
repo, applies each contract check, and emits a single weekly health
snapshot Markdown file.

The manifest is checked-in YAML. The snapshot is checked-in Markdown.
The runner is a Python CLI. There is no hosted dashboard in v0; the
snapshot under `reports/` is the artifact.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `manifest-loader` | Parses a manifest YAML, validates against the manifest schema |
| `repo-walker` | Clones or fetches each repo named in the manifest |
| `contract-checker` | Runs one named contract check against one repo |
| `snapshot-renderer` | Composes per-repo check results into a weekly snapshot |
| `drift-flagger` | Emits a structured drift event when a repo crosses a threshold |

These roles exist in the spec ledger; not all are implemented in v0.

## Voice constraints

- No marketing words. The banned set will live in
  `scripts/voice_lint.py::BANNED_FAIL` once the gate lands.
- No antithetical reversals as a structural device.
- A snapshot report names drift with numbers, not adjectives. "Three
  repos are eighteen days behind on decision schema v3" beats "some
  repos are seriously lagging."

## Gates (will land in spec 0002)

Planned local gates before pushing:

- `pytest`
- `voice_lint.py` on `reports/*.md`
- `spec_check.py` against `specs/`
- `validate_manifests.py` — every manifest validates and every
  declared check exists as a module
- `validate_snapshots.py` — every snapshot validates against the
  snapshot schema

## Out of scope

- Code-quality scoring. This is artifact-contract drift, not lint.
- GitHub Actions hosting. v0 is a CLI; the GitHub App wrapper is
  spec 0004.
- Ownership / security checks. Backstage and OpenSSF Scorecard
  already cover that ground.
- A web dashboard. Markdown snapshots are the artifact.
