"""Check that target Linear workspace has all mapped state names."""

import json
from pathlib import Path

import click

import bootstrap  # noqa: F401
from linear_client import require_env, resolve_by_name, resolve_states


@click.command()
@click.option("--target-api-key-env", required=True)
@click.option("--target-team", required=True)
@click.option(
    "--state-map",
    required=True,
    type=click.Path(exists=True),
    help="JSON file mapping Trello list names to Linear state names",
)
def main(target_api_key_env: str, target_team: str, state_map: str):
    api_key = require_env(target_api_key_env)
    mapped_states = set(json.loads(Path(state_map).read_text()).values())
    team_id = resolve_by_name(api_key, "teams", target_team)
    target_states = resolve_states(api_key, team_id)
    missing = mapped_states - set(target_states)

    report(mapped_states, target_states, missing)

    if missing:
        raise SystemExit(1)


def report(mapped: set, target: dict, missing: set):
    click.echo("Mapped states:")
    for name in sorted(mapped):
        marker = "✗" if name in missing else "✓"
        click.echo(f"  {marker} {name}")

    if not missing:
        click.echo("\nPASS: all mapped states exist in target")
        return

    click.echo(f"\nFAIL: {len(missing)} mapped state(s) missing from target:")
    for name in sorted(missing):
        click.echo(f"  - {name}")
    click.echo("\nTarget has:")
    for name in sorted(target):
        click.echo(f"  {name} ({target[name]['type']})")


if __name__ == "__main__":
    main()
