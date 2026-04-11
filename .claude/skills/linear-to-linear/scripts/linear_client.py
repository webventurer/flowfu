"""Reusable Linear GraphQL client helpers.

Vendored module — no support, no versioning, no PyPI. Copy and adapt
to your needs. See scripts/README.md for the usage contract.

All mutation helpers accept IDs only (no name resolution), return the
created or updated node's id as a string, and raise LinearError on
failure. Use resolve_by_name() to turn names into IDs.
"""

import os
import re
import time

import requests

API_URL = "https://api.linear.app/graphql"


class LinearError(Exception):
    """Raised when a Linear API call fails — connection, HTTP, or GraphQL errors."""


def graphql(
    api_key: str, query: str, variables: dict | None = None, retries: int = 3
) -> dict:
    body = {"query": query}
    if variables:
        body["variables"] = variables
    for attempt in range(retries):
        try:
            return _post_and_check(api_key, body, query)
        except (requests.ConnectionError, requests.Timeout) as e:
            if attempt == retries - 1:
                raise LinearError(
                    f"connection failed after {retries} attempts on {_operation_name(query)}: {e}"
                ) from e
            time.sleep(2**attempt)


def _post_and_check(api_key: str, body: dict, query: str) -> dict:
    resp = requests.post(
        API_URL,
        json=body,
        headers={"Authorization": api_key, "Content-Type": "application/json"},
    )
    _raise_for_http(resp, query)
    data = resp.json()
    _raise_for_graphql_errors(data, query)
    return data


def _raise_for_http(resp: requests.Response, query: str):
    if resp.status_code >= 400:
        raise LinearError(
            f"HTTP {resp.status_code} on {_operation_name(query)}: {resp.text[:200]}"
        )


def _raise_for_graphql_errors(data: dict, query: str):
    errors = data.get("errors")
    if errors:
        msgs = "; ".join(e.get("message", "?") for e in errors)
        raise LinearError(f"GraphQL errors on {_operation_name(query)}: {msgs}")


def _operation_name(query: str) -> str:
    match = re.search(r"(?:mutation|query)\s*(\w+)?\s*[\(\{]", query)
    if match and match.group(1):
        return match.group(1)
    inner = re.search(r"\{\s*(\w+)", query)
    return inner.group(1) if inner else "?"


def require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Env var {name} is not set")
    return val


def resolve_by_name(api_key: str, entity: str, name: str) -> str:
    query = f'{{ {entity}(filter: {{ name: {{ eq: "{name}" }} }}) {{ nodes {{ id }} }} }}'
    return graphql(api_key, query)["data"][entity]["nodes"][0]["id"]


def resolve_states(api_key: str, team_id: str) -> dict:
    query = f'{{ workflowStates(filter: {{ team: {{ id: {{ eq: "{team_id}" }} }} }}) {{ nodes {{ id name type }} }} }}'
    data = graphql(api_key, query)
    return {s["name"]: s for s in data["data"]["workflowStates"]["nodes"]}


QUOTE_MAP = str.maketrans(
    {"\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'"}
)


def normalize_quotes(text: str) -> str:
    return (text or "").translate(QUOTE_MAP)


# ---- Mutations: issues ----

CREATE_ISSUE_QUERY = """mutation($input: IssueCreateInput!) {
    issueCreate(input: $input) {
        issue { id }
    }
}"""


def create_issue(
    api_key: str,
    team_id: str,
    project_id: str,
    state_id: str,
    title: str,
    description: str,
    label_ids: list | None = None,
) -> str:
    input_data = {
        "teamId": team_id,
        "projectId": project_id,
        "stateId": state_id,
        "title": title,
        "description": description,
    }
    if label_ids:
        input_data["labelIds"] = label_ids
    data = graphql(api_key, CREATE_ISSUE_QUERY, variables={"input": input_data})
    return data["data"]["issueCreate"]["issue"]["id"]


UPDATE_ISSUE_QUERY = """mutation($id: String!, $input: IssueUpdateInput!) {
    issueUpdate(id: $id, input: $input) {
        issue { id }
    }
}"""


