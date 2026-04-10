"""Download images from source workspace and re-upload to target workspace."""

import json
import re
from pathlib import Path

import click
import requests
from linear_api import graphql, require_env


@click.command()
@click.option(
    "--source-api-key-env",
    required=True,
    help="Env var for source workspace API key",
)
@click.option(
    "--target-api-key-env",
    required=True,
    help="Env var for target workspace API key",
)
@click.option("--export-dir", required=True, type=click.Path(exists=True))
@click.option("--target-team", required=True)
@click.option("--target-project", required=True)
@click.option("--dry-run", is_flag=True, default=False)
def main(
    source_api_key_env: str,
    target_api_key_env: str,
    export_dir: str,
    target_team: str,
    target_project: str,
    dry_run: bool,
):
    source_key = require_env(source_api_key_env)
    target_key = require_env(target_api_key_env)

    cards = load_cards_with_images(Path(export_dir))
    if not cards:
        click.echo("No issues with images found.")
        return

    click.echo(
        f"Found {len(cards)} issues ({sum(len(c['images']) for c in cards)} images)"
    )

    target_issues = fetch_target_issues(target_key, target_team, target_project)

    for card in cards:
        signed = fetch_signed_urls(source_key, card["id"])
        url_map = migrate_all_images(
            target_key, card["images"], signed, dry_run
        )
        if url_map and not dry_run:
            append_images_to_issue(
                target_key, target_issues, card["title"], url_map
            )


def load_cards_with_images(export_dir: Path) -> list:
    cards = json.loads((export_dir / "all_cards.json").read_text())
    return [
        {"id": c["id"], "title": c["title"], "images": imgs}
        for c in cards
        if (imgs := find_image_refs(c.get("description", "")))
    ]


def find_image_refs(text: str) -> list:
    return re.findall(
        r"!\[([^\]]*)\]\((https://uploads\.linear\.app/[^)]+)\)", text
    )


def fetch_signed_urls(api_key: str, issue_id: str) -> dict:
    query = f'{{ issue(id: "{issue_id}") {{ description }} }}'
    desc = graphql(api_key, query)["data"]["issue"]["description"]
    return {url_path(url): url for _, url in find_image_refs(desc)}


def url_path(url: str) -> str:
    return "/".join(url.split("?")[0].split("/")[-2:])


def migrate_all_images(
    target_key: str, images: list, signed: dict, dry_run: bool
) -> dict:
    url_map = {}
    for alt, old_url in images:
        signed_url = signed.get(url_path(old_url))
        if not signed_url:
            click.echo(f"  ✗ No signed URL for {alt}")
            continue
        if dry_run:
            click.echo(f"  [DRY RUN] {alt}")
            continue
        result = download_and_upload(target_key, alt, signed_url)
        if result:
            url_map[old_url] = result
    return url_map


def download_and_upload(
    target_key: str, alt: str, signed_url: str
) -> tuple | None:
    resp = requests.get(signed_url)
    if resp.status_code != 200:
        click.echo(f"  ✗ Download failed: {resp.status_code}")
        return None

    content_type = resp.headers.get("content-type", "image/png")
    new_url = upload_to_target(target_key, alt, resp.content, content_type)
    if new_url:
        click.echo(f"  ✓ {alt}")
        return (alt, new_url)
    return None


def upload_to_target(
    api_key: str, filename: str, data: bytes, content_type: str
) -> str | None:
    upload_info = request_upload_url(api_key, filename, len(data), content_type)
    return put_image(upload_info, data, content_type)


def request_upload_url(
    api_key: str, filename: str, size: int, content_type: str
) -> dict:
    mutation = f"""mutation {{
        fileUpload(contentType: "{content_type}", filename: "{filename}", size: {size}) {{
            success
            uploadFile {{ uploadUrl assetUrl headers {{ key value }} }}
        }}
    }}"""
    return graphql(api_key, mutation)["data"]["fileUpload"]["uploadFile"]


def put_image(upload_info: dict, data: bytes, content_type: str) -> str | None:
    headers = {"Content-Type": content_type}
    for h in upload_info["headers"]:
        headers[h["key"]] = h["value"]
    resp = requests.put(upload_info["uploadUrl"], data=data, headers=headers)
    return upload_info["assetUrl"] if resp.status_code in (200, 201) else None


def append_images_to_issue(
    api_key: str, target_issues: list, title: str, url_map: dict
):
    issue = next((i for i in target_issues if i["title"] == title), None)
    if not issue:
        click.echo(f"  ✗ Target not found: {title[:60]}")
        return

    img_md = "\n\n".join(f"![{alt}]({url})" for alt, url in url_map.values())
    new_desc = (issue.get("description", "") + "\n\n" + img_md).strip()
    update_issue(api_key, issue["id"], new_desc, title)


def update_issue(api_key: str, issue_id: str, description: str, title: str):
    desc_json = json.dumps(description)
    mutation = f"""mutation {{
        issueUpdate(id: "{issue_id}", input: {{ description: {desc_json} }}) {{ success }}
    }}"""
    result = graphql(api_key, mutation)
    success = (
        result.get("data", {}).get("issueUpdate", {}).get("success", False)
    )
    click.echo(
        f"  {'✓' if success else '✗'} {title[:60]}: {'updated' if success else 'failed'}"
    )


def fetch_target_issues(api_key: str, team: str, project: str) -> list:
    query = f"""{{ issues(filter: {{
        team: {{ name: {{ eq: "{team}" }} }}
        project: {{ name: {{ eq: "{project}" }} }}
    }}, first: 250) {{ nodes {{ id title description }} }} }}"""
    return graphql(api_key, query)["data"]["issues"]["nodes"]


if __name__ == "__main__":
    main()
