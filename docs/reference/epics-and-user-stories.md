# Epics and stories

Stride breaks work into three layers — **epic, story, task** — and maps them onto Linear's primitives. This page is the reference for what each layer is, where it lives, and how the `/linear` commands use them.

For the *why* behind the choices (vocabulary origins, the trade-off between three possible epic mappings, the live question on non-user-facing work), see the [research doc](/research/epics-and-user-stories).

## The mapping

| Layer | Linear primitive | Where it lives |
|:------|:-----------------|:---------------|
| **Product** | Project | `Stride >>>` — the whole-product container |
| **Epic** (named initiative) | **Milestone** inside the project | Created by `/linear:plan-work` when the description is epic-sized |
| **Story** (slice of value) | Issue, optionally linked to a milestone | Created by `/linear:plan-work`; ships as one PR |
| **Task** (unit of work) | Atomic commit | Created during `/linear:start` as the branch accumulates commits |

## What each layer is

**Epic.** A named initiative made of multiple stories. Too big to ship as one PR. Has a stakeholder-recognisable name like a feature or theme. Lives as a Milestone inside the project.

**Story.** One deliverable. Ships as one PR. Reverts cleanly. Belongs to a milestone if one exists; otherwise sits directly in the project.

**Task.** One atomic commit. Stride's task layer lives in git history, not Linear's sub-issue feature. Each commit is one task-sized idea, and the PR ships them together as a coherent story.

**When in doubt about epic vs. story, ask: can this ship as one PR?** If yes, it's a story. If no, it's an epic. <mark>**Premature epics are clutter; missing epics are confusion.**</mark>

## Plan a few, ship, replan

When `/linear:plan-work` creates an epic (Milestone), it asks for **the first 1–3 stories** — not all of them. After the first lands, run `/linear:next-steps` against the milestone and plan the next 1–3 — same loop, fresh context.

| Why plan 1–3 (agile) | What planning all of them at once (waterfall) costs |
|:---------------------|:----------------------------------------------------|
| You only know enough to plan a few stories well — beyond that you're guessing | Locks in design decisions before requirements force them |
| Each shipped story changes the context — story 4 might look different after 1–3 land | The backlog goes stale before you reach it |
| 1–3 fits in working memory; the user can review them as a coherent set | Bulk creation bypasses real review and bloats the board |
| Leaves the milestone open to *act, then adjust* — feedback from a shipped story shapes the next plan | Pretends the future is knowable; closes doors before you need to |

## How the `/linear` commands map to layers

| Command | Layer it operates on |
|:--------|:---------------------|
| `/linear:plan-work` | Epic and story creation. Asks the sizing question; routes epic-sized work through milestone creation, story-sized through issue creation |
| `/linear:start` | Story → atomic commits. Surfaces the parent milestone if any; opens a branch and PR for the story |
| `/linear:fix` | Story (after PR review) — applies reviewer feedback as new commits |
| `/linear:finish` | Story closure. Marks the story Done; if it was the last open story in its milestone, prompts to mark the milestone done |
| `/linear:next-steps` | Story selection within a project or milestone. Offers an epic filter when milestones exist |

## Two axes: decomposition and flow

Epic → story → task is **decomposition** — how big a unit of work is. That's orthogonal to **flow** — where a unit sits on the kanban board (Backburner → Backlog → Todo → Doing → In Review → Done).

| Axis | Question it answers | Reference |
|:-----|:--------------------|:----------|
| **Decomposition** | *What is this work, and how big?* | This doc |
| **Flow** | *Where is this work right now?* | [Kanban process](/reference/kanban) |

A story sits somewhere on the kanban lanes. So does its parent epic. So do the child tasks once work begins. Milestones group issues by decomposition; they don't move them through flow. Each issue inside a milestone still flows Backburner → Done on its own.
