"""Check that target workspace has all source workflow states."""

import json
from pathlib import Path

import click
from linear_api import graphql, require_env, resolve_by_name


@click.command()
@click.option("--target-api-key-env", required=True)
@click.option("--target-team", required=True)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
def main(target_api_key_env: str, target_team: str, export_dir: str):
    api_key = require_env(target_api_key_env)
    source_states = load_source_states(Path(export_dir))
    target_states = fetch_target_states(api_key, target_team)

    source_names = {s["name"] for s in source_states}
    target_names = {s["name"] for s in target_states}
    missing = source_names - target_names

    report(source_states, target_states, missing)

    if missing:
        raise SystemExit(1)


def load_source_states(export_dir: Path) -> list:
    path = export_dir / "states.json"
    if not path.exists():
        raise click.ClickException("states.json not found — run export first")
    return json.loads(path.read_text())


def fetch_target_states(api_key: str, team: str) -> list:
    team_id = resolve_by_name(api_key, "teams", team)
    query = f"""{{ workflowStates(filter: {{ team: {{ id: {{ eq: "{team_id}" }} }} }}) {{
        nodes {{ name type }}
    }} }}"""
    return graphql(api_key, query)["data"]["workflowStates"]["nodes"]


def report(source: list, target: list, missing: set):
    click.echo("Source states:")
    for s in sorted(source, key=lambda x: x["name"]):
        marker = "✗" if s["name"] in missing else "✓"
        click.echo(f"  {marker} {s['name']} ({s['type']})")

    if not missing:
        click.echo("\nPASS: all source states exist in target")
        return

    click.echo(f"\nFAIL: {len(missing)} source state(s) missing from target:")
    for name in sorted(missing):
        click.echo(f"  - {name}")
    click.echo("\nTarget has:")
    for s in sorted(target, key=lambda x: x["name"]):
        click.echo(f"  {s['name']} ({s['type']})")


if __name__ == "__main__":
    main()
