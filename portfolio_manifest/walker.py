from __future__ import annotations

from pathlib import Path


def ensure_local(repo) -> Path:
    if getattr(repo, "fixture_path", None):
        return Path(repo.fixture_path)
    return Path(repo.name)
