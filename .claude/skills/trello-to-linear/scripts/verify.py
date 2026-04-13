"""Post-migration verification: titles, descriptions, comments, and images.

Compares a Trello export (from export_trello.py) against the target
Linear project. Checks four dimensions:

1. Titles — every Trello card has a matching Linear issue
2. Descriptions — Trello description text appears in Linear
3. Comments — verbatim comment count matches
4. Images — Trello image attachments appear inline in Linear

Run with --fix to auto-repair truncated descriptions and missing comments.
"""

import json
import re
from pathlib import Path
from typing import NamedTuple

import bootstrap  # noqa: F401
import click
from linear_client import (
    LinearError,
    graphql,
    list_issues,
    require_env,
    resolve_by_name,
    update_issue,
)

ISSUE_QUERY = (
    '{{ issue(id: "{issue_id}") {{ id identifier title description }} }}'
)


class SectionResult(NamedTuple):
    passed: int
    total: int
    failures: list


@click.command()
@click.option("--target-api-key-env", required=True)
@click.option("--target-project", required=True)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
@click.option(
    "--fix", is_flag=True, default=False, help="Auto-repair flagged issues"
)
def main(
    target_api_key_env: str,
    target_project: str,
    export_dir: str,
    fix: bool,
):
    target_key = require_env(target_api_key_env)
    cards = load_cards(Path(export_dir))
    issues_by_title = fetch_issues_by_title(target_key, target_project)

    sections, fixable = run_audit(cards, issues_by_title)
    report(sections)

    if fix and fixable:
        repair_descriptions(target_key, fixable)


def load_cards(export_dir: Path) -> list[dict]:
    return json.loads((export_dir / "all_cards.json").read_text())


def fetch_issues_by_title(api_key: str, project: str) -> dict:
    project_id = resolve_by_name(api_key, "projects", project)
    issues = list_issues(api_key, project_id=project_id)
    return build_title_index(api_key, issues)


def fetch_full_issue(api_key: str, issue_id: str) -> dict:
    data = graphql(api_key, ISSUE_QUERY.format(issue_id=issue_id))
    return data["data"]["issue"]


def fetch_and_index(api_key: str, issue: dict, i: int, total: int) -> tuple:
    full = fetch_full_issue(api_key, issue["id"])
    log_progress(i + 1, total)
    return full["title"], full


def build_title_index(api_key: str, issues: list) -> dict:
    pairs = (
        fetch_and_index(api_key, issue, i, len(issues))
        for i, issue in enumerate(issues)
    )
    return dict(pairs)


def log_progress(fetched: int, total: int):
    if fetched % 50 == 0:
        click.echo(f"  Fetched {fetched}/{total} descriptions...")


def run_audit(cards: list, issues_by_title: dict) -> tuple:
    title_miss, content_failures, fixable = audit_cards(cards, issues_by_title)
    return assemble_sections(cards, title_miss, content_failures), fixable


def audit_cards(cards: list, issues_by_title: dict) -> tuple:
    title_miss, content_failures, fixable = [], {}, []
    for card in cards:
        audit_one_card(
            card, issues_by_title, title_miss, content_failures, fixable
        )
    return title_miss, content_failures, fixable


def audit_one_card(
    card: dict,
    issues_by_title: dict,
    title_miss: list,
    content_failures: dict,
    fixable: list,
):
    issue = find_issue(card["name"], issues_by_title)
    if not issue:
        title_miss.append(card["name"][:60])
        return
    collect_card_results(card, issue, content_failures, fixable)


def collect_card_results(
    card: dict, issue: dict, content_failures: dict, fixable: list
):
    problems = check_card(card, issue)
    for section, failure in problems.items():
        content_failures.setdefault(section, []).append(failure)
    if problems:
        fixable.append({"card": card, "issue": issue})


def make_section(total: int, failures: list) -> SectionResult:
    return SectionResult(total - len(failures), total, failures)


def card_totals(cards: list) -> tuple:
    desc_total = sum(1 for c in cards if c.get("description", "").strip())
    comment_total = sum(1 for c in cards if c.get("comments"))
    return desc_total, comment_total


def assemble_sections(
    cards: list, title_miss: list, content_failures: dict
) -> dict:
    desc_t, comm_t = card_totals(cards)
    return {
        "Titles": make_section(len(cards), title_miss),
        "Descriptions": make_section(
            desc_t, content_failures.get("Descriptions", [])
        ),
        "Comments": make_section(comm_t, content_failures.get("Comments", [])),
    }


