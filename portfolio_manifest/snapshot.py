from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from portfolio_manifest.checks import run_all
from portfolio_manifest.drift import attach_drift_events
from portfolio_manifest.manifest import Manifest
from portfolio_manifest.report import render_markdown
from portfolio_manifest.score import compute_drift_score
from portfolio_manifest.walker import ensure_local


def build_snapshot(
    manifest: Manifest,
    iso_week: str,
    previous: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repos: list[dict[str, Any]] = []
    for repo in manifest.repos:
        local_path = ensure_local(repo)
        results = run_all(local_path, repo, manifest.contracts)
        repos.append(
            {
                "name": repo.name,
                "drift_score": compute_drift_score(results),
                "check_results": results,
            }
        )
    snapshot = {
        "manifest_id": manifest.id,
        "iso_week": iso_week,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repos": repos,
    }
    if previous is not None:
        attach_drift_events(snapshot, previous)
    return snapshot


__all__ = ["build_snapshot", "compute_drift_score", "render_markdown"]
