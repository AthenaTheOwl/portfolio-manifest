"""Validate every JSON file under schemas/ is a parseable Draft 2020-12 schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = REPO_ROOT / "schemas"


def main() -> int:
    files = sorted(SCHEMAS.glob("*.schema.json"))
    if not files:
        print("no schema files found under schemas/", file=sys.stderr)
        return 1
    for f in files:
        try:
            schema = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"{f.name}: not valid JSON ({exc})", file=sys.stderr)
            return 1
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            print(f"{f.name}: not a valid Draft 2020-12 schema ({exc})", file=sys.stderr)
            return 1
        print(f"{f.name}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
