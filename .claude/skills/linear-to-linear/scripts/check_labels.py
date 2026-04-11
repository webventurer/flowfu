"""Check that target workspace has all source labels, create missing ones."""

import json
from pathlib import Path

import click

from linear_client import LinearError, create_label, list_labels, require_env


@click.command()
@click.option("--target-api-key-env", required=True)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
@click.option(
    "--create", is_flag=True, default=False, help="Create missing labels"
)
def main(target_api_key_env: str, export_dir: str, create: bool):
    api_key = require_env(target_api_key_env)
    source_labels = load_source_labels(Path(export_dir))
    target_labels = list_labels(api_key)

    source_names = {label["name"] for label in source_labels}
    target_names = {label["name"] for label in target_labels}
    missing = source_names - target_names

    report(source_labels, missing)

    if missing and create:
        create_missing(api_key, source_labels, missing)
    elif missing:
        click.echo("\nRun with --create to add missing labels")
        raise SystemExit(1)


def load_source_labels(export_dir: Path) -> list:
    path = export_dir / "labels.json"
    if path.exists():
        return json.loads(path.read_text())
    cards = json.loads((export_dir / "all_cards.json").read_text())
    seen = {}
    for card in cards:
        for name in card.get("labels", []):
            seen[name] = True
    return [{"name": name, "color": ""} for name in seen]


def report(source_labels: list, missing: set):
    click.echo("Source labels:")
    for label in sorted(source_labels, key=lambda x: x["name"]):
        marker = "✗" if label["name"] in missing else "✓"
        click.echo(f"  {marker} {label['name']}")

    if not missing:
        click.echo("\nPASS: all source labels exist in target")


def create_missing(api_key: str, source_labels: list, missing: set):
    click.echo(f"\nCreating {len(missing)} missing labels...")
    source_by_name = {label["name"]: label for label in source_labels}
    for name in sorted(missing):
        color = source_by_name[name].get("color") or None
        create_one_label(api_key, name, color)


def create_one_label(api_key: str, name: str, color: str | None):
    try:
        create_label(api_key, name=name, color=color)
        click.echo(f"  ✓ {name}")
    except LinearError as e:
        click.echo(f"  ✗ {name} — {e}")


if __name__ == "__main__":
    main()
