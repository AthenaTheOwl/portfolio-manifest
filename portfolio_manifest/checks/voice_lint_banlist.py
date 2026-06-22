from __future__ import annotations

from pathlib import Path
from typing import Any


def run(repo_path: Path, repo: Any, contracts: dict[str, Any]) -> dict[str, Any]:
    declared = repo.declared_contracts.get("voice-lint-banlist", {})
    current = declared.get("version", "")
    expected = contracts.get("voice_lint_banlist", {}).get("sha256", "")

    if current == expected:
        return {
            "contract": "voice-lint-banlist",
            "status": "pass",
            "current": current,
            "expected": expected,
            "current_version": current,
            "expected_version": expected,
            "notes": "",
        }
    return {
        "contract": "voice-lint-banlist",
        "status": "fail",
        "current": current,
        "expected": expected,
        "current_version": current,
        "expected_version": expected,
        "notes": "banlist hash drift: repo is using a banlist that does not match the manifest",
    }
