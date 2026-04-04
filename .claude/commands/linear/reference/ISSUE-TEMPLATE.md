# CRAFT prompt template for Linear issue creation

> **What this is**: A CRAFT prompt template used by `plan-work.md` step 3 to turn a vague user description into a precise problem statement before research and drafting.
>
> **Why it exists**: Users often describe work loosely — "add error handling" or "fix the dashboard". Running this through CRAFT produces a structured brief (why it matters, what's wrong, what we'll do, expected outcome) that gives the research step (4) precise targets and the drafting step (6) concrete material to work with.
>
> **Where it comes from**: The [CRAFT framework](../../../skills/craft/SKILL.md) (Context, Role, Action, Format, Target audience) — a meta-prompting technique for generating structured, high-quality LLM outputs.

---

Replace `[user's description]` with what the user provided:

```text
CONTEXT:
We are creating a Linear issue for a software project. The user
has described the work as: "[user's description]". This prompt
will be used to guide codebase research and issue drafting — it
needs to surface why this matters, what's wrong, what we'll
do, and the expected outcome so the resulting issue is immediately
actionable by a developer.

ROLE:
You are a senior product engineer with 20+ years of experience
breaking down ambiguous feature requests into precise, atomic
engineering tasks. You excel at identifying the core problem
behind a request, separating must-haves from nice-to-haves,
and writing issue descriptions that a developer can start
working on without asking clarifying questions.

ACTION:
1. Explain why this matters — the user impact, business reason,
   or technical risk that makes this worth doing now
2. Restate the user's description as a clear problem statement
   — what is broken, missing, or suboptimal?
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

### What's wrong
What is broken, missing, or suboptimal (1–2 sentences)

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
