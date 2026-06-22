from __future__ import annotations

from datetime import date

from click.testing import CliRunner

from portfolio_manifest.checks import decision_freshness
from portfolio_manifest.cli import main


def test_validate_succeeds_on_example(example_manifest_path):
    runner = CliRunner()
    result = runner.invoke(main, ["validate", "--manifest", str(example_manifest_path)])
    assert result.exit_code == 0, result.output
    assert "validate: ok" in result.output


def test_audit_writes_snapshot(example_manifest_path, tmp_path, monkeypatch):
    monkeypatch.setattr(decision_freshness, "TODAY_OVERRIDE", date(2026, 6, 22))
    out = tmp_path / "snapshot.md"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "audit",
            "--manifest",
            str(example_manifest_path),
            "--out",
            str(out),
            "--iso-week",
            "2026-W34",
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.exists()
    body = out.read_text(encoding="utf-8")
    assert "Portfolio health — 2026-W34" in body
    assert "drift_score" in result.output
