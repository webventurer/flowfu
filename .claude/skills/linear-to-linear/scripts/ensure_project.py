"""Create or update the target Linear project from exported project.json."""

import json
from pathlib import Path

import click
from linear_api import graphql, require_env, resolve_by_name


@click.command()
@click.option("--api-key-env", required=True)
@click.option("--team", required=True)
@click.option("--project", required=True)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
def main(api_key_env: str, team: str, project: str, export_dir: str):
    api_key = require_env(api_key_env)
    info = json.loads((Path(export_dir) / "project.json").read_text())
    team_id = resolve_by_name(api_key, "teams", team)

    existing = find_project(api_key, project)
    if existing:
        update_project(api_key, existing["id"], info)
        click.echo(f"Updated project: {project}")
    else:
        created = create_project(api_key, team_id, project, info)
        click.echo(f"Created project: {created['name']} ({created['id']})")


def find_project(api_key: str, name: str) -> dict | None:
    query = f'{{ projects(filter: {{ name: {{ eq: "{name}" }} }}) {{ nodes {{ id name }} }} }}'
    nodes = graphql(api_key, query)["data"]["projects"]["nodes"]
    return nodes[0] if nodes else None


CREATE_PROJECT_QUERY = """mutation($input: ProjectCreateInput!) {
    projectCreate(input: $input) {
        success
        project { id name }
    }
}"""


def create_project(api_key: str, team_id: str, name: str, info: dict) -> dict:
    input_data = build_project_input(info, name=name, team_id=team_id)
    data = graphql(
        api_key, CREATE_PROJECT_QUERY, variables={"input": input_data}
    )
    return data["data"]["projectCreate"]["project"]


UPDATE_PROJECT_QUERY = """mutation($id: String!, $input: ProjectUpdateInput!) {
    projectUpdate(id: $id, input: $input) {
        success
        project { id name }
    }
}"""


def update_project(api_key: str, project_id: str, info: dict):
    input_data = build_project_input(info)
    graphql(
        api_key,
        UPDATE_PROJECT_QUERY,
        variables={"id": project_id, "input": input_data},
    )


def build_project_input(info: dict, name: str = None, team_id: str = None) -> dict:
    result = {
        "description": info.get("summary", ""),
        "content": info.get("description", ""),
    }
    if name:
        result["name"] = name
    if team_id:
        result["teamIds"] = [team_id]
    return result


if __name__ == "__main__":
    main()
