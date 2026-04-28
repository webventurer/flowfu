# Review priorities and recommend next work

Review what's happening and recommend what to work on next.

## Decision rules

- **Priority ordering**: build failure > PRs needing fix > in-progress work > PRs needing review > approved PRs to merge > backlog
- If there are started issues assigned to the current user, treat these as the primary tasks
- Do not recommend new work unless current tasks are blocked or completed
- Sort backlog candidates by priority: Urgent > High > Medium > Low
- Prefer quick wins when priorities are equal (small, self-contained issues)
- Treat issues with dependencies, blocker labels, or blocked status as blocked
- Flag blocked issues but do not recommend them
- Recommend 1–3 concrete next actions, not a full backlog dump

## Steps

### 0. Resolve project

Check for a `.linear_project` file in the repository root.

- If **found**: read the project name from it
- If **not found**: list available projects via `list_projects`, ask the user to choose, and save their selection to `.linear_project`. Then check the repo's `.gitignore` — if `.linear_project` isn't listed, append it.

Use the resolved project name for all Linear API calls in this command.

### 1. Fetch data (all calls in parallel)

| Call | Tool |
|:-----|:-----|
| `get_user` — authenticated user | Linear MCP |
| `list_issues` — state: `started`, project: resolved project | Linear MCP |
| `list_issues` — state: `unstarted`, project: resolved project | Linear MCP |
| `list_issues` — state: `backlog`, project: resolved project | Linear MCP |
| `list_issues` — state: `completed`, updatedAt: `-P7D`, project: resolved project | Linear MCP |
| `list_milestones` — project: resolved project | Linear MCP |
| `gh pr list --state open --json number,title,headRefName,author,reviewDecision,reviews,url` | Bash |

### 2. Show current work

If there are started issues, show them first — they provide context for what's already happening.

| ID | Title | Assignee | Priority |
|:---|:------|:---------|:---------|

If none: "Nothing currently in progress."

### 3. Open pull requests

If there are open PRs, show them:

| PR | Title | Branch | Review | Action |
|:---|:------|:-------|:-------|:-------|

For each PR, check for unaddressed review feedback:

```bash
gh api repos/{owner}/{repo}/pulls/<number>/reviews --jq '[.[] | select(.state == "CHANGES_REQUESTED")] | length'
gh api repos/{owner}/{repo}/pulls/<number>/comments --jq 'length'
```

Classify each PR:

- **Needs fix** — has `CHANGES_REQUESTED` or unresolved review comments → recommend `/fix <issue-id>`
- **Needs review** — `reviewDecision` is not `APPROVED` and no feedback yet → waiting on reviewers
- **Approved** — ready to merge → recommend `/finish <issue-id>`

PRs needing fix take priority over all new backlog work.

If none: "No open pull requests."

### 4. Recently completed (last 7 days)

| ID | Title | Completed |
|:---|:------|:----------|

If none: "No issues completed recently."

This context should influence recommendations — prefer follow-up issues or related tasks where appropriate.

### 5. Build candidate list

Combine `unstarted` and `backlog` issues into a single candidate list. Exclude issues already in `started`. Exclude issues identified as blocked. Sort by priority (Urgent first).

If milestones exist for the project, ask: **"Show next steps for a specific epic, or all work?"** If the user picks an epic, filter the candidate list to issues with that milestone. If they pick all work, group the candidate list by milestone (with one group for issues that have no milestone).

Show as a table per milestone (or one combined table when no milestones exist):

| ID | Title | Priority | Labels | Status |
|:---|:------|:---------|:-------|:-------|

If the list is empty: "Backlog is empty — nothing to recommend."

### 6. Recommend next actions

Apply the priority ordering: build failure > PRs needing fix > in-progress > PRs needing review > approved PRs to merge > backlog.

Pick 1–3 items. For each recommendation, explain briefly why it's the right next move using factors such as: priority, quick win potential, follow-up to recently completed work, unblocking other work, PR needing review, alignment with current work in progress.

Format:

> **Recommended next**
>
> 1. **PG-XX — Title** — reason
> 2. **PG-YY — Title** — reason

### 7. Offer to start

Ask: "Want me to start one of these? I can run `/start <ID>` for you."
