from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

TODAY_OVERRIDE: date | None = None


def _today() -> date:
    return TODAY_OVERRIDE if TODAY_OVERRIDE is not None else date.today()


def run(repo_path: Path, repo: Any, contracts: dict[str, Any]) -> dict[str, Any]:
    declared = repo.declared_contracts.get("decision-freshness", {})
    current = declared.get("version", "")
    max_age_days = int(contracts.get("decision_freshness", {}).get("max_age_days", 90))
    expected = f"<= {max_age_days} days"

    try:
        as_of = date.fromisoformat(current)
    except (ValueError, TypeError):
        return {
            "contract": "decision-freshness",
            "status": "warn",
            "current": current,
            "expected": expected,
            "current_version": current,
            "expected_version": expected,
            "notes": "could not parse decision-freshness version as ISO date",
        }

    age = (_today() - as_of).days
    if age <= max_age_days:
        return {
            "contract": "decision-freshness",
            "status": "pass",
            "current": current,
            "expected": expected,
            "current_version": current,
            "expected_version": expected,
            "notes": "",
        }
    return {
        "contract": "decision-freshness",
        "status": "fail",
        "current": current,
        "expected": expected,
        "current_version": current,
        "expected_version": expected,
        "days_behind": age - max_age_days,
        "notes": "",
    }
