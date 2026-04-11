"""Create or update the target Linear project from exported project.json."""

import json
from pathlib import Path

import click

import _bootstrap  # noqa: F401
from linear_client import (
    create_project,
    list_projects,
    require_env,
    resolve_by_name,
    update_project,
)


@click.command()
@click.option("--api-key-env", required=True)
@click.option("--team", required=True)
@click.option("--project", required=True)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
def main(api_key_env: str, team: str, project: str, export_dir: str):
    api_key = require_env(api_key_env)
    info = json.loads((Path(export_dir) / "project.json").read_text())
    team_id = resolve_by_name(api_key, "teams", team)

    existing_id = find_project_id(api_key, project)
    if existing_id:
        update_project(
            api_key,
            existing_id,
            description=info.get("summary", ""),
            content=info.get("description", ""),
        )
        click.echo(f"Updated project: {project}")
    else:
        new_id = create_project(
            api_key,
            team_id,
            name=project,
            description=info.get("summary", ""),
            content=info.get("description", ""),
        )
        click.echo(f"Created project: {project} ({new_id})")


def find_project_id(api_key: str, name: str) -> str | None:
    match = next((p for p in list_projects(api_key) if p["name"] == name), None)
    return match["id"] if match else None


if __name__ == "__main__":
    main()
