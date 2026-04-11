"""Match source issues to target by title, write match report and cards/ payloads."""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

import click
from skill_io import load_source_cards, load_target_issues_file


@click.command()
@click.option("--source-dir", required=True, type=click.Path(exists=True))
@click.option("--target-file", required=True, type=click.Path(exists=True))
@click.option("--threshold", default=0.85, help="Fuzzy match threshold (0-1)")
def main(source_dir: str, target_file: str, threshold: float):
    source_dir = Path(source_dir)
    source_cards = load_source_cards(str(source_dir))
    target_issues = load_target_issues_file(target_file)
    report = build_match_report(source_cards, target_issues, threshold)

    write_match_report(report, source_dir)
    write_cards(report, source_dir)
    print_summary(report)


def build_match_report(
    source_cards: list, target_issues: list, threshold: float
) -> list:
    target_by_title = {normalise(i["title"]): i for i in target_issues}
    return [
        find_match(card, target_by_title, threshold) for card in source_cards
    ]


def find_match(card: dict, target_by_title: dict, threshold: float) -> dict:
    normalised = normalise(card["title"])
    entry = source_entry(card)

    if exact := target_by_title.get(normalised):
        return entry | target_fields(exact, "exact")

    if fuzzy := best_fuzzy_match(normalised, target_by_title, threshold):
        return entry | target_fields(fuzzy, "fuzzy")

    return entry | {"action": "create"}


def source_entry(card: dict) -> dict:
    return {
        "source_title": card["title"],
        "source_state": card.get("state", ""),
        "source_description": card.get("description", ""),
        "source_labels": card.get("labels", []),
        "source_attachments": card.get("attachments", []),
        "source_comments": card.get("comments", []),
    }


def target_fields(issue: dict, match_type: str) -> dict:
    has_desc = bool(issue.get("description"))
    return {
        "target_id": issue.get("id", ""),
        "target_identifier": issue.get("identifier", ""),
        "target_title": issue.get("title", ""),
        "target_has_description": has_desc,
        "match_type": match_type,
        "action": "skip" if has_desc else "update",
    }


def write_match_report(report: list, source_dir: Path):
    path = source_dir / "match-report.json"
    path.write_text(json.dumps(report, indent=2))
    click.echo(f"Match report written to {path}")


def write_cards(report: list, source_dir: Path):
    cards_dir = source_dir / "cards"
    cards_dir.mkdir(exist_ok=True)
    actionable = [r for r in report if r["action"] in ("create", "update")]

    for i, entry in enumerate(actionable):
        payload = build_card_payload(entry)
        (cards_dir / f"{i:03d}.json").write_text(json.dumps(payload, indent=2))

    click.echo(f"{len(actionable)} card(s) written to {cards_dir}/")


def build_card_payload(entry: dict) -> dict:
    return {
        "action": entry["action"],
        "title": entry["source_title"],
        "description": format_description(entry),
        "state": entry.get("source_state", "Backlog"),
        "labels": entry.get("source_labels", []),
        "attachments": entry.get("source_attachments", []),
    }


def format_description(entry: dict) -> str:
    parts = []
    if desc := entry.get("source_description", ""):
        parts.append(desc)
    if comments := entry.get("source_comments", []):
        parts.append(format_comments(comments))
    return "\n\n".join(parts)


def format_comments(comments: list) -> str:
    lines = ["## Comments\n"]
    for c in comments:
        author = c.get("author", "Unknown")
        date = c.get("date", "")[:10]
        text = c.get("text", "")
        lines.append(f"**{author}** ({date}):\n{text}\n")
    return "\n".join(lines)


def best_fuzzy_match(
    name: str, target_by_title: dict, threshold: float
) -> dict | None:
    best_score, best_issue = 0.0, None
    for title, issue in target_by_title.items():
        score = SequenceMatcher(None, name, title).ratio()
        if score > best_score:
            best_score, best_issue = score, issue
    return best_issue if best_score >= threshold else None


def normalise(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text.lower().strip())
    return re.sub(r"\s+", " ", text)


def print_summary(report: list):
    updates = sum(1 for r in report if r["action"] == "update")
    creates = sum(1 for r in report if r["action"] == "create")
    skips = sum(1 for r in report if r["action"] == "skip")
    fuzzy = sum(1 for r in report if r.get("match_type") == "fuzzy")

    click.echo(f"Total cards: {len(report)}")
    click.echo(f"  Update (empty in target):   {updates}")
    click.echo(f"  Create (no match):          {creates}")
    click.echo(f"  Skip (already has desc):    {skips}")
    click.echo(f"  Fuzzy matches (review):     {fuzzy}")


if __name__ == "__main__":
    main()
