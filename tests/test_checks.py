from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from portfolio_manifest.checks import load, run_all
from portfolio_manifest.checks import decision_freshness
from portfolio_manifest.manifest import SUPPORTED_CONTRACTS, load_manifest


@dataclass
class _FakeRepo:
    declared_contracts: dict[str, dict[str, Any]]


def test_every_supported_contract_loads():
    for contract in SUPPORTED_CONTRACTS:
        run = load(contract)
        assert callable(run)


def test_skeleton_checks_return_warn(example_manifest_path, tmp_path):
    m = load_manifest(example_manifest_path)
    repo = m.repos[0]
    results = {
        r["contract"]: r
        for r in run_all(tmp_path, repo, m.contracts)
    }
    for skeleton in ("decision-schema", "spec-schema", "dream-schema", "eval-coverage"):
        assert results[skeleton]["status"] == "warn"


def test_voice_lint_banlist_pass_and_fail(example_manifest_path, tmp_path):
    m = load_manifest(example_manifest_path)
    results_by_repo = {
        repo.name: {r["contract"]: r for r in run_all(tmp_path, repo, m.contracts)}
        for repo in m.repos
    }
    assert results_by_repo["athena-site"]["voice-lint-banlist"]["status"] == "pass"
    assert results_by_repo["dream-ledger"]["voice-lint-banlist"]["status"] == "pass"
    assert results_by_repo["decision-store"]["voice-lint-banlist"]["status"] == "fail"


def test_decision_freshness_thresholds(example_manifest_path, tmp_path, monkeypatch):
    monkeypatch.setattr(decision_freshness, "TODAY_OVERRIDE", date(2026, 6, 22))
    m = load_manifest(example_manifest_path)
    results_by_repo = {
        repo.name: {r["contract"]: r for r in run_all(tmp_path, repo, m.contracts)}
        for repo in m.repos
    }
    assert results_by_repo["athena-site"]["decision-freshness"]["status"] == "pass"
    assert results_by_repo["decision-store"]["decision-freshness"]["status"] == "pass"
    assert results_by_repo["dream-ledger"]["decision-freshness"]["status"] == "fail"
    assert results_by_repo["dream-ledger"]["decision-freshness"]["days_behind"] >= 1


def _freshness_status_at_age(age_days: int, tmp_path: Path) -> dict[str, Any]:
    today = date(2026, 6, 22)
    as_of = today - timedelta(days=age_days)
    repo = _FakeRepo(
        declared_contracts={"decision-freshness": {"version": as_of.isoformat()}}
    )
    contracts = {"decision_freshness": {"max_age_days": 90}}
    prev = decision_freshness.TODAY_OVERRIDE
    decision_freshness.TODAY_OVERRIDE = today
    try:
        return decision_freshness.run(tmp_path, repo, contracts)
    finally:
        decision_freshness.TODAY_OVERRIDE = prev


def test_decision_freshness_at_exact_max_age_passes(tmp_path):
    # pin the inclusive boundary: age == max_age_days (90) must be 'pass'.
    result = _freshness_status_at_age(90, tmp_path)
    assert result["status"] == "pass"
    assert "days_behind" not in result


def test_decision_freshness_one_day_over_max_age_fails(tmp_path):
    # one day past the boundary (91 > 90) must be 'fail' with days_behind == 1.
    result = _freshness_status_at_age(91, tmp_path)
    assert result["status"] == "fail"
    assert result["days_behind"] == 1
