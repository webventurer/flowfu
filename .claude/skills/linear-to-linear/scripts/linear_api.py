"""Shared Linear GraphQL client, retry logic, and file loaders."""

import json
import os
import time
from pathlib import Path

import requests

API_URL = "https://api.linear.app/graphql"


def graphql(
    api_key: str, query: str, variables: dict | None = None, retries: int = 3
) -> dict:
    body = {"query": query}
    if variables:
        body["variables"] = variables

    for attempt in range(retries):
        try:
            resp = requests.post(
                API_URL,
                json=body,
                headers={
                    "Authorization": api_key,
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()
        except (requests.ConnectionError, requests.Timeout):
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)


def resolve_by_name(api_key: str, entity: str, name: str) -> str:
    query = f"""{{ {entity}(filter: {{ name: {{ eq: "{name}" }} }}) {{ nodes {{ id }} }} }}"""
    return graphql(api_key, query)["data"][entity]["nodes"][0]["id"]


def resolve_states(api_key: str, team_id: str) -> dict:
    query = f"""{{ workflowStates(filter: {{ team: {{ id: {{ eq: "{team_id}" }} }} }}) {{ nodes {{ id name type }} }} }}"""
    data = graphql(api_key, query)
    return {s["name"]: s for s in data["data"]["workflowStates"]["nodes"]}


def require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise SystemExit(f"Env var {name} is not set")
    return val


def load_source_cards(source_dir: str) -> list:
    cards = []
    for f in sorted(Path(source_dir).glob("[0-9]*.json")):
        cards.extend(json.loads(f.read_text()))
    return cards


def load_target_issues_file(path: str) -> list:
    raw = json.loads(Path(path).read_text())
    if isinstance(raw, list) and raw and "text" in raw[0]:
        return json.loads(raw[0]["text"]).get("issues", [])
    if isinstance(raw, dict):
        return raw.get("issues", [])
    return raw
