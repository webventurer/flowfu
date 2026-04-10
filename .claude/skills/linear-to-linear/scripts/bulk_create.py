"""Create issues, project updates, and resource links in a target Linear workspace."""

import json
import time
from pathlib import Path

import click
from linear_api import graphql, require_env, resolve_by_name, resolve_states


@click.command()
@click.option("--cards-dir", required=True, type=click.Path(exists=True))
@click.option("--api-key-env", required=True)
@click.option("--team", required=True, help="Target Linear team name")
@click.option("--project", required=True, help="Target Linear project name")
@click.option("--export-dir", default=None, type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, default=False)
def main(
    cards_dir: str,
    api_key_env: str,
    team: str,
    project: str,
    export_dir: str,
    dry_run: bool,
):
    api_key = require_env(api_key_env)
    team_id = resolve_by_name(api_key, "teams", team)
    project_id = resolve_by_name(api_key, "projects", project)
    state_ids = resolve_state_ids(api_key, team_id)
    label_ids = resolve_label_ids(api_key)
    payloads = load_create_payloads(Path(cards_dir))
    meta_dir = Path(export_dir) if export_dir else Path(cards_dir).parent

    validate_states(payloads, state_ids)

    if dry_run:
        preview_payloads(payloads)
        preview_project_meta(meta_dir)
    else:
        process_payloads(
            api_key, team_id, project_id, state_ids, label_ids, payloads
        )
        create_project_meta(api_key, project_id, meta_dir)


def resolve_state_ids(api_key: str, team_id: str) -> dict:
    states = resolve_states(api_key, team_id)
    return {name: s["id"] for name, s in states.items()}


LABELS_QUERY = """{ issueLabels { nodes { id name } } }"""


def resolve_label_ids(api_key: str) -> dict:
    data = graphql(api_key, LABELS_QUERY)
    return {
        label["name"]: label["id"]
        for label in data["data"]["issueLabels"]["nodes"]
    }


def validate_states(payloads: list, state_ids: dict):
    required = {p.get("state", "Backlog") for p in payloads}
    missing = required - set(state_ids)
    if not missing:
        return
    report_missing_states(missing, state_ids)
    raise SystemExit(1)


def report_missing_states(missing: set, state_ids: dict):
    click.echo("FAIL: source states missing from target:\n")
    for name in sorted(missing):
        click.echo(f"  ✗ {name}")
    click.echo("\nTarget has:")
    for name in sorted(state_ids):
        click.echo(f"  ✓ {name}")


def preview_payloads(payloads: list):
    for p in payloads:
        click.echo(
            f"[DRY RUN] {p['title'][:60]} → {p.get('state', 'Backlog')}{preview_suffix(p)}"
        )


def preview_suffix(p: dict) -> str:
    parts = []
    if labels := p.get("labels", []):
        parts.append(f"[{', '.join(labels)}]")
    if atts := p.get("attachments", []):
        parts.append(f"({len(atts)} attachments)")
    return f" {' '.join(parts)}" if parts else ""


def process_payloads(
    api_key: str,
    team_id: str,
    project_id: str,
    state_ids: dict,
    label_ids: dict,
    payloads: list,
):
    created, failed = 0, 0
    for payload in payloads:
        ok = create_issue(
            api_key, team_id, project_id, state_ids, label_ids, payload
        )
        created += ok
        failed += not ok
        throttle(created)
    click.echo(f"\nCreated: {created}, Failed: {failed}")


def throttle(count: int):
    if count % 10 == 0:
        time.sleep(0.5)


def load_create_payloads(cards_dir: Path) -> list:
    return [
        payload
        for f in sorted(cards_dir.glob("*.json"))
        if (payload := json.loads(f.read_text())).get("action") == "create"
    ]


def create_issue(
    api_key: str,
    team_id: str,
    project_id: str,
    state_ids: dict,
    label_ids: dict,
    payload: dict,
) -> bool:
    state = payload.get("state", "Backlog")
    state_id = state_ids[state]
    issue_input = build_issue_input(
        team_id, project_id, state_id, label_ids, payload
    )
    issue_id = submit_issue(api_key, issue_input, payload["title"])
    if issue_id:
        create_attachments(api_key, issue_id, payload.get("attachments", []))
    return bool(issue_id)


