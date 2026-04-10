---
name: linear-to-linear
description: Copy issues between Linear workspaces — descriptions, comments, labels, attachments, images, and state. Use when Linear lacks a workspace copy tool. Triggers on "linear to linear", "copy workspace", "migrate linear".
---

# Linear to linear

> Copy issues from one Linear workspace to another, preserving descriptions, comments, labels, attachments (PRs, commits), images, and state.

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

<mark>**All scripts are self-contained in `scripts/`. Each phase has its own script — export, match, check states, check labels, create, migrate images, verify.**</mark>

---

## Scripts

All scripts live in `scripts/` and share `linear_api.py` for GraphQL calls, retries, and file loading.

| Script | Phase | What it does |
|:-------|:------|:-------------|
| `export_linear.py` | Export | Pulls all issues from a source workspace — descriptions, comments, labels, attachments, states — writes JSON per state |
| `match.py` | Match | Reads source export + target issues, matches by title (exact → fuzzy), writes `match-report.json` + `cards/` |
| `check_states.py` | Check states | Validates that all source workflow states exist in the target workspace. Run before create |
| `check_labels.py` | Check labels | Validates source labels exist in target. Run with `--create` to add missing ones with matching colors |
| `bulk_create.py` | Create | Reads `cards/`, creates issues in target with labels and attachments. Validates states upfront — fails fast if any are missing |
| `migrate_images.py` | Images | Downloads images via signed source URLs, re-uploads to target workspace |
| `verify.py` | Verify | Compares source export against target issues — checks counts, titles, descriptions |

### Running

```bash
# Phase 1: Export source issues
python scripts/export_linear.py --api-key-env LINEAR_PLAYGROUND_API_KEY --project "Wordtracker: Phase 1" --team "Playground" --output scripts/output/phase1

# Phase 2: Match against target (provide target issues JSON, or empty [] for fresh project)
python scripts/match.py --source-dir scripts/output/phase1 --target-file scripts/output/phase1/target_issues.json

# Phase 3: Check states match
python scripts/check_states.py --target-api-key-env LINEAR_WORDTRACKER_API_KEY --target-team "Wordtracker" --export-dir scripts/output/phase1

# Phase 3b: Check labels (create missing ones)
python scripts/check_labels.py --target-api-key-env LINEAR_WORDTRACKER_API_KEY --export-dir scripts/output/phase1
python scripts/check_labels.py --target-api-key-env LINEAR_WORDTRACKER_API_KEY --export-dir scripts/output/phase1 --create

# Phase 4: Create issues (dry-run first)
python scripts/bulk_create.py --cards-dir scripts/output/phase1/cards --api-key-env LINEAR_WORDTRACKER_API_KEY --team "Wordtracker" --project "Phase 1" --dry-run
python scripts/bulk_create.py --cards-dir scripts/output/phase1/cards --api-key-env LINEAR_WORDTRACKER_API_KEY --team "Wordtracker" --project "Phase 1"

# Phase 5: Migrate images
python scripts/migrate_images.py --source-api-key-env LINEAR_PLAYGROUND_API_KEY --target-api-key-env LINEAR_WORDTRACKER_API_KEY --export-dir scripts/output/phase1 --target-team "Wordtracker" --target-project "Phase 1"

# Phase 6: Verify
python scripts/verify.py --source-dir scripts/output/phase1 --target-file scripts/output/phase1/target_issues.json
```

---

## Known limitations

- **Image positions may shift.** Images are appended to the end rather than preserved in their original position within the description.
- **Comment images require manual transfer.** The Linear API signs description image URLs but not comment image URLs. Images embedded in comments must be saved from the source in a browser and re-uploaded manually.

---

## The governing principle

> _Each script owns one phase. Shared logic lives in `linear_api.py`._
