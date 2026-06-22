from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import validate

SUPPORTED_CONTRACTS = (
    "decision-schema",
    "spec-schema",
    "dream-schema",
    "voice-lint-banlist",
    "eval-coverage",
    "decision-freshness",
)


@dataclass
class RepoEntry:
    name: str
    clone_url: str
    branch: str
    declared_contracts: dict[str, dict[str, Any]]
    fixture_path: str | None = None
    last_audited_at: str | None = None


@dataclass
class Manifest:
    id: str
    owner: str
    schedule: str
    contracts: dict[str, dict[str, Any]]
    repos: list[RepoEntry]

    @property
    def repo_names(self) -> list[str]:
        return [r.name for r in self.repos]


_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "manifest.schema.json"


def load_manifest(path: str | Path) -> Manifest:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    validate(instance=data, schema=schema)
    repos = [
        RepoEntry(
            name=r["name"],
            clone_url=r["clone_url"],
            branch=r["branch"],
            declared_contracts=r["declared_contracts"],
            fixture_path=r.get("fixture_path"),
            last_audited_at=r.get("last_audited_at"),
        )
        for r in data["repos"]
    ]
    return Manifest(
        id=data["id"],
        owner=data["owner"],
        schedule=data["schedule"],
        contracts=data["contracts"],
        repos=repos,
    )
