# Plan work and create a Linear issue (optional --research mode)

Accepts a description and optional flags: `/plan-work --research --craft "add error handling to API calls"`

## Modes

- **Quick mode** (default): `/plan-work "description"` — draft, review, create
- **Research mode**: `/plan-work --research "description"` — explore codebase and Linear first, then draft with richer context

## Flags

- `--research` — explore codebase and Linear before drafting (adds code examples, acceptance criteria)
- `--craft` — auto-run CRAFT prompt refinement without asking (skips the interactive prompt in step 3)

## Decision rules

- One issue = one deliverable. If the description contains "and" connecting unrelated outcomes, split.
- Default to the smallest issue that moves something forward. If the user's description is broad, propose a focused first issue plus follow-ups.
- Titles are imperative and start with a verb (Add, Fix, Replace, Remove…). Avoid "Investigate" unless the outcome genuinely is a report, not a code change.
- Never assign the issue unless the user explicitly asks.
- Labels are optional — suggest at most 3, only when clearly relevant. Prefer no labels over speculative ones.
- Priority defaults to Medium. Only upgrade if the user says it's urgent or the description implies user-facing breakage.
- Research mode exists to improve the draft, not to produce an audit. Cap file exploration at 2–5 relevant files; summarise patterns, don't catalogue the repo.
- Duplicate handling is two-tier: exact/near-exact → warn strongly and ask; similar/related → mention briefly and continue.
- The user always gets final approval before creation. Never auto-create.

## Steps

### 0. Resolve project

Check for a `.linear_project` file in the repository root.

- If **found**: read the project name from it
- If **not found**: list available projects via `list_projects`, ask the user to choose, and save their selection to `.linear_project`. Then check the repo's `.gitignore` — if `.linear_project` isn't listed, append it.

Use the resolved project name for all Linear API calls in this command.

### 1. Parse arguments

Extract the description and flags from `$ARGUMENTS`. Determine if `--research` and/or `--craft` are present.

### 2. Duplicate check (all modes)

Search Linear for potentially related issues:

```
list_issues with a query matching key terms from the description
```

Handle results in two tiers:

- **Exact or near-exact duplicates** (same problem, same scope): warn strongly, show them, and ask whether to proceed or stop.
- **Similar or related issues** (overlapping area but different scope/angle): show briefly, continue drafting, and reference them in the draft's "Related issues" section.

### 3. CRAFT prompt refinement (all modes)

<mark>**When `--craft` is present, always run CRAFT before research. Never skip this step.**</mark> The user passes `--craft` to sharpen their description into a clearer prompt — skipping it means research works from a vaguer input than intended.

If `--craft` flag is present, run CRAFT automatically. Otherwise, ask the user: "Would you like me to run `/craft` on your description first to sharpen the issue before drafting?"

- If **yes** (or `--craft`): read [reference/ISSUE-TEMPLATE.md](reference/ISSUE-TEMPLATE.md), run `/craft` using that template with the user's description, then use the refined output as the description for all subsequent steps
- If **no**: continue with the original description

### 4. Research (only with `--research`)

- Search the codebase for 2–5 relevant files using Grep/Glob — summarise patterns or constraints, avoid exhaustive repository analysis
- Check Linear for similar issues via `list_issues` (broader search than step 2)
- Read relevant project documentation if necessary (see [reference/project-docs.md](reference/project-docs.md) for standard paths)
- Fetch available labels via `list_issue_labels` for the resolved team
- Summarise findings for use in the draft

### 5. Test consideration

Assess whether tests make sense for this change. Not every issue needs them — pure documentation, config changes, or exploratory spikes typically don't.

If tests do make sense, note in the issue that **tests should be written first, then the implementation to match**. Claude writes both at once so it's not strict TDD, but having tests in place makes sure future changes don't break the tool.

Add a `### Tests` section to the draft when applicable:

```markdown
### Tests
Write tests first. [Brief description of what to test — expected
behaviour, edge cases, error conditions.]
```

