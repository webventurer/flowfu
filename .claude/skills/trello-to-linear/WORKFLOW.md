# Trello to Linear workflow

<mark>**Follow these steps in order. Always dry-run before applying.**</mark>

---

## Execution sequence

| Step | Action | Detail |
|:-----|:-------|:-------|
| 1 | **Read** the skill | [SKILL.md](SKILL.md) |
| 2 | **Prepare** session | [PREPARE.md](PREPARE.md) |
| 3 | **Export** Trello cards | Phase 1 below |
| 4 | **Verify** Linear project exists | Phase 1.5 below |
| 5 | **Match** to Linear issues | Phase 2 below |
| 6 | **Review** the match report | Human review |
| 7 | **Upsert** Linear | Phase 3 below |
| 8 | **Verify** migration | Phase 4 below |

---

## Phase 1: Export

**Goal**: Pull every card from every list on the Trello board, including descriptions, comments, and checklists.

1. **Clear the output directory** — remove stale data from previous runs before exporting

```bash
rm -rf /tmp/trello-export && mkdir -p /tmp/trello-export
```

2. Get the Trello board ID — if the user gives a name, resolve it via `mcp__trello__list_boards` and filter by name
3. Run `export_trello.py` with board ID and output directory
3. Verify: check `SUMMARY.md` in the output directory for card counts

```bash
python scripts/export_trello.py --board-id <BOARD_ID> --output /tmp/trello-export
cat /tmp/trello-export/SUMMARY.md
```

**Output**: One JSON file per list + `SUMMARY.md` + `all_cards.json`

---

## Phase 1.5: Verify Linear project

**Goal**: Confirm the target Linear project exists and is not trashed before fetching issues or matching.

1. Call `mcp__linear-*__list_projects` with the project name and `includeArchived: true`
2. Check the results — if **no project** is returned, or **all matches are trashed**, stop and tell the user
3. If a valid (non-trashed) project exists, proceed to Phase 2

<mark>**Why this matters**: Linear's `list_issues` returns issues from trashed projects. Without this check, the match phase silently matches against ghost data and reports everything as "skip" — hiding the fact that there's nothing to match against.</mark>

---

## Phase 2: Match

**Goal**: Match Trello cards to Linear issues by title, producing a match report for human review.

1. Export Linear issues from the verified project to a JSON file (paginate if > 250)
2. Run `match.py` with the Trello export directory and the Linear issues file
3. Review `match-report.json` — check unmatched cards and fuzzy matches

```bash
python scripts/match.py --trello-dir /tmp/trello-export --linear-file /tmp/linear-issues.json
```

**Output**: `match-report.json` with actions: `update`, `skip`, `no_match`

### Reviewing the match report

- **`update`** — Trello has content, Linear issue is empty. Description and comments will be pushed
- **`create`** — Trello card has no matching Linear issue. A new issue will be created
- **`skip`** — Linear issue already has a description. No action
- **`fuzzy`** — title matched approximately, not exactly. Verify the match is correct

---

## Phase 3: Update

**Goal**: Upsert Trello content into Linear — update existing issues, create missing ones.

1. Dry-run first — shows what would change without touching Linear
2. Review the dry-run output
3. Apply when satisfied

```bash
# Dry-run — writes inspection payloads to /tmp/trello-export/cards/
python scripts/update_linear.py --match-report /tmp/trello-export/match-report.json --team Wordtracker --project "What's next (archive)" --dry-run

# Apply — calls Linear directly via tools/linear_client.py
python scripts/update_linear.py --match-report /tmp/trello-export/match-report.json --api-key-env LINEAR_WORDTRACKER_API_KEY --team Wordtracker --project "What's next (archive)" --apply
```

In **dry-run** mode, `update_linear.py` writes one JSON payload per card to `cards/` next to the match report (e.g. `000.json`, `001.json`). These are for human inspection — review them before running `--apply`.

In **apply** mode, the script calls Linear directly via `tools/linear_client.py` — resolving team, project, and state IDs up front, then calling `update_issue` / `create_issue` for each entry. No agent round-trip, no `cards/` artefacts. `--api-key-env` is required in this mode.

---

## Phase 4: Verify

**Goal**: Confirm every Trello card landed in Linear with correct title, description, state, and order.

1. Export Linear issues to a JSON file via `mcp__linear-*__list_issues` (paginate if > 250)
2. Run `verify.py` comparing Trello export against Linear issues
3. Review the output — all checks should pass

```bash
python scripts/verify.py --trello-dir /tmp/trello-export --linear-file /tmp/linear-issues.json
```

**Checks**: counts match, all titles present, correct order, descriptions contain Trello content.

---

## Stopping rules

- All `update` items in the match report have been pushed to Linear
- All `create` items have been created in Linear
- Summary written to `UPDATE-SUMMARY.md`

---

## Verification

- [ ] Export produced JSON files for all lists on the board
- [ ] Linear project verified as existing and not trashed
- [ ] Match report reviewed — fuzzy matches verified, creates confirmed
- [ ] Dry-run output reviewed before applying
- [ ] `verify.py` passes — counts, titles, order, and descriptions all correct
- [ ] `UPDATE-SUMMARY.md` written with final counts
