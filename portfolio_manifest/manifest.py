from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import ValidationError, validate

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


class ManifestError(Exception):
    """A manifest could not be read, parsed, or validated.

    Carries a one-line, actionable message so callers can report the bad
    input without exposing a parser/validator traceback to the user.
    """


def load_manifest(path: str | Path) -> Manifest:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        raise ManifestError(f"{path}: cannot read manifest: {err.strerror or err}") from err

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as err:
        # yaml attaches the offending line/column on problem_mark for mapping errors.
        mark = getattr(err, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise ManifestError(f"{path}: not valid YAML{where}") from err

    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    try:
        validate(instance=data, schema=schema)
    except ValidationError as err:
        # err.message is the single failing rule; err.json_path locates it in the doc.
        raise ManifestError(
            f"{path}: does not match manifest schema at {err.json_path}: {err.message}"
        ) from err
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
