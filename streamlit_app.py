"""portfolio-manifest -- live demo (Streamlit Community Cloud).

reads the committed weekly snapshot under reports/*.md and shows cross-repo
health: which repos carry the most contract drift, and which findings are real
signal versus skeleton placeholders. no network, no secrets -- runs entirely
off the committed report.

deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/portfolio-manifest,
branch main, main file streamlit_app.py.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import streamlit as st

from portfolio_manifest.checks import run_all
from portfolio_manifest.digest import latest_report_path, parse_report
from portfolio_manifest.manifest import RepoEntry
from portfolio_manifest.score import WEIGHTS, compute_drift_score

REPO = Path(__file__).resolve().parent

st.set_page_config(page_title="portfolio-manifest -- cross-repo health", layout="wide")
st.title("portfolio-manifest")
st.caption(
    "cross-repo contract health from the committed weekly snapshot: which repos "
    "carry the most drift, and which findings are real signal versus skeleton "
    "placeholders."
)

path = latest_report_path()
if path is None:
    st.warning("no report found under reports/*.md")
    st.stop()

digest = parse_report(path)
ranked = digest.ranked

signal_total = sum(len(r.signal_findings) for r in digest.repos)
fail_total = sum(len(r.failing) for r in digest.repos)

st.subheader(f"portfolio health -- {digest.iso_week}  (manifest: {digest.manifest_id})")

c1, c2, c3 = st.columns(3)
c1.metric("repos audited", len(digest.repos))
c2.metric("total drift", digest.drift_total)
c3.metric("real findings", signal_total, help="non-skeleton warn/fail checks")

only_signal = st.toggle(
    "show only repos with real findings", value=False,
    help="hide repos whose only warnings are skeleton placeholders",
)

shown = [r for r in ranked if (not only_signal or r.signal_findings)]

st.dataframe(
    [
        {
            "rank": i,
            "repo": r.name,
            "drift score": r.drift_score,
            "real findings": len(r.signal_findings),
            "failing checks": len(r.failing),
        }
        for i, r in enumerate(shown, 1)
    ],
    use_container_width=True,
    hide_index=True,
)

# headline: the real findings, worst repo first.
findings = [(r, c) for r in ranked for c in r.signal_findings]
if findings:
    top_repo, top_check = findings[0]
    behind = ""
    if top_check.days_behind and top_check.days_behind != "-":
        behind = f" ({top_check.days_behind} days behind)"
    st.info(
        f"**headline:** {top_repo.name} carries the most drift "
        f"({top_repo.drift_score}); its sharpest signal is "
        f"`{top_check.contract}` ({top_check.status}) -- "
        f"{top_check.notes.strip() or top_check.current}{behind}."
    )
else:
    st.info("**headline:** no actionable drift -- every non-skeleton check is passing.")

with st.expander("real findings across the portfolio"):
    if not findings:
        st.markdown("none -- all signal checks pass.")
    for r, c in findings:
        detail = c.notes.strip() or f"{c.current} (expected {c.expected})"
        st.markdown(f"- **{r.name}** `{c.contract}` ({c.status}): {detail}")

st.caption(
    f"source: reports/{path.name} -- generated {digest.generated_at}. "
    f"{fail_total} failing checks, {signal_total} total real findings."
)

# -------------------------------------------------------------------------
# interactive: audit a repo yourself.
#
# the table above is the committed weekly snapshot. below, you drive the REAL
# engine: portfolio_manifest.checks.run_all runs the actual contract checks
# against your declared values, and portfolio_manifest.score.compute_drift_score
# scores them -- the same functions the audit command uses. no lookup, no
# hardcoded output; edit the inputs and the drift score recomputes live.
# -------------------------------------------------------------------------

st.divider()
st.header("audit a repo yourself")
st.caption(
    "edit one repo's declared contracts and the manifest baselines, then run the "
    "real checks (`portfolio_manifest.checks.run_all`) and drift score "
    "(`compute_drift_score`) live. two checks actually compute today: "
    "voice-lint-banlist (hash must match the manifest) and decision-freshness "
    "(latest decision must be within the max age). the other four are skeleton "
    "warns by design."
)

# a clean banlist hash that matches by default; flip a char to force drift.
_CLEAN_HASH = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
_DRIFT_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

left, right = st.columns(2)

with left:
    st.markdown("**manifest baselines** (what the portfolio requires)")
    base_hash = st.text_input(
        "voice_lint_banlist.sha256 (manifest)", value=_CLEAN_HASH,
        help="the banlist hash the manifest pins every repo to.",
    )
    max_age = st.slider(
        "decision_freshness.max_age_days", min_value=7, max_value=365, value=90,
        help="a repo's latest decision must be no older than this.",
    )

with right:
    st.markdown("**your repo's declared contracts** (what the repo actually ships)")
    repo_name = st.text_input("repo name", value="my-repo")
    banlist_match = st.toggle(
        "repo's banlist matches the manifest", value=False,
        help="off = the repo ships a different banlist hash -> the check fails.",
    )
    declared_hash = base_hash if banlist_match else _DRIFT_HASH
    st.caption(f"declared banlist hash: `{declared_hash[:16]}...`")
    decided_on = st.date_input(
        "repo's latest decision date (decision-freshness.version)",
        value=date(2025, 1, 1),
        help="how old is the repo's most recent recorded decision?",
    )

# build a RepoEntry + contracts mapping exactly like load_manifest produces,
# then call the same run_all / compute_drift_score the audit command uses.
contracts = {
    "decision_schema": {"latest": "v3"},
    "spec_schema": {"latest": "v2"},
    "dream_schema": {"latest": "v1"},
    "voice_lint_banlist": {"sha256": base_hash},
    "eval_coverage": {"min_ratio": 0.70},
    "decision_freshness": {"max_age_days": max_age},
}
user_repo = RepoEntry(
    name=repo_name or "my-repo",
    clone_url="local",
    branch="main",
    declared_contracts={
        "voice-lint-banlist": {"version": declared_hash},
        "decision-freshness": {"version": decided_on.isoformat()},
    },
)

results = run_all(REPO, user_repo, contracts)
drift = compute_drift_score(results)
worst = sum(WEIGHTS["fail"] for _ in results)  # if every check failed

m1, m2, m3 = st.columns(3)
m1.metric("drift score", drift, help="0 is clean; higher is worse (warn=1, fail=3)")
m2.metric("failing checks", sum(1 for r in results if r["status"] == "fail"))
m3.metric("real (non-skeleton) checks", 2, help="voice-lint-banlist + decision-freshness")

if drift == 0:
    st.success("clean: every check passes against these baselines.")
else:
    real_fails = [
        r for r in results
        if r["status"] == "fail"
    ]
    if real_fails:
        def _why(r: dict) -> str:
            detail = r["notes"].strip() or f"{r['current']} != expected {r['expected']}"
            return f"`{r['contract']}` ({r['status']}): {detail}"

        why = "; ".join(_why(r) for r in real_fails)
        st.error(f"drift {drift} -- {why}")
    else:
        st.warning(f"drift {drift} -- only skeleton warnings, no real failures.")

st.dataframe(
    [
        {
            "contract": r["contract"],
            "status": r["status"],
            "current": str(r.get("current", "")),
            "expected": str(r.get("expected", "")),
            "weight": WEIGHTS.get(r["status"], 0),
            "notes": r.get("notes", "").strip() or "-",
        }
        for r in results
    ],
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "this drives the real checks: toggle the banlist match on and fix the decision "
    "date to within the max age, and drift falls to 0 -- the same result the audit "
    "command would write to a report."
)
