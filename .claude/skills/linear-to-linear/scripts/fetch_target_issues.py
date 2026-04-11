"""Fetch all issues in a target Linear project to JSON for match.py."""

import json
from pathlib import Path

import click
from linear_api import graphql, require_env


@click.command()
@click.option("--api-key-env", required=True)
@click.option("--team", required=True)
@click.option("--project", required=True)
@click.option("--output", required=True, type=click.Path())
def main(api_key_env: str, team: str, project: str, output: str):
    api_key = require_env(api_key_env)
    issues = fetch_issues(api_key, team, project)
    Path(output).write_text(json.dumps(issues, indent=2))
    click.echo(f"Fetched {len(issues)} target issues to {output}")


ISSUES_QUERY = """{{ issues(filter: {{
    team: {{ name: {{ eq: "{team}" }} }}
    project: {{ name: {{ eq: "{project}" }} }}
}}, first: 250 {after}) {{
    nodes {{ id identifier title description }}
    pageInfo {{ hasNextPage endCursor }}
}} }}"""


def fetch_issues(api_key: str, team: str, project: str) -> list:
    issues, cursor = [], None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = graphql(
            api_key,
            ISSUES_QUERY.format(team=team, project=project, after=after),
        )["data"]["issues"]
        issues.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]
    return issues


if __name__ == "__main__":
    main()
