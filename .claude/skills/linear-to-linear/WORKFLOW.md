# Linear to Linear workflow

<mark>**Follow these steps in order. Always dry-run before applying.**</mark>

---

## Before you start

Collect these inputs and **confirm source/target with the user** before proceeding — getting them backwards overwrites the wrong workspace.

| Input | Example |
|:------|:--------|
| Source MCP server | `mcp__linear-personal__*` |
| Source team / project | Playground / "Wordtracker: Intelligence" |
| Source API key env var | `LINEAR_PLAYGROUND_API_KEY` |
| Target MCP server | `mcp__linear-wordtracker__*` |
| Target team / project | Wordtracker / "Intelligence" |
| Target API key env var | `LINEAR_WORDTRACKER_API_KEY` |

---

## Execution sequence

| Step | Action | Detail |
|:-----|:-------|:-------|
| 1 | **Export** source issues | Phase 1 below |
| 2 | **Verify** target project exists | Phase 1.5 below |
| 3 | **Match** to target issues | Phase 2 below |
| 4 | **Review** the match report | Human review |
| 5 | **Create** target issues | Phase 3 below |
| 6 | **Migrate images** | Phase 4 below |
| 7 | **Verify** migration | Phase 5 below |
| 8 | **Compare** source to target | Phase 6 below |

---

## Phase 1: Export source issues

**Goal**: Pull every issue from the source project, including descriptions and comments, into JSON.

```bash
rm -rf /tmp/linear-export && mkdir -p /tmp/linear-export
python scripts/export_linear.py --api-key-env <SOURCE_API_KEY_ENV> --team <TEAM> --project "<PROJECT>" --output /tmp/linear-export
cat /tmp/linear-export/SUMMARY.md
```

**Output**: One JSON file per state + `SUMMARY.md` + `all_cards.json`

---

## Phase 1.5: Verify target project and states

**Goal**: Confirm the target project exists and the target workspace has all the source workflow states.

1. Call `mcp__linear-<target>__list_projects` with the project name
2. If not found, create it or stop
3. **Check states** — compare source states against the target:

```bash
python scripts/check_states.py \
  --target-api-key-env <TARGET_API_KEY_ENV> \
  --target-team <TARGET_TEAM> \
  --export-dir /tmp/linear-export
```

4. If any source states are missing, ask the user to rename them in the target workspace (Linear UI > Team Settings > Workflow). Re-run until all pass

---

## Phase 2: Match

**Goal**: Match source issues to target issues by title.

1. **Fetch target issues** via the target MCP server and save to JSON
2. **Run `match.py`**

```bash
python scripts/match.py --source-dir /tmp/linear-export --target-file /tmp/linear-target-issues.json
```

3. **Review** the match report — check fuzzy matches and create counts

---

## Phase 3: Create

**Goal**: Create source issues in the target workspace.

```bash
# Dry-run
python scripts/bulk_create.py \
  --cards-dir /tmp/linear-export/cards \
  --api-key-env <TARGET_API_KEY_ENV> \
  --team <TARGET_TEAM> \
  --project "<TARGET_PROJECT>" \
  --dry-run

# Apply
python scripts/bulk_create.py \
  --cards-dir /tmp/linear-export/cards \
  --api-key-env <TARGET_API_KEY_ENV> \
  --team <TARGET_TEAM> \
  --project "<TARGET_PROJECT>"
```

States are matched by exact name. Phase 1.5 ensures all source states exist in the target before this step runs.

---

## Phase 4: Migrate images

**Goal**: Download inline images from the source workspace and re-upload to the target.

Linear upload URLs (`uploads.linear.app`) are workspace-scoped. The source MCP's `get_issue` returns signed download URLs. The target workspace's `fileUpload` mutation provides presigned upload URLs.

```bash
# Dry-run
python scripts/migrate_images.py \
  --source-api-key-env <SOURCE_API_KEY_ENV> \
  --target-api-key-env <TARGET_API_KEY_ENV> \
  --export-dir /tmp/linear-export \
  --target-team <TARGET_TEAM> \
  --target-project "<TARGET_PROJECT>" \
  --dry-run

# Apply
python scripts/migrate_images.py \
  --source-api-key-env <SOURCE_API_KEY_ENV> \
  --target-api-key-env <TARGET_API_KEY_ENV> \
  --export-dir /tmp/linear-export \
  --target-team <TARGET_TEAM> \
  --target-project "<TARGET_PROJECT>"
```

**Note**: images are appended before the migration footer — if an image belongs mid-description (e.g. after a "Screenshot:" label), reposition it manually.

---

## Phase 5: Verify

**Goal**: Confirm every source issue landed in the target with correct title and description.

```bash
python scripts/verify.py --source-dir /tmp/linear-export --target-file /tmp/linear-target-issues.json
```

---

## Phase 6: Compare source to target

**Goal**: Catch truncation, missing comments, or content that didn't survive the migration.

```bash
# Report only
python scripts/compare.py \
  --target-api-key-env <TARGET_API_KEY_ENV> \
  --target-team <TARGET_TEAM> \
  --target-project "<TARGET_PROJECT>" \
  --export-dir /tmp/linear-export

# Report and fix
python scripts/compare.py \
  --target-api-key-env <TARGET_API_KEY_ENV> \
  --target-team <TARGET_TEAM> \
  --target-project "<TARGET_PROJECT>" \
  --export-dir /tmp/linear-export \
  --fix
```

The script compares each source issue (description + comments) against the live target issue. It flags:

- **Truncated** — target is significantly shorter than expected
- **Missing comments** — source had comments that aren't in the target
- **Missing images** — source had inline images that aren't in the target

Any flagged issues are automatically fixed by re-pushing the full content.

---

## Verification

- [ ] Source issues exported with descriptions and comments
- [ ] Target project verified as existing and not trashed
- [ ] Match report reviewed — fuzzy matches verified, creates confirmed
- [ ] Dry-run output reviewed before applying
- [ ] `bulk_create.py` run — all issues created
- [ ] `migrate_images.py` run — images downloaded, uploaded, and descriptions updated
- [ ] `verify.py` passes — counts, titles, and descriptions correct
- [ ] `compare.py` passes — no truncation, missing comments, or missing images
- [ ] Spot-checked image rendering in target issues
