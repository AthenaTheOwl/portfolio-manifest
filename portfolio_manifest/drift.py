from __future__ import annotations

from typing import Any


def _by_name(snap: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["name"]: r for r in snap.get("repos", [])}


def _by_contract(repo: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {r["contract"]: r for r in repo.get("check_results", [])}


def diff_snapshots(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    events: dict[str, list[dict[str, str]]] = {}
    if previous is None:
        for repo in current.get("repos", []):
            events[repo["name"]] = []
        return events

    prev_by_name = _by_name(previous)
    for repo in current.get("repos", []):
        prev_repo = prev_by_name.get(repo["name"])
        if prev_repo is None:
            events[repo["name"]] = []
            continue
        prev_contracts = _by_contract(prev_repo)
        repo_events: list[dict[str, str]] = []
        for r in repo.get("check_results", []):
            prev = prev_contracts.get(r["contract"])
            if prev is None:
                continue
            if prev["status"] != r["status"]:
                repo_events.append(
                    {
                        "contract": r["contract"],
                        "from": prev["status"],
                        "to": r["status"],
                    }
                )
        events[repo["name"]] = repo_events
    return events


def attach_drift_events(current: dict[str, Any], previous: dict[str, Any] | None) -> None:
    events = diff_snapshots(previous, current)
    for repo in current.get("repos", []):
        repo["drift_events"] = events.get(repo["name"], [])
