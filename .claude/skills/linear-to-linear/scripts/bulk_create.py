"""Create issues, project updates, and resource links in a target Linear workspace."""

import json
import time
from pathlib import Path

import click

import _bootstrap  # noqa: F401
from linear_client import (
    LinearError,
    create_attachment,
    create_issue,
    create_project_link,
    create_project_update,
    list_labels,
    require_env,
    resolve_by_name,
    resolve_states,
)


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
        process_project_meta(api_key, project_id, meta_dir)


def resolve_state_ids(api_key: str, team_id: str) -> dict:
    states = resolve_states(api_key, team_id)
    return {name: s["id"] for name, s in states.items()}


def resolve_label_ids(api_key: str) -> dict:
    return {label["name"]: label["id"] for label in list_labels(api_key)}


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
        ok = process_one_issue(
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


def process_one_issue(
    api_key: str,
    team_id: str,
    project_id: str,
    state_ids: dict,
    label_ids: dict,
    payload: dict,
) -> bool:
    state_id = state_ids[payload.get("state", "Backlog")]
    resolved_labels = resolve_payload_labels(payload, label_ids)
    title = payload["title"]
    try:
        issue_id = create_issue(
            api_key,
            team_id=team_id,
            project_id=project_id,
            state_id=state_id,
            title=title,
            description=payload["description"],
            label_ids=resolved_labels or None,
        )
    except LinearError as e:
        click.echo(f"  ✗ ERROR: {title[:60]} — {e}")
        return False
    click.echo(f"  ✓ {title[:60]}")
    process_attachments(api_key, issue_id, payload.get("attachments", []))
    return True


def resolve_payload_labels(payload: dict, label_ids: dict) -> list:
    return [label_ids[n] for n in payload.get("labels", []) if n in label_ids]


def process_attachments(api_key: str, issue_id: str, attachments: list):
    for a in attachments:
        try:
            create_attachment(
                api_key,
                issue_id=issue_id,
                title=a["title"],
                url=a["url"],
                subtitle=a.get("subtitle") or None,
                metadata=a.get("metadata") or None,
            )
            click.echo(f"    ✓ attachment: {a['title'][:50]}")
        except LinearError as e:
            click.echo(f"    ✗ attachment: {a['title'][:50]} — {e}")


def load_json_file(path: Path) -> list:
    return json.loads(path.read_text()) if path.exists() else []


def preview_project_meta(meta_dir: Path):
    for u in load_json_file(meta_dir / "project_updates.json"):
        click.echo(f"[DRY RUN] Update: {u['health']} — {u['body'][:60]}")
    for ln in load_json_file(meta_dir / "project_links.json"):
        click.echo(f"[DRY RUN] Link: {ln['label']} → {ln['url']}")


def process_project_meta(api_key: str, project_id: str, meta_dir: Path):
    for u in load_json_file(meta_dir / "project_updates.json"):
        process_one_update(api_key, project_id, u)
    for ln in load_json_file(meta_dir / "project_links.json"):
        process_one_link(api_key, project_id, ln)


def process_one_update(api_key: str, project_id: str, update: dict):
    try:
        create_project_update(
            api_key, project_id, update["body"], update["health"]
        )
        click.echo(f"  ✓ update: {update['health']} — {update['body'][:50]}")
    except LinearError as e:
        click.echo(f"  ✗ update: {update['body'][:50]} — {e}")


def process_one_link(api_key: str, project_id: str, link: dict):
    try:
        create_project_link(api_key, project_id, link["url"], link["label"])
        click.echo(f"  ✓ link: {link['label']} → {link['url']}")
    except LinearError as e:
        click.echo(f"  ✗ link: {link['label']} → {link['url']} — {e}")


if __name__ == "__main__":
    main()
