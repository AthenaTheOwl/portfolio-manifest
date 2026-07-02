from __future__ import annotations

from pathlib import Path

import click

from portfolio_manifest.digest import build_show_text
from portfolio_manifest.manifest import ManifestError, load_manifest
from portfolio_manifest.report import render_markdown
from portfolio_manifest.snapshot import build_snapshot


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "manifests" / "example.yaml"


@click.group()
def main() -> None:
    """Portfolio Manifest CLI."""


@main.command("validate")
@click.option(
    "--manifest",
    "manifest_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="defaults to the bundled manifests/example.yaml",
)
def validate_cmd(manifest_path: Path | None) -> None:
    path = manifest_path or DEFAULT_MANIFEST
    try:
        load_manifest(path)
    except ManifestError as err:
        click.echo(f"validate: {err}", err=True)
        raise SystemExit(1)
    click.echo(f"validate: ok ({path.name})")


@main.command("show")
def show_cmd() -> None:
    """print a ranked, readable view of the latest committed weekly snapshot."""
    text, path = build_show_text()
    if path is None:
        click.echo("show: no report found under reports/ — run `audit` first.", err=True)
        raise SystemExit(1)
    click.echo(text)


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
    try:
        manifest = load_manifest(manifest_path)
    except ManifestError as err:
        click.echo(f"audit: {err}", err=True)
        raise SystemExit(1)
    snapshot = build_snapshot(manifest, iso_week)
    body = render_markdown(snapshot)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8")
    for repo in snapshot["repos"]:
        click.echo(f"{repo['name']}: drift_score={repo['drift_score']}")


if __name__ == "__main__":
    main()
