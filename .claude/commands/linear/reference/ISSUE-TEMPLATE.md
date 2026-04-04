# CRAFT prompt template for Linear issue creation

> **What this is**: A CRAFT prompt template used by `plan-work.md` step 3 to turn a vague user description into a precise brief before research and drafting.
>
> **Why it exists**: Users often describe work loosely — "add error handling" or "fix the dashboard". Running this through CRAFT produces a structured brief (why it matters, where things stand, what we'll do, expected outcome) that gives the research step (4) precise targets and the drafting step (6) concrete material to work with.
>
> **Where it comes from**: The [CRAFT framework](../../../skills/craft/SKILL.md) (Context, Role, Action, Format, Target audience) — a meta-prompting technique for generating structured, high-quality LLM outputs.

---

## Issue sections

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | Why this matters | Should I care? |
| 2 | Where things stand | What's the current state? |
| 3 | What we'll do | What's the plan? |
| 4 | What we won't do | Where's the boundary? |
| 5 | Expected outcome | How do we know it's done? |
| 6 | How to test it | How do we verify? |
| 7 | Assumptions to confirm | What's still uncertain? |

---

## Example issue

> **Verify new issue template format renders correctly**

### Why this matters
*Sets the stakes — why this work is worth doing now.*

Every issue we create uses this template. If the format is
broken, every card in the backlog is harder to read.

### Where things stand
*Current state — the gap, limitation, or opportunity.*

The issue template has new conversational headings but
no one has checked whether they render correctly in
Linear's markdown.

### What we'll do
*Concrete deliverables — what ships when this closes.*
- Create a single placeholder issue using the new template
  format
- Visual check that all sections render as expected

### What we won't do
*Draws the line so scope doesn't creep.*

No changes to the template based on this card — just
validation.

### Expected outcome
*Observable proof it's done — what a reviewer should see.*
- Issue appears in Linear with all sections visible and
  correctly formatted
- "Why this matters" section appears first, before
  "Where things stand"
- All headings render as distinct sections with no overlap

### How to test it
*How to verify the outcome is real.*

Visual inspection in Linear — open the issue and confirm each
heading renders as
a separate section with correct hierarchy.

### Assumptions to confirm
*Unknowns that could change the plan.*
- Linear renders h3 markdown headings consistently across
  views (board, detail, sidebar)

---

Replace `[user's description]` with what the user provided:

```text
CONTEXT:
We are creating a Linear issue for a software project. The user
has described the work as: "[user's description]". This prompt
will be used to guide codebase research and issue drafting — it
needs to surface why this matters, where things stand, what
we'll do, and the expected outcome so the resulting issue is
immediately
actionable by a developer.

ROLE:
You are a senior product engineer with 20+ years of experience
breaking down ambiguous feature requests into precise, atomic
engineering tasks. You excel at identifying the core need
behind a request, separating must-haves from nice-to-haves,
and writing issue descriptions that a developer can start
working on without asking clarifying questions.

ACTION:
1. Explain why this matters — the user impact, business reason,
   or technical risk that makes this worth doing now
2. Describe where things stand — the current state, whether
   that's a bug, a gap, or an opportunity for something new
3. Define what we'll do — the deliverable and scope boundary
4. Define what we won't do — scope exclusions, only if
   genuinely useful
5. Define the expected outcome — observable results that prove
   it's done, plus measurable metrics if applicable
6. Describe how to test it — expected behaviour, edge cases,
   error conditions (omit for docs, config, or exploratory work)
7. Flag any ambiguities or assumptions that need confirming

FORMAT:
Return a structured brief matching the Linear issue template:

## Title
Concise, imperative, starting with a verb (e.g., "Add dark mode
toggle to dashboard header"). Under 70 characters.

## Description

### Why this matters
User impact, business reason, or technical risk that makes
this worth doing now (1–2 sentences)

### Where things stand
Current state — the bug, gap, or opportunity (1–2 sentences)

### What we'll do
- Bullet list of what's included (the deliverable and scope)

### What we won't do
(Only if genuinely useful — omit if nothing meaningful)

### Expected outcome
Observable results that prove it's done (2–3 bullets). These
are not implementation steps — they describe what a reviewer
should see, not how to code it. Include measurable metrics
when applicable.

### How to test it
(Optional — omit for docs, config, or exploratory work)
Write tests first. What to test: expected behaviour, edge cases,
error conditions.

### Assumptions to confirm
- Bullet list of ambiguities that need resolving

TARGET AUDIENCE:
A developer who will implement this issue. They need clarity,
not context they already have from the codebase. Prefer
concrete over abstract — "the API returns 500 when X is null"
beats "improve error handling".
```

---

## Research mode additions

When running in `--research` mode, append these sections to the
issue after the base template above:

### Implementation notes
Findings from codebase exploration

### Code examples
Actual snippets from the codebase showing how similar patterns are
already implemented — component structure, styling, registration,
utility usage. The goal: the implementing agent should never need
to ask "how do we do X in this codebase?" because examples of X
are right there in the issue.

### Related code
- Files, components, or areas discovered during research

### Related issues
- Links/identifiers of similar Linear issues found
