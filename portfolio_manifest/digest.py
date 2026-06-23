"""read the committed weekly snapshot report and turn it back into structured rows.

the audit command writes a markdown report under reports/. the show verb reads
that same committed file (offline, read-only) and reconstructs a small ranked
view so a reader sees the worst repos and the real findings without opening the
raw markdown or re-running the audit.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports"

# a check row is signal only if it is not one of the skeleton placeholders.
# the skeleton checks emit a fixed "skeleton, not yet implemented" note.
_SKELETON_MARK = "skeleton, not yet implemented"


@dataclass
class CheckRow:
    contract: str
    status: str
    current: str
    expected: str
    days_behind: str
    notes: str

    @property
    def is_skeleton(self) -> bool:
        return _SKELETON_MARK in self.notes

    @property
    def is_signal(self) -> bool:
        return self.status in ("warn", "fail") and not self.is_skeleton


@dataclass
class RepoBlock:
    name: str
    drift_score: int
    checks: list[CheckRow] = field(default_factory=list)

    @property
    def failing(self) -> list[CheckRow]:
        return [c for c in self.checks if c.status == "fail"]

    @property
    def signal_findings(self) -> list[CheckRow]:
        return [c for c in self.checks if c.is_signal]


@dataclass
class Digest:
    manifest_id: str
    iso_week: str
    generated_at: str
    drift_total: int
    repos: list[RepoBlock]

    @property
    def ranked(self) -> list[RepoBlock]:
        return sorted(self.repos, key=lambda r: r.drift_score, reverse=True)


_FRONTMATTER_KEYS = ("manifest_id", "iso_week", "generated_at", "drift_total")
_HEADING_RE = re.compile(r"^##\s+(?P<name>[^\n]+?)\s*$")
_DRIFT_RE = re.compile(r"^Drift score:\s+\*\*(?P<score>\d+)\*\*\s*$")
_ROW_RE = re.compile(r"^\|(?P<body>.+)\|\s*$")


def latest_report_path() -> Path | None:
    if not REPORTS_DIR.is_dir():
        return None
    reports = sorted(REPORTS_DIR.glob("*.md"))
    return reports[-1] if reports else None


def _parse_frontmatter(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    if end == -1:
        return out
    block = text[3:end]
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        if key in _FRONTMATTER_KEYS:
            out[key] = val.strip()
    return out


def _split_cells(body: str) -> list[str]:
    return [c.strip() for c in body.split("|")]


def parse_report(path: str | Path) -> Digest:
    text = Path(path).read_text(encoding="utf-8")
    fm = _parse_frontmatter(text)

    repos: list[RepoBlock] = []
    current: RepoBlock | None = None
    skip_section = False  # for "## Reading the row" prose section

    for line in text.splitlines():
        h = _HEADING_RE.match(line)
        if h:
            name = h.group("name")
            # the report ends with a "## Reading the row" prose section; not a repo.
            if name.lower().startswith("reading the row"):
                current = None
                skip_section = True
                continue
            skip_section = False
            current = RepoBlock(name=name, drift_score=0)
            repos.append(current)
            continue
        if skip_section or current is None:
            continue
        d = _DRIFT_RE.match(line)
        if d:
            current.drift_score = int(d.group("score"))
            continue
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        cells = _split_cells(m.group("body"))
        if len(cells) < 6:
            continue
        contract = cells[0]
        # skip the header row and the separator row.
        if contract.lower() == "contract" or set(contract) <= {"-", ":"}:
            continue
        current.checks.append(
            CheckRow(
                contract=contract,
                status=cells[1],
                current=cells[2],
                expected=cells[3],
                days_behind=cells[4],
                notes=cells[5],
            )
        )

    drift_total = int(fm.get("drift_total", "0") or 0)
    return Digest(
        manifest_id=fm.get("manifest_id", "?"),
        iso_week=fm.get("iso_week", "?"),
        generated_at=fm.get("generated_at", "?"),
        drift_total=drift_total,
        repos=repos,
    )


def _bar(score: int, worst: int, width: int = 12) -> str:
    if worst <= 0:
        return ""
    filled = round(width * score / worst)
    return "#" * filled + "." * (width - filled)


def render_show(digest: Digest) -> str:
    """ranked, readable plaintext: a table plus one headline finding."""
    lines: list[str] = []
    lines.append(f"portfolio health -- {digest.iso_week}  (manifest: {digest.manifest_id})")
    lines.append(f"generated {digest.generated_at}  |  {len(digest.repos)} repos  |  total drift {digest.drift_total}")
    lines.append("")

    ranked = digest.ranked
    worst = ranked[0].drift_score if ranked else 0
    name_w = max((len(r.name) for r in ranked), default=4)
    name_w = max(name_w, 4)

    lines.append(f"  {'#':>2}  {'repo':<{name_w}}  {'drift':>5}  {'signal':>6}  bar")
    lines.append(f"  {'-'*2}  {'-'*name_w}  {'-'*5}  {'-'*6}  {'-'*12}")
    for i, r in enumerate(ranked, 1):
        sig = len(r.signal_findings)
        lines.append(
            f"  {i:>2}  {r.name:<{name_w}}  {r.drift_score:>5}  {sig:>6}  {_bar(r.drift_score, worst)}"
        )
    lines.append("")

    # headline: the real findings (non-skeleton warn/fail), worst repo first.
    findings: list[tuple[RepoBlock, CheckRow]] = []
    for r in ranked:
        for c in r.signal_findings:
            findings.append((r, c))

    if findings:
        lines.append(f"real findings ({len(findings)}):")
        for r, c in findings:
            detail = c.notes.strip() or f"{c.current} (expected {c.expected})"
            behind = f"  [{c.days_behind} days behind]" if c.days_behind and c.days_behind != "-" else ""
            lines.append(f"  - {r.name} | {c.contract} | {c.status}: {detail}{behind}")
        lines.append("")
        top_repo, top_check = findings[0]
        lines.append(
            f"headline: {top_repo.name} carries the most drift ({top_repo.drift_score}); "
            f"its sharpest signal is {top_check.contract} ({top_check.status})."
        )
    else:
        lines.append("real findings (0): every non-skeleton check is passing.")
        lines.append(f"headline: no actionable drift across {len(digest.repos)} repos this week.")

    skeleton_warns = sum(
        1 for r in digest.repos for c in r.checks if c.is_skeleton and c.status == "warn"
    )
    if skeleton_warns:
        lines.append(
            f"note: {skeleton_warns} of the warnings are skeleton placeholders (not signal)."
        )

    return "\n".join(lines)


def build_show_text() -> tuple[str, Path | None]:
    path = latest_report_path()
    if path is None:
        return ("", None)
    return (render_show(parse_report(path)), path)


__all__ = [
    "CheckRow",
    "RepoBlock",
    "Digest",
    "latest_report_path",
    "parse_report",
    "render_show",
    "build_show_text",
]
