"""Compare source and target issues, flag and fix truncation or missing content."""

import json
import re
import time
from pathlib import Path

import click

from linear_client import (
    LinearError,
    graphql,
    list_issues,
    normalize_quotes,
    require_env,
    resolve_by_name,
    update_issue,
)

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
    export_path = Path(export_dir)
    cards = json.loads((export_path / "all_cards.json").read_text())
    target_by_title = {
        i["title"]: i
        for i in fetch_issues(target_key, target_team, target_project)
    }

    problems = [
        p for card in cards if (p := compare_one(card, target_by_title))
    ]
    report_problems(problems)

    meta_problems = compare_project_meta(
        target_key, target_project, export_path
    )
    report_meta_problems(meta_problems)

    if fix and problems:
        fix_problems(target_key, problems)


def fetch_issues(api_key: str, team: str, project: str) -> list:
    project_id = resolve_by_name(api_key, "projects", project)
    return list_issues(api_key, project_id=project_id)


def compare_one(card: dict, target_by_title: dict) -> dict | None:
    target = target_by_title.get(card["title"])
    if not target:
        return None

    expected = build_expected(card)
    actual = normalize_quotes(target.get("description") or "")
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
        parts.append(format_comments_section(card["comments"]))
    return "\n\n".join(parts)


def format_comments_section(comments: list) -> str:
    body = "\n\n".join(
        f"**{c['author']}** ({c['date'][:10]}):\n{c['text']}" for c in comments
    )
    return "## Comments\n\n" + body


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
        try:
            update_issue(target_key, p["target_id"], description=p["expected"])
            click.echo(f"  ✓ {p['title'][:60]}")
            fixed += 1
        except LinearError as e:
            click.echo(f"  ✗ {p['title'][:60]} — {e}")
        if fixed % 10 == 0:
            time.sleep(0.5)
    click.echo(f"\nFixed {fixed}/{len(problems)}")


PROJECT_META_QUERY = """{{
    projects(filter: {{ name: {{ eq: "{project}" }} }}) {{
        nodes {{
            name description content
            projectUpdates(first: 50) {{ nodes {{ body health }} }}
            externalLinks {{ nodes {{ label url }} }}
        }}
    }}
}}"""


def fetch_target_project_meta(api_key: str, project: str) -> dict | None:
    data = graphql(api_key, PROJECT_META_QUERY.format(project=project))
    nodes = data["data"]["projects"]["nodes"]
    return nodes[0] if nodes else None


def load_json_file(path: Path) -> list | dict:
    return json.loads(path.read_text()) if path.exists() else []


def compare_project_meta(api_key: str, project: str, export_dir: Path) -> list:
    target = fetch_target_project_meta(api_key, project)
    if not target:
        return [f"target project '{project}' not found"]

    source_info = load_json_file(export_dir / "project.json") or {}
    source_updates = load_json_file(export_dir / "project_updates.json")
    source_links = load_json_file(export_dir / "project_links.json")

    return [
        *compare_project_fields(source_info, target),
        *compare_project_updates(source_updates, target),
        *compare_project_links(source_links, target),
    ]


def compare_project_fields(source: dict, target: dict) -> list:
    problems = []
    if source.get("description", "") != normalize_quotes(
        target.get("content") or ""
    ):
        problems.append("project description differs from source")
    if source.get("summary", "") != normalize_quotes(
        target.get("description") or ""
    ):
        problems.append("project summary differs from source")
    return problems


def compare_project_updates(source: list, target: dict) -> list:
    target_bodies = {
        normalize_quotes(u["body"]) for u in target["projectUpdates"]["nodes"]
    }
    missing = [u["body"][:60] for u in source if u["body"] not in target_bodies]
    return [f"missing project update: {body}" for body in missing]


def compare_project_links(source: list, target: dict) -> list:
    target_urls = {ln["url"] for ln in target["externalLinks"]["nodes"]}
    missing = [ln for ln in source if ln["url"] not in target_urls]
    return [
        f"missing resource link: {ln['label']} → {ln['url']}" for ln in missing
    ]


def report_meta_problems(problems: list):
    if not problems:
        click.echo("PASS: project description, updates, and links match source")
        return
    click.echo(f"\nProject metadata problems ({len(problems)}):")
    for p in problems:
        click.echo(f"  - {p}")


if __name__ == "__main__":
    main()