def update_issue(
    api_key: str,
    issue_id: str,
    title: str | None = None,
    description: str | None = None,
    state_id: str | None = None,
    label_ids: list | None = None,
) -> str:
    input_data = {}
    if title is not None:
        input_data["title"] = title
    if description is not None:
        input_data["description"] = description
    if state_id is not None:
        input_data["stateId"] = state_id
    if label_ids is not None:
        input_data["labelIds"] = label_ids
    data = graphql(
        api_key,
        UPDATE_ISSUE_QUERY,
        variables={"id": issue_id, "input": input_data},
    )
    return data["data"]["issueUpdate"]["issue"]["id"]


LIST_ISSUES_QUERY = """{{
    issues(
        filter: {{ {filters} }}
        first: 250 {after}
    ) {{
        nodes {{ id identifier title description }}
        pageInfo {{ hasNextPage endCursor }}
    }}
}}"""


def list_issues(
    api_key: str,
    team_id: str | None = None,
    project_id: str | None = None,
) -> list:
    issues, cursor = [], None
    while True:
        query = _list_issues_query(team_id, project_id, cursor)
        page = graphql(api_key, query)["data"]["issues"]
        issues.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return issues
        cursor = page["pageInfo"]["endCursor"]


def _list_issues_query(
    team_id: str | None, project_id: str | None, cursor: str | None
) -> str:
    filters = _issue_filters(team_id, project_id)
    after = f', after: "{cursor}"' if cursor else ""
    return LIST_ISSUES_QUERY.format(filters=filters, after=after)


def _issue_filters(team_id: str | None, project_id: str | None) -> str:
    parts = []
    if team_id:
        parts.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
    if project_id:
        parts.append(f'project: {{ id: {{ eq: "{project_id}" }} }}')
    return " ".join(parts)


CREATE_ATTACHMENT_QUERY = """mutation($input: AttachmentCreateInput!) {
    attachmentCreate(input: $input) {
        attachment { id }
    }
}"""


def create_attachment(
    api_key: str,
    issue_id: str,
    title: str,
    url: str,
    subtitle: str | None = None,
    metadata: dict | None = None,
) -> str:
    input_data = {"issueId": issue_id, "title": title, "url": url}
    if subtitle:
        input_data["subtitle"] = subtitle
    if metadata:
        input_data["metadata"] = metadata
    data = graphql(
        api_key, CREATE_ATTACHMENT_QUERY, variables={"input": input_data}
    )
    return data["data"]["attachmentCreate"]["attachment"]["id"]


DELETE_ISSUE_QUERY = """mutation($id: String!) {
    issueDelete(id: $id) { success }
}"""


def delete_issue(api_key: str, issue_id: str):
    graphql(api_key, DELETE_ISSUE_QUERY, variables={"id": issue_id})


# ---- Mutations: projects ----

CREATE_PROJECT_QUERY = """mutation($input: ProjectCreateInput!) {
    projectCreate(input: $input) {
        project { id }
    }
}"""


def create_project(
    api_key: str,
    team_id: str,
    name: str,
    description: str | None = None,
    content: str | None = None,
) -> str:
    input_data = {"name": name, "teamIds": [team_id]}
    if description is not None:
        input_data["description"] = description
    if content is not None:
        input_data["content"] = content
    data = graphql(
        api_key, CREATE_PROJECT_QUERY, variables={"input": input_data}
    )
    return data["data"]["projectCreate"]["project"]["id"]


UPDATE_PROJECT_QUERY = """mutation($id: String!, $input: ProjectUpdateInput!) {
    projectUpdate(id: $id, input: $input) {
        project { id }
    }
}"""


def update_project(
    api_key: str,
    project_id: str,
    description: str | None = None,
    content: str | None = None,
) -> str:
    input_data = {}
    if description is not None:
        input_data["description"] = description
    if content is not None:
        input_data["content"] = content
    data = graphql(
        api_key,
        UPDATE_PROJECT_QUERY,
        variables={"id": project_id, "input": input_data},
    )
    return data["data"]["projectUpdate"]["project"]["id"]


