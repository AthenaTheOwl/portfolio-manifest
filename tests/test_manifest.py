from __future__ import annotations

import pytest

from portfolio_manifest.manifest import (
    SUPPORTED_CONTRACTS,
    ManifestError,
    load_manifest,
)


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


def test_malformed_yaml_raises_manifest_error(tmp_path):
    bad = tmp_path / "garbage.yaml"
    bad.write_text("this: [is, : garbage", encoding="utf-8")
    with pytest.raises(ManifestError) as exc:
        load_manifest(bad)
    assert "not valid YAML" in str(exc.value)


def test_schema_incomplete_manifest_raises_manifest_error(tmp_path):
    incomplete = tmp_path / "incomplete.yaml"
    incomplete.write_text("id: x\nowner: y\n", encoding="utf-8")
    with pytest.raises(ManifestError) as exc:
        load_manifest(incomplete)
    assert "does not match manifest schema" in str(exc.value)
