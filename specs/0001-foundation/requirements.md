# Requirements — 0001 Foundation

Numbered requirements for the v0 scaffold of portfolio-manifest. The
R-PM-* prefix is the brand tag and appears in every downstream spec,
decision, and gate.

## Manifest

- **R-PM-001** The repo ships a manifest schema under
  `schemas/manifest.schema.json`. Fields: `id`, `owner`, `repos[]`,
  `contracts`, `schedule`.
- **R-PM-002** Each repo entry has `name`, `clone_url`, `branch`,
  `declared_contracts`, `last_audited_at`.
- **R-PM-003** A contract is one of `decision-schema`, `spec-schema`,
  `dream-schema`, `voice-lint-banlist`, `eval-coverage`,
  `decision-freshness`. v0 closes the list at these six; extensions
  require a DEC entry.

## Snapshots

- **R-PM-004** The repo ships a snapshot schema under
  `schemas/snapshot.schema.json`. Fields: `manifest_id`, `iso_week`,
  `repos[]`. Each repo entry has `name`, `check_results[]`, `drift_score`.
- **R-PM-005** A check result has `contract`, `status`
  (`pass`, `warn`, `fail`), `current_version`, `expected_version`,
  `days_behind`.
- **R-PM-006** A snapshot is rendered to Markdown at
  `reports/<iso-week>.md` from a Jinja2 template.

## Checks

- **R-PM-007** Each contract maps to a Python module under
  `src/portfolio_manifest/checks/<contract>.py` exposing
  `run(repo_path, manifest_entry) -> CheckResult`. v0 ships the
  module skeletons for all six contracts; behaviour lands in spec
  0002.

## Drift

- **R-PM-008** A drift score per repo is computed as the count of
  `warn` plus three times the count of `fail`. The score is included
  in the snapshot front-matter.
- **R-PM-009** When a check transitions from `pass` to `fail` between
  consecutive snapshots, the snapshot includes a `drift_event` entry
  naming the repo, the contract, and the transition.

## Governance

- **R-PM-010** Architectural choices are recorded in
  `decisions/DEC-PM-NNN-<slug>.md`. The first decision (DEC-PM-001)
  justifies the closure to six contracts in v0 and lists the
  contracts considered and deferred.
