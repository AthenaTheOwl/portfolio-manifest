from __future__ import annotations

from portfolio_manifest.digest import CheckRow


def _row(status: str, notes: str) -> CheckRow:
    return CheckRow(
        contract="decision-freshness",
        status=status,
        current="",
        expected="",
        days_behind="",
        notes=notes,
    )


def test_non_skeleton_warn_is_signal():
    # a real warn (e.g. an unparseable ISO date) counts as signal, so a change
    # that drops 'warn' from is_signal must fail here.
    row = _row("warn", "could not parse decision-freshness version as ISO date")
    assert row.is_skeleton is False
    assert row.is_signal is True


def test_skeleton_warn_is_not_signal():
    row = _row("warn", "skeleton, not yet implemented")
    assert row.is_skeleton is True
    assert row.is_signal is False


def test_fail_is_signal_and_pass_is_not():
    assert _row("fail", "").is_signal is True
    assert _row("pass", "").is_signal is False