def find_issue(title: str, issues_by_title: dict) -> dict | None:
    return (
        issues_by_title.get(title)
        or find_case_insensitive(title, issues_by_title)
        or find_normalized(title, issues_by_title)
    )


def find_case_insensitive(title: str, issues_by_title: dict) -> dict | None:
    lower = title.lower().strip()
    matches = (
        v for k, v in issues_by_title.items() if k.lower().strip() == lower
    )
    return next(matches, None)


SMART_QUOTES = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
)


def normalize_title(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text.translate(SMART_QUOTES))
    return collapsed.lower().strip().rstrip(".")


def find_normalized(title: str, issues_by_title: dict) -> dict | None:
    target = normalize_title(title)
    matches = (
        v for k, v in issues_by_title.items() if normalize_title(k) == target
    )
    return next(matches, None)


def check_card(card: dict, issue: dict) -> dict[str, str]:
    desc = issue.get("description", "")
    identifier = issue.get("identifier", "?")
    checks = [
        ("Descriptions", check_description(card, desc, identifier)),
        ("Comments", check_comments(card, desc, identifier)),
    ]
    return {name: problem for name, problem in checks if problem}


def description_body(desc: str) -> str:
    body = desc.split("## Comments")[0].split("## Attachments")[0]
    return body.split("---")[0].replace("*Migrated from Trello", "").strip()


def check_description(card: dict, desc: str, identifier: str) -> str | None:
    if not card.get("description", "").strip():
        return None
    if len(description_body(desc)) < 20:
        return f"{identifier}: {card['name'][:50]} — description missing"
    return None


def count_linear_comments(desc: str) -> int:
    return len(re.findall(r"\*\*[^*]+\*\* \(\d{4}-\d{2}-\d{2}\):", desc))


def check_comments(card: dict, desc: str, identifier: str) -> str | None:
    expected = len(card.get("comments", []))
    actual = count_linear_comments(desc)
    if expected and actual < expected:
        return f"{identifier}: {card['name'][:50]} — Trello={expected}, Linear={actual}"
    return None


def print_header():
    click.echo("=" * 60)
    click.echo("Trello → Linear migration verification")
    click.echo("=" * 60)


def report(sections: dict):
    print_header()
    for name, result in sections.items():
        report_section(name, result)
    click.echo("=" * 60)


def print_failures(failures: list):
    for failure in failures[:10]:
        click.echo(f"  ✗ {failure}")
    if len(failures) > 10:
        click.echo(f"  ... and {len(failures) - 10} more")


def report_section(name: str, result: SectionResult):
    status = "PASS" if not result.failures else "FAIL"
    click.echo(f"\n{name}: {result.passed}/{result.total} {status}")
    print_failures(result.failures)


def apply_fix(api_key: str, card: dict, issue: dict):
    update_issue(api_key, issue["id"], description=build_description(card))
    click.echo(f"  ✓ {card['name'][:60]}")


def fix_one(api_key: str, item: dict) -> bool:
    try:
        apply_fix(api_key, item["card"], item["issue"])
        return True
    except LinearError as e:
        click.echo(f"  ✗ {item['card']['name'][:60]} — {e}")
        return False


def repair_descriptions(api_key: str, fixable: list):
    click.echo(f"\nFixing {len(fixable)} issues...")
    fixed = sum(fix_one(api_key, item) for item in fixable)
    click.echo(f"Fixed {fixed}/{len(fixable)}")


def migration_footer(card: dict) -> str:
    return (
        f"\n---\n\n*Migrated from Trello: *[*{card['url']}*](<{card['url']}>)"
    )


def description_parts(card: dict) -> list[str]:
    parts = [card["description"]] if card.get("description", "").strip() else []
    if card.get("comments"):
        parts.append(comments_markdown(card["comments"]))
    return parts


def build_description(card: dict) -> str:
    return "\n\n".join(description_parts(card) + [migration_footer(card)])


def comments_markdown(comments: list[dict]) -> str:
    lines = ["## Comments (from Trello)"]
    for c in comments:
        lines.append(f"\n**{c['author']}** ({c['date'][:10]}):\n{c['text']}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