Omit the section entirely when tests don't apply.

### 6. Draft the issue

### Title rules

- Imperative mood, starting with a verb (Add, Fix, Replace, Remove, Extract…)
- Specific enough that someone can understand the scope without reading the description
- Avoid "Investigate" unless the deliverable genuinely is a report, not a code change
- Keep under 70 characters when possible

**Quick mode** — lean template:

```markdown
## Title
Concise, imperative (e.g., "Add dark mode toggle to dashboard header")

## Description

### Problem
What problem exists

### Goal
Desired outcome

### Scope
- Bullet list of what's included

### Out of scope
(Include only when genuinely useful — omit if nothing meaningful to exclude)

### Success metric
(Include only when genuinely useful — omit if not applicable)
```

**Research mode** — adds to the lean template:

```markdown
### Implementation notes
Findings from codebase exploration

### Code examples
Actual snippets from the codebase showing how similar patterns are
already implemented — component structure, styling, registration,
utility usage. The goal: the implementing agent should never need
to ask "how do we do X in this codebase?" because examples of X
are right there in the issue.

### Acceptance criteria
Observable outcomes that define "done". These are not implementation
steps — they describe what a reviewer should see, not how to code it.

### Related code
- Files, components, or areas discovered during research

### Related issues
- Links/identifiers of similar Linear issues found
```

Suggest **priority** (default Medium unless clearly urgent). Suggest no more than 3 **labels**, only if clearly relevant — prefer no labels over speculative ones.

**Scope guidance**: Prefer small, actionable issues. If the description is too broad for a single issue, suggest splitting into a focused primary issue plus follow-ups.

### 7. Cross-model feedback loop (optional)

After drafting the issue:

1. **Claude presents the draft** with its own assessment — what's strong, what could be better, any concerns about scope or feasibility
2. Ask: **"Want to send this to ChatGPT for feedback before creating?"**

If **yes**, run the three-voice feedback loop (Claude → ChatGPT → Claude → User):

**Round N:**

1. **Send to ChatGPT** — send the current draft (including Claude's assessment) to ChatGPT:

```bash
python tools/openrouter-chat.py "<full draft text + Claude assessment>" -m openai/gpt-5.4-pro -s "You are reviewing a Linear issue draft and a first review from Claude. Give specific, actionable feedback on the problem statement, scope, and acceptance criteria. Point out gaps, assumptions, or scope creep. Agree or disagree with the first review. Be direct."
```

2. **Show ChatGPT's feedback** — display the full ChatGPT response as text output so the user can read it. Do not summarise or collapse it — the user needs to see the raw feedback before Claude responds. Use a heading like "**ChatGPT's feedback (round N):**" followed by the complete response text.

3. **Claude responds** — after the user has seen ChatGPT's feedback, review it against the draft. Incorporate points that strengthen the issue, push back on points that don't fit or expand scope unnecessarily. Explain your reasoning for each decision. Present the updated draft.

4. **User decides** — ask: **"Send to ChatGPT again, or exit the loop?"**
   - If **again** — repeat from step 1 with the revised draft
   - If **exit** — continue to step 8

Each round has three voices: Claude proposes and synthesises, ChatGPT challenges, the user steers. The loop sharpens the issue through cross-model perspectives — like a design review but for issue planning.

### 8. Present for approval

Show the full draft to the user. Ask for explicit approval before creating.

- If the user requests changes, revise and re-present
- If the user declines, stop — do not create the issue

### 9. Create the issue

Only after explicit approval:

```
save_issue with:
  - team: resolved team
  - project: resolved project
  - status: "Backlog"
  - title, description, priority, and labels from the draft
```

Do not assign the issue unless the user explicitly requested it.

### 10. Confirm creation

Display:
- Linear issue identifier (e.g., PG-184)
- URL to the issue
- Branch name from Linear's `gitBranchName` field

## Error handling

- If `$ARGUMENTS` is empty or missing a description, ask the user for one
- If issue creation fails, show the error and stop
