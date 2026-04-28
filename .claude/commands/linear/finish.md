# Finish issue

Merge an approved PR, clean up branches, and mark the issue Done.

Accepts a Linear issue ID as argument: `/finish PG-205`

If no argument is given, infer the issue ID from the current branch name (extract `PG-\d+` pattern). If neither works, ask the user.

Workflow: `/plan-work` → `/start` (includes terminal review) → `/fix` (if GitHub review feedback) → **`/finish`**

## Rules

- Never merge if tests fail
- The merge commit message should read as if the work was done right the first time — no mention of rejections, fix cycles, or iterations
- Use `--merge` (not `--squash`) to preserve atomic commits in the branch
- Never force-delete branches

---

## Steps

### 1. Read the Linear issue

Fetch the issue via MCP:

- `get_issue` with `$ARGUMENTS`

Extract: issue ID, title, `gitBranchName`, current status, milestone.

Stop if the issue cannot be found.

### 2. Find the PR

Run `gh pr list --head <gitBranchName> --json number,url,title,reviewDecision,mergeable`.

If no PR exists, stop — nothing to merge.

### 3. Check repo state

Run `git status -sb`.

If there are uncommitted changes, warn and stop — suggest `/commit`.

### 4. Validate

Run the project's build command (e.g. `pnpm build`). If the project has tests, run them too.

If anything fails, stop — do not merge. Show what failed.

### 5. Merge (preserve commits)

Merge with `--merge` to preserve the atomic commits from the branch. The merge commit gets the default subject only — no body. The individual commits on the branch already explain what was built and why; duplicating that in the merge commit just creates drift between the two messages.

```bash
gh pr merge <number> --merge --subject "Merge branch '<gitBranchName>'" --body ""
```

Pass `--body ""` explicitly so `gh` does not fall back to the PR description.

### 6. Clean up branches, remove worktree, close VS Code

Detect the main repo path. Run `git worktree list` — the first entry is the main repo:

```bash
git worktree list
```

**All git commands must use `git -C <main-repo-path>`** to avoid depending on the worktree directory.

Derive the worktree path from the repo name and issue ID:

```
../<repo-dirname>-<issue-id-lowercase>
```

**Step 6a — Switch to main and pull:**

```bash
git -C <main-repo-path> checkout main && git -C <main-repo-path> pull
```

**Step 6b — Remove worktree:**

Remove the worktree first — git refuses to delete a branch that a worktree is checked out on.

```bash
git -C <main-repo-path> worktree remove <worktree-path>
```

If the worktree directory does not exist, skip silently. If `git worktree remove` fails due to untracked files, use `--force`.

**Step 6c — Delete branches:**

Now that the worktree is gone, the branch can be deleted:

- **Local**: `git -C <main-repo-path> branch -d <gitBranchName>` — use lowercase `-d` since the merge commit makes the branch fully merged. If already deleted, skip silently
- **Remote**: `git -C <main-repo-path> push origin --delete <gitBranchName>` — if already deleted (GitHub may auto-delete), skip silently

**Step 6d — Ask user to close VS Code:**

```
Please close the VS Code window for <worktree-dirname>.
```

VS Code does not support programmatic window closing. The worktree directory is already gone, so VS Code will show an error state — the user just needs to close the window.

### 7. Update Linear → done

Move the issue to **Done** via `save_issue`.

Only set Done status. Skip if already Done. Never set any other status.

### 7b. Check milestone completion

Skip this step if the issue had no milestone.

Otherwise, call `list_issues` filtered by the milestone with non-Done states (`backlog`, `unstarted`, `started`). If any results come back, the milestone has remaining work — skip silently.

If the result is empty, all stories in the milestone are now Done. Prompt:

```
All stories in *[Milestone name]* are complete — mark the milestone done?
```

If the user confirms, append a completion note to the milestone description via `save_milestone` (Linear has no milestone "completed" state, so a description note is the durable signal). Format:

```
Completed: <YYYY-MM-DD> — all stories Done.
```

If the user declines, leave the milestone untouched.

### 8. Summary

Display:

- Issue ID and title
- PR: merged
- Build: passed
- Local branch: deleted / already gone
- Remote branch: deleted / already gone
- Worktree: removed / not found
- Linear status: Done
- Milestone (if applicable): name + completion status (`complete` if 7b marked it complete, `<n> stories remaining` otherwise)

---

## Error handling

- Issue ID unresolvable → stop, ask the user
- Issue not found in Linear → stop
- No PR found → stop, nothing to merge
- Uncommitted changes → stop, suggest `/commit`
- Tests fail → stop, do not merge
- Branch not fully merged → stop, warn (never force-delete)
- Local branch already deleted → skip silently
- Remote branch already deleted → skip silently
