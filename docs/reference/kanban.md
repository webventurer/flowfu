# Kanban process

Kanban is a workflow management method that visualises work as cards moving across columns on a board. Each column represents a stage — work flows left to right, and the board makes bottlenecks visible at a glance.

## The columns

| Column | Purpose | Entry rule | Exit rule |
|:-------|:--------|:-----------|:----------|
| **Backlog** | Ideas and requests not yet prioritised | Anyone can add work here | Prioritised and refined enough to start |
| **To do** | Committed work, ready to pick up | Prioritised by the team | Someone pulls it into Doing |
| **Doing** | Actively being worked on | Developer pulls from To do | Implementation complete, ready for review |
| **In review** | Waiting for code review or QA | PR opened or review requested | Reviewer approves or requests changes |
| **Waiting** | Blocked on something external | Work cannot progress without input | Blocker resolved, moves back to Doing or forward |
| **Done** | Merged and deployed | Review approved, PR merged | — |
| **Backburner** | Parked work — valid but not now | Team agrees to defer | Re-prioritised back to Backlog or To do |

## How work flows

| | | | | | | |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Backlog** | **To do** | **Doing** | **In review** | **Waiting** | **Done** | **Backburner** |
| Work we want to achieve | Prioritised, ready to pick up | Actively being worked on | Waiting for review | Blocked externally | Merged and deployed | Valid, but not now |

### The rules

1. **Pull, don't push** — developers pull the next item from To do when they have capacity. Nobody assigns work to a full queue.
2. **Limit work in progress** — cap how many items can be in Doing and In review at once. This prevents context switching and makes bottlenecks visible.
3. **Make blockers explicit** — when work stalls, move it to Waiting with a note explaining *what* it's waiting on. Don't leave it in Doing looking like active work.
4. **Backburner is not a graveyard** — items here are intentionally deferred, not forgotten. Review the backburner periodically and either promote items back or remove them.

## Key principles

- **Visualise the work** — if it's not on the board, it doesn't exist. All work should be visible.
- **Limit WIP** — the most counterintuitive and most important rule. Finishing work is more valuable than starting work.
- **Manage flow** — optimise for smooth, continuous movement across columns. A card stuck in one column for days is a signal.
- **Make policies explicit** — entry and exit rules for each column prevent ambiguity about when work should move.

## WIP — work in progress

WIP (work in progress) is the number of items actively being worked on at any given time. In Kanban, you set a **WIP limit** — a maximum number of cards allowed in a column (typically Doing and In review).

**Why limit WIP?**

- **Focus** — fewer items in flight means less context switching and faster completion of each one.
- **Exposes bottlenecks** — when a column hits its limit, upstream work stops. This makes the bottleneck impossible to ignore, forcing the team to fix it rather than pile up more work behind it.
- **Pulls over pushes** — a WIP limit means developers only pull new work when they have capacity, rather than having work pushed onto an already full plate.

<mark>The natural instinct is to start more work when something is blocked. WIP limits force the opposite: *stop starting, start finishing*.</mark>

**Setting WIP limits**

There's no universal number. A common starting point is **number of team members + 1** for the Doing column. Adjust based on what you observe — if work flows smoothly, the limit is about right. If cards queue up before a column, that column's limit may be too low, or the *next* column's limit is hiding a bottleneck.

## Common mistakes

- **No WIP limits** — without limits, everything is "in progress" and nothing finishes. The board becomes a to-do list with extra steps.
- **Skipping Waiting** — leaving blocked items in Doing hides the true state of work and inflates the active count.
- **Backlog as a dumping ground** — an ungroomed backlog grows endlessly. Regularly prune items that will never be done.
- **Moving cards backwards** — if review finds issues, the card goes back to Doing (not to To do). Backwards movement through earlier stages signals a process problem.
