"""Fetch all issues in a target Linear project to JSON for match.py."""

import json
from pathlib import Path

import click

from linear_client import list_issues, require_env, resolve_by_name


@click.command()
@click.option("--api-key-env", required=True)
@click.option("--team", required=True)
@click.option("--project", required=True)
@click.option("--output", required=True, type=click.Path())
def main(api_key_env: str, team: str, project: str, output: str):
    api_key = require_env(api_key_env)
    project_id = resolve_by_name(api_key, "projects", project)
    issues = list_issues(api_key, project_id=project_id)
    Path(output).write_text(json.dumps(issues, indent=2))
    click.echo(f"Fetched {len(issues)} target issues to {output}")


if __name__ == "__main__":
    main()
