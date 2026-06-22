"""Voice lint: scan checked-in snapshots and docs for banned marketing words.

v0.1 carries a small banned set. The production banlist is governed
by spec 0003 and lives at `voice/banlist-v1.txt`.

Exit code:
- 0 if no banned tokens appear
- 1 if any are found, with file:line hits printed to stderr
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

BANNED_FAIL = (
    "seamless",
    "leverage",
    "robust",
    "world-class",
    "cutting-edge",
    "synergy",
    "delight",
    "best-in-class",
)

SCAN_GLOBS = ("reports/*.md", "docs/*.md", "STATUS.md")


def main() -> int:
    hits: list[str] = []
    files: list[Path] = []
    for glob in SCAN_GLOBS:
        if "*" in glob:
            files.extend(sorted((REPO_ROOT).glob(glob)))
        else:
            p = REPO_ROOT / glob
            if p.exists():
                files.append(p)
    for f in files:
        text = f.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), start=1):
            lower = line.lower()
            for word in BANNED_FAIL:
                if re.search(rf"\b{re.escape(word)}\b", lower):
                    hits.append(f"{f.relative_to(REPO_ROOT)}:{i}: banned word {word!r}")
    if hits:
        for h in hits:
            print(h, file=sys.stderr)
        return 1
    print(f"voice_lint: {len(files)} files scanned, no banned tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
