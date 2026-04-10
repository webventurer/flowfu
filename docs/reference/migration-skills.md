# Migration skills

Linear has no built-in way to copy issues between workspaces. These two skills fill the gap.

## The skills

| Skill | Source | Target | When to use |
|:------|:-------|:-------|:------------|
| `/linear-to-linear` | Linear workspace | Linear workspace | Migrating issues between workspaces (e.g. org1 → org2) |
| `/trello-to-linear` | Trello board | Linear workspace | Migrating from Trello after switching to Linear |

## Why they exist

When work starts in one Linear workspace (a personal sandbox, a prototype project) and needs to move to another (a team workspace), there's no way to do it natively. Linear's bulk move only works within the same workspace. The API doesn't expose a copy operation.

The same problem applies to Trello migrations — Linear's official importer handles basic card titles but loses descriptions, comments, and checklists.

Both skills solve this by exporting everything to JSON, then creating issues in the target with full content preserved.

## What they preserve

| Content | linear-to-linear | trello-to-linear |
|:--------|:----------------:|:----------------:|
| Titles | ✓ | ✓ |
| Descriptions | ✓ | ✓ |
| Comments | ✓ | ✓ |
| Labels | ✓ | — |
| Attachments (PRs, commits) | ✓ | — |
| Images | ✓ | — |
| Workflow state | ✓ | ✓ (mapped) |
| Checklists | — | ✓ |

## How they work

Both follow the same phased pattern — each phase has its own script, run in order:

1. **Export** — pull everything from the source into JSON files
2. **Match** — compare source against target to avoid duplicates
3. **Check** — validate that states (and labels) exist in the target
4. **Create** — create issues in the target (dry-run first)
5. **Verify** — confirm counts, titles, and descriptions landed

linear-to-linear adds two extra phases: **migrate images** (re-upload via signed URLs) and **check labels** (create missing labels with matching colors).

## Where they live

Both skills are in `.claude/skills/` with their scripts in a `scripts/` subdirectory. Each script is standalone and shares `linear_api.py` for GraphQL calls.

See the individual skill docs for full usage:

- linear-to-linear: `.claude/skills/linear-to-linear/SKILL.md`
- trello-to-linear: `.claude/skills/trello-to-linear/SKILL.md`
