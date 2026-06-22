from __future__ import annotations

from typing import Iterable, Mapping

WEIGHTS: dict[str, int] = {"pass": 0, "warn": 1, "fail": 3}


def compute_drift_score(results: Iterable[Mapping[str, object]]) -> int:
    return sum(WEIGHTS.get(str(r.get("status", "pass")), 0) for r in results)
