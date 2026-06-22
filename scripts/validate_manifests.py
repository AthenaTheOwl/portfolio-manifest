"""Validate every manifest under manifests/ parses against the manifest schema
and that every declared contract resolves to a check module on disk.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from portfolio_manifest.checks import load  # noqa: E402
from portfolio_manifest.manifest import SUPPORTED_CONTRACTS, load_manifest  # noqa: E402

MANIFESTS = REPO_ROOT / "manifests"


def main() -> int:
    files = sorted(MANIFESTS.glob("*.yaml")) + sorted(MANIFESTS.glob("*.yml"))
    if not files:
        print("no manifests found under manifests/", file=sys.stderr)
        return 1
    for f in files:
        try:
            m = load_manifest(f)
        except Exception as exc:
            print(f"{f.name}: invalid ({exc})", file=sys.stderr)
            return 1
        for repo in m.repos:
            for contract in repo.declared_contracts:
                if contract not in SUPPORTED_CONTRACTS:
                    print(f"{f.name}: {repo.name} declares unsupported contract {contract}", file=sys.stderr)
                    return 1
                try:
                    load(contract)
                except Exception as exc:
                    print(f"{f.name}: {repo.name}: cannot import check for {contract} ({exc})", file=sys.stderr)
                    return 1
        print(f"{f.name}: ok ({len(m.repos)} repos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
