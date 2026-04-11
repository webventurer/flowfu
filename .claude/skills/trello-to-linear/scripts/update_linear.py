"""Update matched Linear issues and create missing ones from a match report.

`--dry-run` (default) writes one JSON payload per entry to `cards/`
next to the match report so reviewers can inspect what would change
without touching Linear. `--apply` calls Linear directly via
`linear_client` — no cards/ files, no agent round-trip.
"""

import json
import time
from pathlib import Path

import click

import _bootstrap  # noqa: F401
from linear_client import (
    LinearError,
    create_issue,
    require_env,
    resolve_by_name,
    resolve_states,
    update_issue,
)

DEFAULT_LIST_TO_STATE = {
    "Done": "Done",
    "Current iteration": "Todo",
    "Backburner": "Backburner",
}


@click.command()
@click.option(
    "--match-report",
    required=True,
    type=click.Path(exists=True),
    help="Path to match-report.json",
)
@click.option(
    "--api-key-env",
    default=None,
    help="Env var holding the Linear API key (required with --apply)",
)
@click.option(
    "--team", default=None, help="Linear team name (required for creates)"
)
@click.option(
    "--project",
    default=None,
    help="Linear project name (required for creates in apply mode)",
)
@click.option(
    "--state-map",
    default=None,
    type=click.Path(exists=True),
    help="JSON file mapping Trello list names to Linear state names",
)
@click.option(
    "--apply", "mode", flag_value="apply", help="Actually update Linear"
)
@click.option(
    "--dry-run",
    "mode",
    flag_value="dry-run",
    default=True,
    help="Write payload files for inspection (default)",
)
def main(
    match_report: str,
    api_key_env: str,
    team: str,
    project: str,
    state_map: str,
    mode: str,
):
    report = json.loads(Path(match_report).read_text())
    list_to_state = load_state_map(state_map)
    updates, creates = split_by_action(report)

    require_team_for_creates(creates, team)
    if creates:
        validate_states(creates, list_to_state)
    if not updates and not creates:
        click.echo(
            "Nothing to do — all matched issues already have descriptions."
        )
        return

    if mode == "apply":
        apply_to_linear(
            updates, creates, api_key_env, team, project, list_to_state
        )
    else:
        dry_run_payloads(
            updates, creates, team, project, list_to_state, match_report
        )


def split_by_action(report: list) -> tuple:
    updates = [r for r in report if r["action"] == "update"]
    creates = [r for r in report if r["action"] == "create"]
    return updates, creates


def require_team_for_creates(creates: list, team: str):
    if creates and not team:
        raise click.UsageError(
            "--team is required when match report contains creates"
        )


def load_state_map(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text())
    return DEFAULT_LIST_TO_STATE


def validate_states(creates: list, list_to_state: dict):
    trello_lists = {e.get("trello_list", "") for e in creates}
    unmapped = {
        name
        for name in trello_lists
        if name not in list_to_state and not name.startswith("Doing")
    }
    if not unmapped:
        return
    click.echo("FAIL: Trello lists with no state mapping:\n")
    for name in sorted(unmapped):
        click.echo(f"  ✗ {name}")
    click.echo("\nCurrent mappings:")
    for src, tgt in sorted(list_to_state.items()):
        click.echo(f"  {src} → {tgt}")
    click.echo("\nProvide a --state-map JSON file or add mappings.")
    raise SystemExit(1)


def dry_run_payloads(
    updates: list,
    creates: list,
    team: str,
    project: str,
    list_to_state: dict,
    match_report: str,
):
    out_dir = Path(match_report).parent / "cards"
    out_dir.mkdir(exist_ok=True)
    for i, entry in enumerate(updates + creates):
        payload = build_payload(entry, team, project, list_to_state)
        write_payload_file(payload, out_dir, i)
        display_entry(payload, i)
    click.echo(
        f"\n[DRY RUN] {len(updates)} updates, {len(creates)} creates written to {out_dir}/"
    )
    click.echo("Run with --apply to push to Linear.")


def apply_to_linear(
    updates: list,
    creates: list,
    api_key_env: str,
    team: str,
    project: str,
    list_to_state: dict,
):
    if not api_key_env:
        raise click.UsageError("--api-key-env is required when using --apply")
    if creates and not project:
        raise click.UsageError(
            "--project is required when the match report contains creates"
        )

    api_key = require_env(api_key_env)
    team_id = resolve_by_name(api_key, "teams", team) if team else None
    project_id = (
        resolve_by_name(api_key, "projects", project) if project else None
    )
    state_ids = resolve_state_ids(api_key, team_id) if team_id else {}

    updated = apply_updates(api_key, updates)
    created = apply_creates(
        api_key, team_id, project_id, state_ids, list_to_state, creates
    )
    click.echo(
        f"\nApplied: {updated}/{len(updates)} updates, "
        f"{created}/{len(creates)} creates"
    )


