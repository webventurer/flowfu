"""List all projects in a Linear workspace for picker prompts."""

import click
from linear_api import graphql, require_env


@click.command()
@click.option("--api-key-env", required=True)
def main(api_key_env: str):
    api_key = require_env(api_key_env)
    for project in fetch_projects(api_key):
        teams = ", ".join(t["name"] for t in project["teams"]["nodes"])
        click.echo(f"{project['name']} | {teams}")


PROJECTS_QUERY = """{ projects { nodes { name teams { nodes { name } } } } }"""


def fetch_projects(api_key: str) -> list:
    data = graphql(api_key, PROJECTS_QUERY)
    return data["data"]["projects"]["nodes"]


if __name__ == "__main__":
    main()
