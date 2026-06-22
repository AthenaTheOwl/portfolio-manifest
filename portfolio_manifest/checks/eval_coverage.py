from __future__ import annotations

from pathlib import Path
from typing import Any


def run(repo_path: Path, repo: Any, contracts: dict[str, Any]) -> dict[str, Any]:
    declared = repo.declared_contracts.get("eval-coverage", {})
    current = declared.get("version", "")
    min_ratio = contracts.get("eval_coverage", {}).get("min_ratio", "")
    expected = str(min_ratio)
    return {
        "contract": "eval-coverage",
        "status": "warn",
        "current": current,
        "expected": expected,
        "current_version": current,
        "expected_version": expected,
        "notes": "skeleton, not yet implemented (R-PM-013)",
    }
