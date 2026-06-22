from __future__ import annotations

from datetime import date
from pathlib import Path

from portfolio_manifest.checks import load, run_all
from portfolio_manifest.checks import decision_freshness
from portfolio_manifest.manifest import SUPPORTED_CONTRACTS, load_manifest


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
