"""List all projects in a Linear workspace for picker prompts."""

import click

import bootstrap  # noqa: F401
from linear_client import list_projects, require_env


@click.command()
@click.option("--api-key-env", required=True)
def main(api_key_env: str):
    api_key = require_env(api_key_env)
    for project in list_projects(api_key):
        teams = ", ".join(t["name"] for t in project["teams"]["nodes"])
        click.echo(f"{project['name']} | {teams}")


if __name__ == "__main__":
    main()