def resolve_state_ids(api_key: str, team_id: str) -> dict:
    states = resolve_states(api_key, team_id)
    return {name: s["id"] for name, s in states.items()}


def apply_updates(api_key: str, updates: list) -> int:
    applied = 0
    for i, entry in enumerate(updates):
        if apply_one_update(api_key, entry, i):
            applied += 1
        throttle(applied)
    return applied


def apply_one_update(api_key: str, entry: dict, index: int) -> bool:
    issue_id = entry["linear_id"]
    title = entry["linear_title"]
    description = format_description(entry)
    try:
        update_issue(api_key, issue_id, description=description)
    except LinearError as e:
        click.echo(f"  ✗ {index + 1}. [UPDATE] {issue_id} — {title[:50]} — {e}")
        return False
    click.echo(f"  ✓ {index + 1}. [UPDATE] {issue_id} — {title[:50]}")
    return True


def apply_creates(
    api_key: str,
    team_id: str,
    project_id: str,
    state_ids: dict,
    list_to_state: dict,
    creates: list,
) -> int:
    applied = 0
    for i, entry in enumerate(creates):
        if apply_one_create(
            api_key, team_id, project_id, state_ids, list_to_state, entry, i
        ):
            applied += 1
        throttle(applied)
    return applied


def apply_one_create(
    api_key: str,
    team_id: str,
    project_id: str,
    state_ids: dict,
    list_to_state: dict,
    entry: dict,
    index: int,
) -> bool:
    state_name = state_for(entry, list_to_state)
    state_id = state_ids.get(state_name)
    if not state_id:
        click.echo(
            f"  ✗ {index + 1}. [CREATE] {entry['trello_name'][:50]} — unknown state '{state_name}'"
        )
        return False
    title = entry["trello_name"]
    try:
        create_issue(
            api_key,
            team_id=team_id,
            project_id=project_id,
            state_id=state_id,
            title=title,
            description=format_description(entry),
        )
    except LinearError as e:
        click.echo(f"  ✗ {index + 1}. [CREATE] {title[:50]} — {e}")
        return False
    click.echo(f"  ✓ {index + 1}. [CREATE] {title[:50]}")
    return True


def throttle(count: int):
    if count and count % 10 == 0:
        time.sleep(0.5)


def build_payload(
    entry: dict, team: str, project: str | None, list_to_state: dict
) -> dict:
    if entry["action"] == "update":
        return {
            "action": "update",
            "id": entry["linear_id"],
            "title": entry["linear_title"],
            "description": format_description(entry),
            "trello_url": entry.get("trello_url", ""),
        }
    payload = {
        "action": "create",
        "title": entry["trello_name"],
        "description": format_description(entry),
        "team": team,
        "state": state_for(entry, list_to_state),
        "trello_url": entry.get("trello_url", ""),
    }
    if project:
        payload["project"] = project
    return payload


def state_for(entry: dict, list_to_state: dict) -> str:
    trello_list = entry.get("trello_list", "")
    if trello_list.startswith("Doing"):
        return "Todo"
    return list_to_state[trello_list]


def format_description(entry: dict) -> str:
    parts = []

    if desc := entry.get("trello_description", ""):
        parts.append(desc)

    if comments := entry.get("trello_comments", []):
        parts.append(format_comments(comments))

    url = entry.get("trello_url", "")
    source = "Linear" if "linear.app" in url else "Trello"
    parts.append(f"---\n*Migrated from {source}: {url}*")
    return "\n\n".join(parts)


def format_comments(comments: list[dict]) -> str:
    lines = ["## Comments (from Trello)\n"]
    for c in comments:
        author = c.get("author", "Unknown")
        date = c.get("date", "")[:10]
        text = c.get("text", "")
        lines.append(f"**{author}** ({date}):\n{text}\n")
    return "\n".join(lines)


def write_payload_file(payload: dict, out_dir: Path, index: int):
    path = out_dir / f"{index:03d}.json"
    path.write_text(json.dumps(payload, indent=2))


def display_entry(payload: dict, index: int):
    action = payload["action"].upper()
    label = payload.get("id", "NEW")
    desc_preview = payload["description"][:80].replace("\n", " ")
    click.echo(
        f"[DRY RUN] {index + 1}. [{action}] {label} — {payload['title']}"
    )
    click.echo(f"   {desc_preview}...")


if __name__ == "__main__":
    main()