def build_issue_input(
    team_id: str, project_id: str, state_id: str, label_ids: dict, payload: dict
) -> dict:
    result = {
        "teamId": team_id,
        "projectId": project_id,
        "stateId": state_id,
        "title": payload["title"],
        "description": payload["description"],
    }
    if resolved := resolve_payload_labels(payload, label_ids):
        result["labelIds"] = resolved
    return result


def resolve_payload_labels(payload: dict, label_ids: dict) -> list:
    return [label_ids[n] for n in payload.get("labels", []) if n in label_ids]


CREATE_ISSUE_QUERY = """mutation($input: IssueCreateInput!) {
    issueCreate(input: $input) {
        success
        issue { id identifier title }
    }
}"""


def submit_issue(api_key: str, issue_input: dict, title: str) -> str | None:
    try:
        data = graphql(
            api_key, CREATE_ISSUE_QUERY, variables={"input": issue_input}
        )
        success = (
            data.get("data", {}).get("issueCreate", {}).get("success", False)
        )
        if success:
            issue = data["data"]["issueCreate"]["issue"]
            click.echo(f"  ✓ {issue['identifier']}: {issue['title'][:60]}")
            return issue["id"]
        click.echo(f"  ✗ FAILED: {title[:60]} — {data}")
        return None
    except Exception as e:
        click.echo(f"  ✗ ERROR: {title[:60]} — {e}")
        return None


CREATE_ATTACHMENT_QUERY = """mutation($input: AttachmentCreateInput!) {
    attachmentCreate(input: $input) { success }
}"""


def create_attachments(api_key: str, issue_id: str, attachments: list):
    for a in attachments:
        att_input = {"issueId": issue_id, "title": a["title"], "url": a["url"]}
        if a.get("subtitle"):
            att_input["subtitle"] = a["subtitle"]
        if a.get("metadata"):
            att_input["metadata"] = a["metadata"]
        result = graphql(
            api_key, CREATE_ATTACHMENT_QUERY, variables={"input": att_input}
        )
        success = (
            result.get("data", {})
            .get("attachmentCreate", {})
            .get("success", False)
        )
        icon = "✓" if success else "✗"
        click.echo(f"    {icon} attachment: {a['title'][:50]}")


def load_json_file(path: Path) -> list:
    return json.loads(path.read_text()) if path.exists() else []


def preview_project_meta(meta_dir: Path):
    for u in load_json_file(meta_dir / "project_updates.json"):
        click.echo(f"[DRY RUN] Update: {u['health']} — {u['body'][:60]}")
    for ln in load_json_file(meta_dir / "project_links.json"):
        click.echo(f"[DRY RUN] Link: {ln['label']} → {ln['url']}")


def create_project_meta(api_key: str, project_id: str, meta_dir: Path):
    for u in load_json_file(meta_dir / "project_updates.json"):
        create_project_update(api_key, project_id, u)
    for ln in load_json_file(meta_dir / "project_links.json"):
        create_project_link(api_key, project_id, ln)


CREATE_UPDATE_QUERY = """mutation($input: ProjectUpdateCreateInput!) {
    projectUpdateCreate(input: $input) {
        success
        projectUpdate { id health }
    }
}"""


def create_project_update(api_key: str, project_id: str, update: dict) -> bool:
    input_data = {
        "projectId": project_id,
        "health": update["health"],
        "body": update["body"],
    }
    data = graphql(
        api_key, CREATE_UPDATE_QUERY, variables={"input": input_data}
    )
    success = data.get("data", {}).get("projectUpdateCreate", {}).get("success")
    icon = "✓" if success else "✗"
    click.echo(f"  {icon} update: {update['health']} — {update['body'][:50]}")
    return bool(success)


CREATE_LINK_QUERY = """mutation($input: EntityExternalLinkCreateInput!) {
    entityExternalLinkCreate(input: $input) {
        success
        entityExternalLink { id }
    }
}"""


def create_project_link(api_key: str, project_id: str, link: dict) -> bool:
    input_data = {
        "projectId": project_id,
        "url": link["url"],
        "label": link["label"],
    }
    data = graphql(api_key, CREATE_LINK_QUERY, variables={"input": input_data})
    success = (
        data.get("data", {}).get("entityExternalLinkCreate", {}).get("success")
    )
    icon = "✓" if success else "✗"
    click.echo(f"  {icon} link: {link['label']} → {link['url']}")
    return bool(success)


if __name__ == "__main__":
    main()
