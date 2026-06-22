"""Validate decision records under decisions/.

Each file must:
- be named DEC-PM-NNN-<slug>.md
- start with a level-1 heading containing the DEC ID
- include a `Status:` line, a `Date:` line, and a `Spec:` line in
  the bullet metadata.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DECISIONS = REPO_ROOT / "decisions"

NAME_RE = re.compile(r"^DEC-PM-(\d{3})-[a-z0-9-]+\.md$")
HEADING_RE = re.compile(r"^# DEC-PM-\d{3} —")
REQUIRED_BULLETS = ("Status:", "Date:", "Spec:")


def main() -> int:
    if not DECISIONS.exists():
        print("decisions/ directory missing", file=sys.stderr)
        return 1
    files = sorted(DECISIONS.glob("DEC-PM-*.md"))
    if not files:
        print("no decision files found", file=sys.stderr)
        return 1
    seen: set[str] = set()
    for f in files:
        m = NAME_RE.match(f.name)
        if not m:
            print(f"{f.name}: filename does not match DEC-PM-NNN-<slug>.md", file=sys.stderr)
            return 1
        if m.group(1) in seen:
            print(f"{f.name}: duplicate DEC number", file=sys.stderr)
            return 1
        seen.add(m.group(1))
        body = f.read_text(encoding="utf-8")
        lines = body.splitlines()
        if not lines or not HEADING_RE.match(lines[0]):
            print(f"{f.name}: first line must be '# DEC-PM-NNN — Title'", file=sys.stderr)
            return 1
        for bullet in REQUIRED_BULLETS:
            if not any(bullet in line for line in lines[:15]):
                print(f"{f.name}: missing required metadata bullet {bullet!r}", file=sys.stderr)
                return 1
        print(f"{f.name}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
