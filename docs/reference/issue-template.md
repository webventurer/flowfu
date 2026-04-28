# Issue template

Every Linear issue created by [`/linear:plan-work`](/skills/linear#linear-plan-work) follows the same seven-section structure. Each heading answers a natural question so the reader can scan quickly and know exactly what the issue is about.

## Title

The title is the first thing a stakeholder reads. Two rules:

1. **Imperative form** — start with a verb (Add, Fix, Replace, Remove…). Avoid "Investigate" unless the outcome genuinely is a report.
2. **Outcome, not implementation** — name the change a stakeholder would recognise from their perspective, not the line of code that delivers it. The body explains *how*; the title says *what changes for the reader*.

### Outcome vs. implementation

| Implementation-level (avoid) | Outcome-level (prefer) |
|:-----------------------------|:-----------------------|
| Reset Tortoise globals between RQ jobs to prevent stale-loop pool | Background jobs run reliably after the first one |
| Add `null` check to `validateUser()` | Sign-up no longer crashes when the email is missing |
| Migrate from Webpack 4 to 5 | Builds finish in under 30 seconds |

### The infrastructure exception

Some work has no user-visible outcome — package upgrades, internal refactors, build changes. For these, name the **system behaviour** that changes, not the file that changes:

| Avoid | Prefer |
|:------|:-------|
| Update `pyproject.toml` ruff config | Linter accepts both 88- and 100-char lines |
| Move `linear_client.py` to `tools/` | `linear_client` is reusable across migration scripts |

If even the system behaviour is invisible (a pure rename, for instance), say what it is plainly: "Rename …", "Upgrade …". Don't contort the title into pretending there's a stakeholder when there isn't.

## Sections

| # | Section | Question it answers |
|:--|:--------|:--------------------|
| 1 | Why this matters | Should I care? |
| 2 | Where things stand | What's the current state? |
| 3 | What we'll do | What's the plan? |
| 4 | What we won't do | Where's the boundary? |
| 5 | Expected outcome | How do we know it's done? |
| 6 | How to test it | How do we verify? |
| 7 | Assumptions to confirm | What's still uncertain? |

Sections 4, 6, and 7 are optional — omit them when they don't add value.

## Example

**Verify new issue template format renders correctly**

### Why this matters

Every issue we create uses this template. If the format is broken, every card in the backlog is harder to read.

### Where things stand

The issue template has new conversational headings but no one has checked whether they render correctly in Linear's markdown.

### What we'll do

- Create a single placeholder issue using the new template format
- Visual check that all sections render as expected

### What we won't do

No changes to the template based on this card — just validation.

### Expected outcome

- Issue appears in Linear with all sections visible and correctly formatted
- "Why this matters" section appears first, before "Where things stand"
- All headings render as distinct sections with no overlap

### How to test it

Visual inspection in Linear — open the issue and confirm each heading renders as a separate section with correct hierarchy.

### Assumptions to confirm

- Linear renders h3 markdown headings consistently across views (board, detail, sidebar)

## Design principles

The headings are deliberately conversational — they work equally well for bugs, features, and improvements. "Where things stand" is neutral: it can describe a broken API, a missing feature, or an opportunity for something new.

The template avoids overlap between sections. Earlier versions had separate Goal, Acceptance criteria, and Success metric sections that all answered "how do we know it's done?" — these were merged into a single Expected outcome.
