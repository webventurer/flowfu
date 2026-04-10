"""Post-migration checks: counts, titles, and description content."""

import click
from linear_api import load_source_cards, load_target_issues_file


@click.command()
@click.option("--source-dir", required=True, type=click.Path(exists=True))
@click.option("--target-file", required=True, type=click.Path(exists=True))
def main(source_dir: str, target_file: str):
    source = load_source_cards(source_dir)
    target = load_target_issues_file(target_file)

    check_counts(source, target)
    check_titles(source, target)
    check_descriptions(source, target)


def check_counts(source: list, target: list):
    click.echo(f"Source cards: {len(source)}")
    click.echo(f"Target issues: {len(target)}")
    if len(source) == len(target):
        click.echo("  PASS: counts match")
    else:
        click.echo(f"  FAIL: {abs(len(source) - len(target))} difference")


def check_titles(source: list, target: list):
    source_titles = {c["title"] for c in source}
    target_titles = {i["title"] for i in target}
    missing = source_titles - target_titles
    extra = target_titles - source_titles

    if not missing and not extra:
        click.echo("  PASS: all titles match")
        return

    if missing:
        click.echo(f"  FAIL: {len(missing)} missing from target:")
        for t in sorted(missing)[:10]:
            click.echo(f"    - {t[:70]}")
    if extra:
        click.echo(f"  WARN: {len(extra)} extra in target:")
        for t in sorted(extra)[:10]:
            click.echo(f"    + {t[:70]}")


def check_descriptions(source: list, target: list):
    target_by_title = {i["title"]: i for i in target}
    checked, passed = 0, 0

    for card in source:
        issue = target_by_title.get(card["title"])
        if not issue:
            continue
        if description_matches(card, issue):
            passed += 1
        checked += 1

    click.echo(f"  Descriptions: {passed}/{checked} contain source content")
    if passed < checked:
        click.echo(f"  WARN: {checked - passed} descriptions missing content")


def description_matches(card: dict, issue: dict) -> bool:
    source_desc = card.get("description", "")
    target_desc = issue.get("description", "") or ""
    return not source_desc or source_desc in target_desc


if __name__ == "__main__":
    main()
