"""Skill-specific file loaders for migration JSON artifacts.

These are not part of the reusable Linear client — they know the shape
of the export/match JSON files that linear-to-linear produces.
"""

import json
from pathlib import Path


def load_source_cards(source_dir: str) -> list:
    cards = []
    for f in sorted(Path(source_dir).glob("[0-9]*.json")):
        cards.extend(json.loads(f.read_text()))
    return cards


def load_target_issues_file(path: str) -> list:
    raw = json.loads(Path(path).read_text())
    if isinstance(raw, list) and raw and "text" in raw[0]:
        return json.loads(raw[0]["text"]).get("issues", [])
    if isinstance(raw, dict):
        return raw.get("issues", [])
    return raw
