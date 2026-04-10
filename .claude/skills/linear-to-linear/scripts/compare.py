"""Compare source and target issues, flag and fix truncation or missing content."""

import json
import re
import time
from pathlib import Path

import click
from linear_api import graphql, require_env

TOLERANCE = 100


@click.command()
@click.option("--target-api-key-env", required=True)
@click.option("--target-team", required=True)
@click.option("--target-project", required=True)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
@click.option(
    "--fix", is_flag=True, default=False, help="Auto-fix flagged issues"
)
def main(
    target_api_key_env: str,
    target_team: str,
    target_project: str,
    export_dir: str,
    fix: bool,
):
    target_key = require_env(target_api_key_env)
    cards = json.loads((Path(export_dir) / "all_cards.json").read_text())
    target_by_title = {
        i["title"]: i
        for i in fetch_issues(target_key, target_team, target_project)
    }

    problems = [
        p for card in cards if (p := compare_one(card, target_by_title))
    ]
    report_problems(problems)

    if fix and problems:
        fix_problems(target_key, problems)


def fetch_issues(api_key: str, team: str, project: str) -> list:
    issues, cursor = [], None
    while True:
        after = f', after: "{cursor}"' if cursor else ""
        query = f"""{{ issues(filter: {{
            team: {{ name: {{ eq: "{team}" }} }}
            project: {{ name: {{ eq: "{project}" }} }}
        }}, first: 250 {after}) {{
            nodes {{ id title description }}
            pageInfo {{ hasNextPage endCursor }}
        }} }}"""
        data = graphql(api_key, query)["data"]["issues"]
        issues.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            break
        cursor = data["pageInfo"]["endCursor"]
    return issues


def compare_one(card: dict, target_by_title: dict) -> dict | None:
    target = target_by_title.get(card["title"])
    if not target:
        return None

    expected = build_expected(card)
    actual = target.get("description") or ""
    issues = check_content(expected, actual)

    if not issues:
        return None
    return {
        "title": card["title"],
        "target_id": target["id"],
        "expected": expected,
        "issues": issues,
    }


def build_expected(card: dict) -> str:
    parts = []
    if desc := card.get("description", ""):
        parts.append(desc)
    if card.get("comments"):
        comments = "\n\n".join(
            f"**{c['author']}** ({c['date'][:10]}):\n{c['text']}"
            for c in card["comments"]
        )
        parts.append("## Comments\n\n" + comments)
    return "\n\n".join(parts)


def check_content(expected: str, actual: str) -> list:
    issues = []
    if len(expected) > len(actual) + TOLERANCE:
        issues.append(
            f"truncated: expected {len(expected)} chars, got {len(actual)}"
        )
    if "## Comments" in expected and "## Comments" not in actual:
        issues.append("missing comments section")
    if missing_images(expected, actual):
        issues.append("missing image references")
    return issues


def missing_images(expected: str, actual: str) -> bool:
    expected_alts = set(re.findall(r"!\[([^\]]*)\]", expected))
    actual_alts = set(re.findall(r"!\[([^\]]*)\]", actual))
    return bool(expected_alts - actual_alts)


def report_problems(problems: list):
    if not problems:
        click.echo("PASS: all issues match source content")
        return

    click.echo(f"Found {len(problems)} issues with problems:\n")
    for p in problems:
        click.echo(f"  {p['title'][:60]}")
        for issue in p["issues"]:
            click.echo(f"    - {issue}")


def fix_problems(target_key: str, problems: list):
    click.echo(f"\nFixing {len(problems)} issues...")
    fixed = 0
    for p in problems:
        desc_json = json.dumps(p["expected"])
        query = f'mutation {{ issueUpdate(id: "{p["target_id"]}", input: {{ description: {desc_json} }}) {{ success }} }}'
        result = graphql(target_key, query)
        success = (
            result.get("data", {}).get("issueUpdate", {}).get("success", False)
        )
        click.echo(f"  {'✓' if success else '✗'} {p['title'][:60]}")
        fixed += success
        if fixed % 10 == 0:
            time.sleep(0.5)
    click.echo(f"\nFixed {fixed}/{len(problems)}")


if __name__ == "__main__":
    main()
