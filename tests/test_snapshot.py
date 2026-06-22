from __future__ import annotations

from datetime import date

from portfolio_manifest.checks import decision_freshness
from portfolio_manifest.drift import attach_drift_events, diff_snapshots
from portfolio_manifest.manifest import load_manifest
from portfolio_manifest.snapshot import build_snapshot, compute_drift_score, render_markdown


def test_drift_score_computation():
    results = [
        {"status": "pass"},
        {"status": "warn"},
        {"status": "warn"},
        {"status": "fail"},
    ]
    assert compute_drift_score(results) == 1 + 1 + 3


def test_snapshot_renders_markdown(example_manifest_path, monkeypatch):
    monkeypatch.setattr(decision_freshness, "TODAY_OVERRIDE", date(2026, 6, 22))
    m = load_manifest(example_manifest_path)
    snap = build_snapshot(m, "2026-W34")
    md = render_markdown(snap)
    assert "Portfolio health" in md
    assert "athena-site" in md
    assert "dream-ledger" in md
    assert "decision-store" in md
    assert "manifest_id: example-portfolio" in md
    assert "iso_week: 2026-W34" in md


def test_drift_diff_emits_event_only_on_transition():
    previous = {
        "repos": [
            {
                "name": "r1",
                "check_results": [
                    {"contract": "decision-freshness", "status": "pass"},
                    {"contract": "voice-lint-banlist", "status": "fail"},
                ],
            }
        ]
    }
    current = {
        "repos": [
            {
                "name": "r1",
                "check_results": [
                    {"contract": "decision-freshness", "status": "fail"},
                    {"contract": "voice-lint-banlist", "status": "fail"},
                ],
            }
        ]
    }
    events = diff_snapshots(previous, current)
    assert events["r1"] == [{"contract": "decision-freshness", "from": "pass", "to": "fail"}]
    attach_drift_events(current, previous)
    assert current["repos"][0]["drift_events"] == [
        {"contract": "decision-freshness", "from": "pass", "to": "fail"}
    ]


def test_drift_diff_with_no_previous_snapshot():
    current = {"repos": [{"name": "r1", "check_results": [{"contract": "x", "status": "pass"}]}]}
    assert diff_snapshots(None, current) == {"r1": []}
