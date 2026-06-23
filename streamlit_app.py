"""portfolio-manifest -- live demo (Streamlit Community Cloud).

reads the committed weekly snapshot under reports/*.md and shows cross-repo
health: which repos carry the most contract drift, and which findings are real
signal versus skeleton placeholders. no network, no secrets -- runs entirely
off the committed report.

deploy: Streamlit Community Cloud -> New app -> repo AthenaTheOwl/portfolio-manifest,
branch main, main file streamlit_app.py.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from portfolio_manifest.digest import latest_report_path, parse_report

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
