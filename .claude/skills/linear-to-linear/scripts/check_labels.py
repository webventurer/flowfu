"""Check that target workspace has all source labels, create missing ones."""

import json
from pathlib import Path

import click
from linear_api import graphql, require_env


@click.command()
@click.option("--target-api-key-env", required=True)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
@click.option("--create", is_flag=True, default=False, help="Create missing labels")
def main(target_api_key_env: str, export_dir: str, create: bool):
    api_key = require_env(target_api_key_env)
    source_labels = load_source_labels(Path(export_dir))
    target_labels = fetch_target_labels(api_key)

    source_names = {l["name"] for l in source_labels}
    target_names = {l["name"] for l in target_labels}
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


def fetch_target_labels(api_key: str) -> list:
    query = """{ issueLabels { nodes { name color } } }"""
    return graphql(api_key, query)["data"]["issueLabels"]["nodes"]


def report(source_labels: list, missing: set):
    click.echo("Source labels:")
    for l in sorted(source_labels, key=lambda x: x["name"]):
        marker = "✗" if l["name"] in missing else "✓"
        click.echo(f"  {marker} {l['name']}")

    if not missing:
        click.echo("\nPASS: all source labels exist in target")


def create_missing(api_key: str, source_labels: list, missing: set):
    click.echo(f"\nCreating {len(missing)} missing labels...")
    source_by_name = {l["name"]: l for l in source_labels}
    for name in sorted(missing):
        color = source_by_name[name].get("color", "")
        create_label(api_key, name, color)


def create_label(api_key: str, name: str, color: str):
    mutation = """mutation($input: IssueLabelCreateInput!) {
        issueLabelCreate(input: $input) { success issueLabel { id name } }
    }"""
    label_input = {"name": name}
    if color:
        label_input["color"] = color
    result = graphql(api_key, mutation, variables={"input": label_input})
    success = result.get("data", {}).get("issueLabelCreate", {}).get("success", False)
    click.echo(f"  {'✓' if success else '✗'} {name}")


if __name__ == "__main__":
    main()
