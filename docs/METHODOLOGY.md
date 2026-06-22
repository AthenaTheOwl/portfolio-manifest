# Methodology

How portfolio-manifest decides what is drift and what is not.
The CLI mechanics are in `SYSTEM_MAP.md` (root) and the longer
narrative is in `docs/system-map.md`; this doc is the why.

## Premise

Multi-repo orgs accumulate contract drift the same way they
accumulate any other drift: nobody sees the whole picture each
week. The fix is not a new tool per contract — it is a single
weekly artifact that names the drift in numbers.

The artifact is the snapshot under `reports/<iso-week>.md`. The
artifact is the product. The CLI is plumbing.

## Two underlying check shapes

Every v0 contract reduces to one of two shapes:

1. **Version compare.** A repo declares the version of some
   schema it follows. The manifest declares the latest. The
   check compares the two. `pass` on match, `warn` on one major
   behind, `fail` on two or more.
2. **Threshold compare.** A repo declares (or surfaces) a
   numeric value. The manifest declares a floor or a max. The
   check compares the value to the threshold. `pass` inside,
   `warn` near the boundary, `fail` outside.

A seventh contract that does not reduce to one of these two is a
DEC, not a one-line manifest edit. This closure is the spine of
DEC-PM-001.

## Three statuses, not five

A snapshot uses three statuses: `pass`, `warn`, `fail`. There is
no `info` or `error`. The reasoning:

- `info` would let checks emit chatter that does not actionably
  represent drift. The snapshot is a drift artifact; status
  values that do not represent drift dilute it.
- `error` (the check itself blew up) collapses to `fail` with a
  `notes` field. A check that cannot answer is failing to do
  its job.

## Drift score weights

A repo's drift score is `1 * count(warn) + 3 * count(fail)`. The
ratio is the only knob worth tuning. v0 picks 1:3 because:

- A single `fail` should outrank two `warn`s when sorting the
  ledger. Otherwise a flood of `warn`s drowns out the one repo
  that actually broke a contract.
- Three is the smallest integer that achieves this. Larger
  ratios were considered (1:5, 1:10) and rejected as harder to
  reason about with no clear benefit on the example portfolio.

These weights are recorded in DEC-PM-002 (to land in spec 0002)
so a future calibration pass can change them with an audit
trail.

## Drift events only on transitions

A repo that has been `fail` on `decision-schema` for three weeks
emits one drift event in week 1 and no drift events in weeks 2
and 3. R-PM-009. The reasoning is that a weekly report should
be readable in thirty seconds; persistent failures are visible in
the drift-score column, not as new news.

A drift event is "this got worse this week" or "this got better
this week". The score column is "this is still bad."

## Calibration cadence

The drift weights are pinned in DEC-PM-002 until the calibration
script (spec 0002, R-PM-016) recommends a change. Calibration
runs whenever the cumulative drift ledger has more than thirteen
weeks of data — roughly one quarter. The cadence is quarterly,
not weekly, on purpose: a weekly recalibration would chase noise.

## When to add a contract

A new contract is worth adding when all three are true:

1. The signal is not already in Scorecard, Dependabot,
   Backstage, or another tool the user already runs.
2. The signal is structurally checkable (version compare or
   threshold compare), not a judgment call.
3. The signal applies to at least three of the repos in the
   manifest. Two is a one-off; one is a fixture.

If any of the three is false, the answer is "not yet" and a DEC
entry under DEC-PM-001's deferred list.

## What revisits this

This doc is intentionally stable. Three named triggers re-open
it; nothing else should.

1. **Calibration pass after thirteen weeks of ledger data
   (R-PM-016).** The first calibration run lands once
   `data/ledger/*.jsonl` has accumulated at least thirteen ISO
   weeks of audit rows. If the observed warn/fail distribution
   suggests the 1:3 weight is wrong, the calibration script
   writes a recommended ratio and DEC-PM-002 records the
   change. The "Drift score weights" section above is the
   thing that has to be edited in lockstep.
2. **A new contract that does not fit version-compare or
   threshold-compare (DEC-PM-001 deferred list).** Adding a
   third underlying shape means the "Two underlying check
   shapes" section is no longer two. That edit is paired with
   the DEC that opens the new shape.
3. **A status value beyond `pass`/`warn`/`fail`.** Spec 0004
   considers an `info` status for the GitHub-App wrapper's
   check-run integration. If that ships, the "Three statuses,
   not five" section is the thing that re-opens; the snapshot
   schema, the score weights, and the drift differ all key off
   the status enum.

Anything else — a new repo in a manifest, a new manifest, a
weekly snapshot — is a normal cut and does not edit this doc.
