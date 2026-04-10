"""Export issues with descriptions, comments, and labels from a Linear workspace."""

import json
import re
import time
from pathlib import Path

import click
from linear_api import graphql, require_env

ISSUES_QUERY = """{{
    issues(
        filter: {{
            team: {{ name: {{ eq: "{team}" }} }}
            project: {{ name: {{ eq: "{project}" }} }}
        }}
        first: 250 {after}
    ) {{
        nodes {{
            id identifier title description url
            state {{ name }}
            labels {{ nodes {{ name color }} }}
            attachments {{ nodes {{ title subtitle url sourceType }} }}
        }}
        pageInfo {{ hasNextPage endCursor }}
    }}
}}"""

COMMENTS_QUERY = """{{
    issue(id: "{issue_id}") {{
        comments(first: 250) {{ nodes {{ body createdAt user {{ name }} }} }}
    }}
}}"""

STATES_QUERY = """{{ workflowStates(filter: {{ team: {{ name: {{ eq: "{team}" }} }} }}) {{
    nodes {{ name type }}
}} }}"""


@click.command()
@click.option("--api-key-env", required=True)
@click.option("--project", required=True)
@click.option("--team", required=True)
@click.option("--output", required=True, type=click.Path())
def main(api_key_env: str, project: str, team: str, output: str):
    api_key = require_env(api_key_env)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)

    issues, labels = fetch_issues(api_key, team, project)
    fetch_comments(api_key, issues)
    states = fetch_states(api_key, team)

    grouped = group_by_state(issues)

    write_json(out / "all_cards.json", issues)
    write_json(out / "states.json", states)
    write_json(out / "labels.json", [{"name": n, "color": c} for n, c in labels.items()])
    write_grouped(grouped, out)
    write_summary(grouped, issues, out)

    click.echo(f"Exported {len(issues)} issues across {len(grouped)} states to {out}")


def fetch_issues(api_key: str, team: str, project: str) -> tuple:
    issues, labels, cursor = [], {}, None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = graphql(api_key, ISSUES_QUERY.format(team=team, project=project, after=after))
        for n in data["data"]["issues"]["nodes"]:
            issues.append(issue_record(n))
            for l in n.get("labels", {}).get("nodes", []):
                labels[l["name"]] = l.get("color", "")
        page = data["data"]["issues"]["pageInfo"]
        cursor = page["endCursor"] if page["hasNextPage"] else None
        if not cursor:
            break
    return issues, labels


def issue_record(n: dict) -> dict:
    return {
        "id": n["id"],
        "identifier": n["identifier"],
        "title": n["title"],
        "description": n.get("description") or "",
        "state": n.get("state", {}).get("name", "Unknown"),
        "labels": [l["name"] for l in n.get("labels", {}).get("nodes", [])],
        "attachments": [attachment_record(a) for a in n.get("attachments", {}).get("nodes", [])],
        "url": n.get("url", ""),
        "comments": [],
    }


def attachment_record(a: dict) -> dict:
    return {
        "title": a["title"],
        "subtitle": a.get("subtitle", ""),
        "url": a["url"],
        "sourceType": a.get("sourceType", ""),
    }


def fetch_comments(api_key: str, issues: list):
    for i, issue in enumerate(issues):
        data = graphql(api_key, COMMENTS_QUERY.format(issue_id=issue["id"]))
        issue["comments"] = [
            {
                "author": c.get("user", {}).get("name", "Unknown"),
                "date": c.get("createdAt", ""),
                "text": c.get("body", ""),
            }
            for c in data["data"]["issue"]["comments"]["nodes"]
        ]
        if i % 10 == 9:
            time.sleep(0.5)


def fetch_states(api_key: str, team: str) -> list:
    data = graphql(api_key, STATES_QUERY.format(team=team))
    return data["data"]["workflowStates"]["nodes"]


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2))


def group_by_state(issues: list) -> dict:
    grouped = {}
    for issue in issues:
        grouped.setdefault(issue["state"], []).append(issue)
    return grouped


def write_grouped(grouped: dict, out: Path):
    for i, (state, group) in enumerate(sorted(grouped.items()), 1):
        slug = re.sub(r"[^a-z0-9]+", "-", state.lower()).strip("-")
        write_json(out / f"{i:02d}-{slug}.json", group)


def write_summary(grouped: dict, issues: list, out: Path):
    def count(items, field):
        return sum(1 for i in items if i[field])

    lines = [
        "# Linear export summary\n",
        f"**Total issues**: {len(issues)}",
        f"**With descriptions**: {count(issues, 'description')}",
        f"**With comments**: {count(issues, 'comments')}\n",
        "| State | Issues | With desc | With comments |",
        "|:------|-------:|----------:|--------------:|",
    ]
    for name in sorted(grouped):
        g = grouped[name]
        lines.append(f"| {name} | {len(g)} | {count(g, 'description')} | {count(g, 'comments')} |")
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
