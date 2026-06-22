from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Callable

_CONTRACT_TO_MODULE: dict[str, str] = {
    "decision-schema": "decision_schema",
    "spec-schema": "spec_schema",
    "dream-schema": "dream_schema",
    "voice-lint-banlist": "voice_lint_banlist",
    "eval-coverage": "eval_coverage",
    "decision-freshness": "decision_freshness",
}


def load(contract: str) -> Callable[..., dict[str, Any]]:
    module_name = _CONTRACT_TO_MODULE[contract]
    module = importlib.import_module(f"portfolio_manifest.checks.{module_name}")
    return module.run


def run_all(
    repo_path: Path,
    repo: Any,
    contracts: dict[str, Any],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for contract in _CONTRACT_TO_MODULE:
        run = load(contract)
        results.append(run(repo_path, repo, contracts))
    return results


from portfolio_manifest.checks import decision_freshness  # noqa: E402,F401

__all__ = ["load", "run_all", "decision_freshness"]
