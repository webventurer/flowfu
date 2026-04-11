---
name: trello-to-linear
description: Migrate Trello cards to Linear issues — descriptions, comments, and checklists. Use when migrating from Trello to Linear or recovering lost content. Triggers on "trello to linear", "migrate trello", "sync descriptions".
---

**CRITICAL**: Read and follow EVERY step in `WORKFLOW.md`

# Trello to Linear

> Deterministic migration of Trello card content (descriptions, comments, checklists) into Linear issues, matched by title.

---

## When to use

- Migrating a Trello board to Linear and descriptions/comments didn't come across
- Recovering content after a bulk card move lost descriptions
- Backfilling Linear issues with historical Trello context

## When NOT to use

- One-off card lookups — use the Trello MCP tools interactively

---

## Quick reference

<mark>**Three scripts, three phases: export → match → update. Always dry-run first.**</mark>

---

## Skill documents

| Document | Purpose |
|:---------|:--------|
| [WORKFLOW.md](WORKFLOW.md) | Step-by-step execution phases |
| [PREPARE.md](PREPARE.md) | Session setup and cleanup |

---

## Scripts

All scripts live in `scripts/` and follow the `/script` skill conventions.

| Script | Phase | What it does |
|:-------|:------|:-------------|
| `export_trello.py` | Export | Pulls all cards from a Trello board (including archived lists) — descriptions, comments, checklists — writes one JSON per list |
| `match.py` | Match | Reads Trello export + Linear issues, matches by title (exact → normalised → fuzzy), writes match report |
| `check_states.py` | Check | Validates that all mapped state names exist in the target Linear workspace. Run before upsert |
| `update_linear.py` | Upsert | Reads match report, updates existing issues and creates missing ones. `--dry-run` by default |
| `verify.py` | Verify | Compares Trello export against Linear issues — checks counts, titles, order, and descriptions |

### Running

Pipeline artifacts go to `/tmp/trello-export` so they never touch the repo working tree — see [WORKFLOW.md](WORKFLOW.md) for the canonical walkthrough.

```bash
# Phase 1: Export Trello board
python scripts/export_trello.py --board-id 647a2cce8b1c202caf3cadfc --output /tmp/trello-export

# Phase 2: Match against Linear
python scripts/match.py --trello-dir /tmp/trello-export --linear-file /tmp/linear-issues.json

# Phase 3: Upsert Linear (dry-run first, then apply)
python scripts/update_linear.py --match-report /tmp/trello-export/match-report.json --team Wordtracker --project "What's next (archive)" --dry-run
python scripts/update_linear.py --match-report /tmp/trello-export/match-report.json --team Wordtracker --project "What's next (archive)" --apply

# Phase 4: Verify
python scripts/verify.py --trello-dir /tmp/trello-export --linear-file /tmp/linear-issues.json
```

---

## Dependencies

- `requests` — Trello REST API calls
- `click` — CLI parameters
- `difflib` — fuzzy title matching (stdlib)

The Linear API is accessed via MCP tools (not direct HTTP), so the update script delegates to Claude via match report files rather than calling Linear directly. The agent reads the match report and calls `mcp__linear-*__save_issue` for each update.

---

## Cross-references

| Skill | Relationship |
|:------|:-------------|
| [script](../script/SKILL.md) | Python coding conventions for the scripts |

---

## The governing principle

> _Bulk data operations should be deterministic scripts, not agent conversations. Agents explore; scripts execute._
