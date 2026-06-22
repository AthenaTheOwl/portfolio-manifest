from __future__ import annotations

from pathlib import Path

import click

from portfolio_manifest.manifest import load_manifest
from portfolio_manifest.report import render_markdown
from portfolio_manifest.snapshot import build_snapshot


@click.group()
def main() -> None:
    """Portfolio Manifest CLI."""


@main.command("validate")
@click.option(
    "--manifest",
    "manifest_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def validate_cmd(manifest_path: Path) -> None:
    load_manifest(manifest_path)
    click.echo("validate: ok")


@main.command("audit")
@click.option(
    "--manifest",
    "manifest_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--out",
    "out_path",
    required=True,
    type=click.Path(dir_okay=False, path_type=Path),
)
@click.option("--iso-week", "iso_week", required=True)
def audit_cmd(manifest_path: Path, out_path: Path, iso_week: str) -> None:
    manifest = load_manifest(manifest_path)
    snapshot = build_snapshot(manifest, iso_week)
    body = render_markdown(snapshot)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    for repo in snapshot["repos"]:
        click.echo(f"{repo['name']}: drift_score={repo['drift_score']}")


if __name__ == "__main__":
    main()
