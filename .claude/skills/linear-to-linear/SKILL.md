---
name: linear-to-linear
description: Copy issues between Linear workspaces — descriptions, comments, labels, attachments, images, state, project updates, and resource links. Use when Linear lacks a workspace copy tool. Triggers on "linear to linear", "copy workspace", "migrate linear".
---

**CRITICAL**: Read and follow EVERY step in `WORKFLOW.md`

# Linear to linear

> Copy issues from one Linear workspace to another, preserving descriptions, comments, labels, attachments (PRs, commits), images, state, project updates, and resource links.

---

## When to use

- Migrating issues between Linear workspaces (e.g. personal to team)
- Duplicating a project across workspaces
- Linear has no built-in workspace copy tool

## When NOT to use

- Migrating from Trello to Linear — use [trello-to-linear](../trello-to-linear/SKILL.md)
- Moving issues within the same workspace — use Linear's bulk move

---

## Quick reference

<mark>**All scripts are self-contained in `scripts/` and talk directly to the Linear GraphQL API. No MCP calls — every read and write is deterministic.** Each phase has its own script — export, ensure project, fetch target, match, check states, check labels, create, migrate images, verify, compare.</mark>

---

## Scripts

All scripts live in `scripts/` and import the shared Linear client from `tools/linear_client.py` (via a small `_bootstrap.py` that puts the repo-root `tools/` directory on `sys.path`). Skill-specific file loaders live in `skill_io.py`.

| Script | Phase | What it does |
|:-------|:------|:-------------|
| `export_linear.py` | Export | Pulls all issues, project description/summary, project updates, and resource links from a source workspace — writes JSON per state plus `project.json`, `project_updates.json`, `project_links.json` |
| `ensure_project.py` | Ensure project | Creates the target project from `project.json` if missing, or updates its description/summary if it exists |
| `fetch_target_issues.py` | Fetch target | Writes target issue list to JSON for `match.py` |
| `match.py` | Match | Reads source export + target issues, matches by title (exact → fuzzy), writes `match-report.json` + `cards/` |
| `check_states.py` | Check states | Validates that all source workflow states exist in the target workspace. Run before create |
| `check_labels.py` | Check labels | Validates source labels exist in target. Run with `--create` to add missing ones with matching colors |
| `bulk_create.py` | Create | Reads `cards/`, creates issues, project updates, and resource links in target. Validates states upfront — fails fast if any are missing |
| `migrate_images.py` | Images | Downloads images via signed source URLs, re-uploads to target workspace |
| `verify.py` | Verify | Compares source export against target issues — checks counts, titles, descriptions |
| `compare.py` | Compare | End-to-end comparison: issues (description + comments + images) and project-level metadata (description, summary, updates, links) |

### Running

All commands assume you are in `.claude/skills/linear-to-linear/`. Pipeline artifacts go to `/tmp/linear-export` so they never touch the repo working tree — see [WORKFLOW.md](WORKFLOW.md) for the canonical walkthrough.

```bash
# Phase 1: Export source issues and project metadata
python scripts/export_linear.py --api-key-env LINEAR_PLAYGROUND_API_KEY --project "Wordtracker: Phase 1" --team "Playground" --output /tmp/linear-export

# Phase 1.5a: Ensure target project exists with source description/summary
python scripts/ensure_project.py --api-key-env LINEAR_WORDTRACKER_API_KEY --team "Wordtracker" --project "Phase 1" --export-dir /tmp/linear-export

# Phase 1.5b: Check states and labels
python scripts/check_states.py --target-api-key-env LINEAR_WORDTRACKER_API_KEY --target-team "Wordtracker" --export-dir /tmp/linear-export
python scripts/check_labels.py --target-api-key-env LINEAR_WORDTRACKER_API_KEY --export-dir /tmp/linear-export
python scripts/check_labels.py --target-api-key-env LINEAR_WORDTRACKER_API_KEY --export-dir /tmp/linear-export --create

# Phase 2: Fetch target issues and match
python scripts/fetch_target_issues.py --api-key-env LINEAR_WORDTRACKER_API_KEY --team "Wordtracker" --project "Phase 1" --output /tmp/linear-target-issues.json
python scripts/match.py --source-dir /tmp/linear-export --target-file /tmp/linear-target-issues.json

# Phase 3: Create issues, project updates, and resource links (dry-run first)
python scripts/bulk_create.py --cards-dir /tmp/linear-export/cards --api-key-env LINEAR_WORDTRACKER_API_KEY --team "Wordtracker" --project "Phase 1" --export-dir /tmp/linear-export --dry-run
python scripts/bulk_create.py --cards-dir /tmp/linear-export/cards --api-key-env LINEAR_WORDTRACKER_API_KEY --team "Wordtracker" --project "Phase 1" --export-dir /tmp/linear-export

# Phase 4: Migrate images
python scripts/migrate_images.py --source-api-key-env LINEAR_PLAYGROUND_API_KEY --target-api-key-env LINEAR_WORDTRACKER_API_KEY --export-dir /tmp/linear-export --target-team "Wordtracker" --target-project "Phase 1"

# Phase 5: Compare end-to-end (issues + project metadata)
python scripts/compare.py --target-api-key-env LINEAR_WORDTRACKER_API_KEY --target-team "Wordtracker" --target-project "Phase 1" --export-dir /tmp/linear-export
```

---

## Known limitations

- **Image positions may shift.** Images are appended to the end rather than preserved in their original position within the description.
- **Comment images require manual transfer.** The Linear API signs description image URLs but not comment image URLs. Images embedded in comments must be saved from the source in a browser and re-uploaded manually.
- **Project update timestamps are not preserved.** The `projectUpdateCreate` mutation does not accept a `createdAt` field — updates are created with the current timestamp.
- **Project update authorship is not preserved.** Updates are created as the API key owner. The original author is stored in the exported JSON.

---

## The governing principle

> _Each script owns one phase. Shared Linear client lives in `tools/linear_client.py`._
