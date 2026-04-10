import json
from pathlib import Path

import click

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
    "--team", default=None, help="Linear team name (required for creates)"
)
@click.option(
    "--project",
    default=None,
    help="Linear project name (optional, for creates)",
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
    help="Show what would change (default)",
)
def main(match_report: str, team: str, project: str, state_map: str, mode: str):
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

    out_dir = prepare_output_dir(match_report)
    write_all_payloads(
        updates + creates, team, project, list_to_state, out_dir, mode
    )
    report_summary(updates, creates, out_dir, mode)


def split_by_action(report: list) -> tuple:
    updates = [r for r in report if r["action"] == "update"]
    creates = [r for r in report if r["action"] == "create"]
    return updates, creates


def require_team_for_creates(creates: list, team: str):
    if creates and not team:
        raise click.UsageError(
            "--team is required when match report contains creates"
        )


def prepare_output_dir(match_report: str) -> Path:
    out_dir = Path(match_report).parent / "cards"
    out_dir.mkdir(exist_ok=True)
    return out_dir


def write_all_payloads(
    entries: list,
    team: str,
    project: str,
    list_to_state: dict,
    out_dir: Path,
    mode: str,
):
    for i, entry in enumerate(entries):
        payload = build_payload(entry, team, project, list_to_state)
        write_payload_file(payload, out_dir, i)
        display_entry(payload, mode, i)


def report_summary(updates: list, creates: list, out_dir: Path, mode: str):
    prefix = "[DRY RUN] " if mode == "dry-run" else ""
    click.echo(
        f"\n{prefix}{len(updates)} updates, {len(creates)} creates written to {out_dir}/"
    )
    if mode == "dry-run":
        click.echo("Run with --apply to push to Linear via the agent.")


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


def display_entry(payload: dict, mode: str, index: int):
    prefix = "[DRY RUN] " if mode == "dry-run" else ""
    action = payload["action"].upper()
    label = payload.get("id", "NEW")
    desc_preview = payload["description"][:80].replace("\n", " ")
    click.echo(f"{prefix}{index + 1}. [{action}] {label} — {payload['title']}")
    click.echo(f"   {desc_preview}...")


if __name__ == "__main__":
    main()