DELETE_PROJECT_QUERY = """mutation($id: String!) {
    projectDelete(id: $id) { success }
}"""


def delete_project(api_key: str, project_id: str):
    graphql(api_key, DELETE_PROJECT_QUERY, variables={"id": project_id})


# ---- Mutations: project metadata (status updates + resource links) ----

CREATE_PROJECT_UPDATE_QUERY = """mutation($input: ProjectUpdateCreateInput!) {
    projectUpdateCreate(input: $input) {
        projectUpdate { id }
    }
}"""


def create_project_update(
    api_key: str, project_id: str, body: str, health: str
) -> str:
    input_data = {"projectId": project_id, "body": body, "health": health}
    data = graphql(
        api_key, CREATE_PROJECT_UPDATE_QUERY, variables={"input": input_data}
    )
    return data["data"]["projectUpdateCreate"]["projectUpdate"]["id"]


CREATE_PROJECT_LINK_QUERY = """mutation($input: EntityExternalLinkCreateInput!) {
    entityExternalLinkCreate(input: $input) {
        entityExternalLink { id }
    }
}"""


def create_project_link(
    api_key: str, project_id: str, url: str, label: str
) -> str:
    input_data = {"projectId": project_id, "url": url, "label": label}
    data = graphql(
        api_key, CREATE_PROJECT_LINK_QUERY, variables={"input": input_data}
    )
    return data["data"]["entityExternalLinkCreate"]["entityExternalLink"]["id"]


# ---- Mutations: labels ----

CREATE_LABEL_QUERY = """mutation($input: IssueLabelCreateInput!) {
    issueLabelCreate(input: $input) {
        issueLabel { id }
    }
}"""


def create_label(
    api_key: str,
    name: str,
    color: str | None = None,
    team_id: str | None = None,
) -> str:
    input_data = {"name": name}
    if color:
        input_data["color"] = color
    if team_id:
        input_data["teamId"] = team_id
    data = graphql(api_key, CREATE_LABEL_QUERY, variables={"input": input_data})
    return data["data"]["issueLabelCreate"]["issueLabel"]["id"]


DELETE_LABEL_QUERY = """mutation($id: String!) {
    issueLabelDelete(id: $id) { success }
}"""


def delete_label(api_key: str, label_id: str):
    graphql(api_key, DELETE_LABEL_QUERY, variables={"id": label_id})


# ---- Queries: lists ----

LIST_PROJECTS_QUERY = """{{
    projects(first: 50 {after}) {{
        nodes {{
            id name
            teams {{ nodes {{ id name }} }}
        }}
        pageInfo {{ hasNextPage endCursor }}
    }}
}}"""


def list_projects(api_key: str, team_id: str | None = None) -> list:
    projects, cursor = [], None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = graphql(api_key, LIST_PROJECTS_QUERY.format(after=after))
        page = data["data"]["projects"]
        projects.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return _filter_by_team(projects, team_id) if team_id else projects


def _filter_by_team(projects: list, team_id: str) -> list:
    return [
        p
        for p in projects
        if any(t["id"] == team_id for t in p["teams"]["nodes"])
    ]


LIST_LABELS_QUERY = """{{
    issueLabels(first: 250 {after}) {{
        nodes {{ id name color team {{ id }} }}
        pageInfo {{ hasNextPage endCursor }}
    }}
}}"""


def list_labels(api_key: str, team_id: str | None = None) -> list:
    labels, cursor = [], None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = graphql(api_key, LIST_LABELS_QUERY.format(after=after))
        page = data["data"]["issueLabels"]
        labels.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return _labels_for_team(labels, team_id) if team_id else labels


def _labels_for_team(labels: list, team_id: str) -> list:
    return [
        lbl
        for lbl in labels
        if lbl.get("team") and lbl["team"]["id"] == team_id
    ]
