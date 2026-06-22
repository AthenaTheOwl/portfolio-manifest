from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_run(snapshot: dict[str, Any], ledger_path: Path, run_id: str | None = None) -> None:
    ledger_path = Path(ledger_path)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    rid = run_id or f"{snapshot['iso_week']}-001"
    with ledger_path.open("a", encoding="utf-8") as f:
        for repo in snapshot.get("repos", []):
            row = {
                "run_id": rid,
                "manifest_id": snapshot["manifest_id"],
                "iso_week": snapshot["iso_week"],
                "generated_at": snapshot.get("generated_at"),
                "repo": repo["name"],
                "drift_score": repo["drift_score"],
                "check_results": repo["check_results"],
            }
            f.write(json.dumps(row) + "\n")
