# Linear to Linear workflow

<mark>**Follow these steps in order. Always dry-run before applying.**</mark>

---

## Before you start

<mark>**Ask each question below one at a time using `AskUserQuestion`. Do not proceed until all four answers are collected. Getting source/target backwards overwrites the wrong workspace.**</mark>

### Step 1: Ask for source workspace

Ask: *"Which Linear workspace are you migrating FROM (source)?"*

Offer the available workspaces as options by API key env var (e.g. `LINEAR_PERSONAL_API_KEY`, `LINEAR_PLAYGROUND_API_KEY`, `LINEAR_WEBVENTURER_API_KEY`). Confirm the choice with the user.

### Step 2: Ask for source project

Run `python scripts/list_projects.py --api-key-env <SOURCE_API_KEY_ENV>` and present the project names (and teams) as options.

Ask: *"Which project are you migrating FROM?"*

Record the project name and its team.

### Step 3: Ask for target workspace

Ask: *"Which Linear workspace are you migrating TO (target)?"*

Offer the remaining workspaces as options. Confirm the env var with the user.

### Step 4: Ask for target project

Run `python scripts/list_projects.py --api-key-env <TARGET_API_KEY_ENV>` and present the project names (and teams) as options.

Ask: *"Which project are you migrating TO? (Select 'Other' to create a new one)"*

Record the project name and its team.

### Step 5: Confirm

Display a summary table and ask for confirmation before proceeding:

| | Workspace | Team | Project | API key env var |
|:--|:----------|:-----|:--------|:----------------|
| **Source** | *answer 1* | *from step 2* | *answer 2* | *derived* |
| **Target** | *answer 3* | *from step 4* | *answer 4* | *derived* |

Ask: *"Does this look correct? Getting source/target backwards will overwrite the wrong workspace."*

---

## Working directory

<mark>**All commands assume you are in the skill directory. `cd` there immediately after collecting inputs — before running any script.**

```bash
cd .claude/skills/linear-to-linear
```

Script paths (`scripts/...`) are relative to this directory. Running from the repo root will fail. **Do not skip this step.**</mark>

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

## Phase 1.5: Ensure target project and verify states

**Goal**: Create or update the target project with the source description and summary, then confirm the target workspace has all the source workflow states.

1. **Ensure project** — creates the target project if it does not exist, or updates its description/summary if it does. Uses `project.json` from the export:

```bash
python scripts/ensure_project.py \
  --api-key-env <TARGET_API_KEY_ENV> \
  --team <TARGET_TEAM> \
  --project "<TARGET_PROJECT>" \
  --export-dir /tmp/linear-export
```

2. **Check states** — compare source states against the target:

```bash
python scripts/check_states.py \
  --target-api-key-env <TARGET_API_KEY_ENV> \
  --target-team <TARGET_TEAM> \
  --export-dir /tmp/linear-export
```

3. If any source states are missing, ask the user to rename them in the target workspace (Linear UI > Team Settings > Workflow). Re-run until all pass

---

## Phase 2: Match

**Goal**: Match source issues to target issues by title.

1. **Fetch target issues** — writes a JSON file for `match.py`:

```bash
python scripts/fetch_target_issues.py \
  --api-key-env <TARGET_API_KEY_ENV> \
  --team <TARGET_TEAM> \
  --project "<TARGET_PROJECT>" \
  --output /tmp/linear-target-issues.json
```

2. **Run `match.py`**:

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

Linear upload URLs (`uploads.linear.app`) are workspace-scoped. The source workspace's `issue` query returns signed download URLs. The target workspace's `fileUpload` mutation provides presigned upload URLs.

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
