from __future__ import annotations

from portfolio_manifest.manifest import SUPPORTED_CONTRACTS, load_manifest


def test_example_manifest_loads(example_manifest_path):
    m = load_manifest(example_manifest_path)
    assert m.id == "example-portfolio"
    assert m.owner == "vignesh"
    assert m.schedule == "weekly"
    assert len(m.repos) == 3
    names = m.repo_names
    assert "athena-site" in names
    assert "dream-ledger" in names
    assert "decision-store" in names


def test_every_declared_contract_is_supported(example_manifest_path):
    m = load_manifest(example_manifest_path)
    for repo in m.repos:
        for contract in repo.declared_contracts:
            assert contract in SUPPORTED_CONTRACTS, f"{repo.name}: {contract}"
