"""Export issues, project updates, and resource links from a Linear workspace."""

import json
import re
import time
from pathlib import Path

import click

import _bootstrap  # noqa: F401
from linear_client import (
    graphql,
    normalize_quotes,
    require_env,
    resolve_by_name,
)


@click.command()
@click.option("--api-key-env", required=True)
@click.option("--project", required=True)
@click.option("--team", required=True)
@click.option("--output", required=True, type=click.Path())
def main(api_key_env: str, project: str, team: str, output: str):
    api_key = require_env(api_key_env)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)

    project_id = resolve_project_id(api_key, project)
    issues, labels = fetch_issues(api_key, team, project)
    fetch_comments(api_key, issues)
    states = fetch_states(api_key, team)
    meta = fetch_project_meta(api_key, project_id)
    project_info = extract_project_info(meta)
    updates = extract_updates(meta)
    links = extract_links(meta)

    grouped = group_by_state(issues)

    write_json(out / "all_cards.json", issues)
    write_json(out / "states.json", states)
    write_json(out / "project.json", project_info)
    write_json(out / "project_updates.json", updates)
    write_json(out / "project_links.json", links)
    write_labels(out, labels)
    write_grouped(grouped, out)
    write_summary(grouped, issues, updates, links, out)

    click.echo(
        f"Exported {len(issues)} issues across {len(grouped)} states to {out}"
    )


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
            attachments {{ nodes {{ title subtitle url sourceType metadata }} }}
        }}
        pageInfo {{ hasNextPage endCursor }}
    }}
}}"""


def fetch_issues(api_key: str, team: str, project: str) -> tuple:
    issues, labels = [], {}
    for page in paginate_issues(api_key, team, project):
        for n in page:
            issues.append(issue_record(n))
            collect_labels(n, labels)
    return issues, labels


def paginate_issues(api_key: str, team: str, project: str):
    cursor = None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        data = graphql(
            api_key,
            ISSUES_QUERY.format(team=team, project=project, after=after),
        )
        yield data["data"]["issues"]["nodes"]
        page = data["data"]["issues"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]


def collect_labels(node: dict, labels: dict):
    for label in node.get("labels", {}).get("nodes", []):
        labels[label["name"]] = label.get("color", "")


def issue_record(n: dict) -> dict:
    return {
        "id": n["id"],
        "identifier": n["identifier"],
        "title": normalize_quotes(n["title"]),
        "description": normalize_quotes(n.get("description") or ""),
        "state": n.get("state", {}).get("name", "Unknown"),
        "labels": label_names(n),
        "attachments": attachment_records(n),
        "url": n.get("url", ""),
        "comments": [],
    }


def label_names(n: dict) -> list:
    return [label["name"] for label in n.get("labels", {}).get("nodes", [])]


def attachment_records(n: dict) -> list:
    return [
        attachment_record(a) for a in n.get("attachments", {}).get("nodes", [])
    ]


def attachment_record(a: dict) -> dict:
    rec = {
        "title": a["title"],
        "subtitle": a.get("subtitle", ""),
        "url": a["url"],
        "sourceType": a.get("sourceType", ""),
    }
    if a.get("metadata"):
        rec["metadata"] = a["metadata"]
    return rec


COMMENTS_QUERY = """{{
    issue(id: "{issue_id}") {{
        comments(first: 250) {{ nodes {{ body createdAt user {{ name }} }} }}
    }}
}}"""


def fetch_comments(api_key: str, issues: list):
    for i, issue in enumerate(issues):
        data = graphql(api_key, COMMENTS_QUERY.format(issue_id=issue["id"]))
        issue["comments"] = sorted(
            [
                comment_record(c)
                for c in data["data"]["issue"]["comments"]["nodes"]
            ],
            key=lambda c: c["date"],
        )
        if i % 10 == 9:
            time.sleep(0.5)


def comment_record(c: dict) -> dict:
    return {
        "author": c.get("user", {}).get("name", "Unknown"),
        "date": c.get("createdAt", ""),
        "text": normalize_quotes(c.get("body", "")),
    }


STATES_QUERY = """{{ workflowStates(filter: {{ team: {{ name: {{ eq: "{team}" }} }} }}) {{
    nodes {{ name type }}
}} }}"""


def fetch_states(api_key: str, team: str) -> list:
    data = graphql(api_key, STATES_QUERY.format(team=team))
    return data["data"]["workflowStates"]["nodes"]


def resolve_project_id(api_key: str, project: str) -> str:
    return resolve_by_name(api_key, "projects", project)


PROJECT_META_QUERY = """{{
    project(id: "{project_id}") {{
        name description content
        projectUpdates(first: 50) {{
            nodes {{ id body health createdAt user {{ name }} }}
        }}
        externalLinks {{
            nodes {{ id label url }}
        }}
    }}
}}"""


def fetch_project_meta(api_key: str, project_id: str) -> dict:
    data = graphql(api_key, PROJECT_META_QUERY.format(project_id=project_id))
    return data["data"]["project"]


def extract_project_info(meta: dict) -> dict:
    return {
        "name": meta.get("name", ""),
        "summary": normalize_quotes(meta.get("description") or ""),
        "description": normalize_quotes(meta.get("content") or ""),
    }


def extract_updates(meta: dict) -> list:
    updates = meta["projectUpdates"]["nodes"]
    return sorted(
        [update_record(u) for u in updates], key=lambda u: u["createdAt"]
    )


def update_record(n: dict) -> dict:
    return {
        "body": normalize_quotes(n.get("body", "")),
        "health": n.get("health", "onTrack"),
        "createdAt": n.get("createdAt", ""),
        "author": n.get("user", {}).get("name", "Unknown"),
    }


def extract_links(meta: dict) -> list:
    return [link_record(ln) for ln in meta["externalLinks"]["nodes"]]


def link_record(n: dict) -> dict:
    return {"label": normalize_quotes(n["label"]), "url": n["url"]}


def write_labels(out: Path, labels: dict):
    write_json(
        out / "labels.json",
        [{"name": n, "color": c} for n, c in labels.items()],
    )


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


def write_summary(
    grouped: dict, issues: list, updates: list, links: list, out: Path
):
    def count(items, field):
        return sum(1 for i in items if i[field])

    lines = [
        "# Linear export summary\n",
        f"**Total issues**: {len(issues)}",
        f"**With descriptions**: {count(issues, 'description')}",
        f"**With comments**: {count(issues, 'comments')}",
        f"**Project updates**: {len(updates)}",
        f"**Resource links**: {len(links)}\n",
        "| State | Issues | With desc | With comments |",
        "|:------|-------:|----------:|--------------:|",
    ]
    for name in sorted(grouped):
        g = grouped[name]
        lines.append(
            f"| {name} | {len(g)} | {count(g, 'description')} | {count(g, 'comments')} |"
        )
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
