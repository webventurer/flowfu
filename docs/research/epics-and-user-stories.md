# Epics, stories, and tasks in Linear

> **Status**: Research stage. Four working positions the doc takes: (a) *epic / story / task* is **work-breakdown** vocabulary, not Agile Manifesto material; (b) stride maps it onto Linear via **Milestones inside a project** when an epic crystallises; (c) stride's atomic commit discipline fills the task layer; (d) stride adds an **iteration** layer between story and task — one pass of the agent loop toward the story, invisible to the kanban board. One [open question](#open-question-non-user-facing-work) about non-user-facing work remains live — that's why this doc lives in `research/`, not `reference/`.

## Linear mapping quick reference

| Linear primitive | Hierarchy layer | Stride today |
|:-----------------|:----------------|:-------------|
| Project | Product / vision | `Stride >>>` |
| Milestone | Epic | Create with `/linear:plan-work` |
| Issue | Story | Create with `/linear:plan-work` |
| Atomic commit | Task | Created during `/linear:start` |

Stride drives delivery through Linear issues, but Linear's data model — projects, milestones, issues, sub-issues — doesn't prescribe how *big* each unit of work should be. *Epic → user story → task* is a well-worn **work-breakdown hierarchy** for sizing. Bringing it into stride gives the `/linear` commands a shared vocabulary for "is this too big to be one issue?" and "what does a shippable slice look like?"

## Where the vocabulary actually comes from

These terms get called *agile* all the time — and yet the three-layer hierarchy *epic → story → task* **isn't in the Agile Manifesto**. It isn't in Dave Thomas's *"agility"* talk either. It's **Scrum + Jira-popularised project-management terminology** that got bundled under the branded *"Agile"* industry Dave Thomas critiques.

Which is exactly why it *feels* agile-shaped — it travelled with that industry — but it didn't come from the manifesto.

The individual terms each have their own origin:

| Term | Origin |
|:-----|:-------|
| **Epic** | Made a formal container by **Atlassian's Jira** |
| **User story** | Extreme Programming (Kent Beck, late 1990s); formalised with the *"As a user, I want…"* template by Mike Cohn's *User Stories Applied* (2004) |
| **Task** | Generic project-management practice, formalised as a story-child by Scrum convention |

See [*What agile really means*](./agile/what-agile-really-means) for Dave Thomas's argument that **agility** (lowercase, a practice) is the thing worth keeping, and *"Agile"* (capital, a branded methodology) is the thing the industry sold on top of it. This doc uses *agile* only as a lowercase adjective, for that reason.

## What is an epic?

An epic is a large chunk of work that's too big to complete in a single sprint.

*(Stride uses [kanban, not sprints](./agile/sprint-vs-kanban) — but the spirit is the same: an epic is too big to ship as **one issue**.)*

Think of it as a container for related user stories.

### 1. Simple definition

An epic =

A big goal or feature that gets broken down into smaller, deliverable pieces.

### 2. The work-breakdown hierarchy

Looks like:

- **Epic** (big outcome)
  - **User stories** (smaller pieces of value)
    - **Iterations / loop passes** (each agent run that drives the story toward done — invisible to the board)
      - **Tasks** (actual work to build it — atomic commits)

The **iteration** layer is stride-specific and exists because of the human + AI agents shape. In a classic team, a story goes from Todo to Doing to Done in one human work-stream. With agents, a story usually takes *multiple loop passes* — plan, implement, review, refine — each one a discrete run. That's an *iteration*. It lives below the story, doesn't surface on the kanban board, and is the unit the agent loops over (not the human).

### 3. Example: an epic and its user stories

Epic:
"Improve checkout experience"

Breaks into user stories:

- "As a user, I can save my card details"
- "As a user, I can checkout in one click"
- "As a user, I see total cost clearly before paying"

Each of those gets split into tasks (UI, backend, validation, etc.)

### 4. Key traits of an epic

- Too big for one sprint
- Spans multiple teams or features (sometimes)
- Focused on an outcome, not implementation
- Gets refined over time (not fully defined upfront)

### 5. Quick mental model

- Epic = theme / initiative
- Story = usable slice of value
- Iteration = one agent loop pass toward the story (stride-specific; not on the board)
- Task = how it gets built (one atomic commit)

### 6. Why epics exist

Without epics:

- Work becomes fragmented
- Hard to track progress on big goals
- Strategy → execution link breaks

<mark>**Epics keep everything tied to a bigger objective.**</mark>

### 7. One-line version

An epic is just a big user story that's been split into smaller stories over time.

## How this lives in stride

Stride is built on the `/linear` commands, which sit on top of Linear's data model. The hierarchy above maps onto that model cleanly — once you know where each layer lives, the commands can be shaped to reason about scope instead of guessing.

### Decomposition vs flow — two orthogonal axes

Epic → story → task is **decomposition**: how we break big work down into shippable pieces. It answers *what is this, and how big?*

That's orthogonal to **flow** — how work moves through the system. Flow is the kanban dimension: Backburner → Backlog → Todo → Doing → In Review → Done. It answers *where is this right now?*

| Axis | Question it answers | Where stride documents it |
|:-----|:--------------------|:--------------------------|
| **Decomposition** | *What is this work, and how big?* | This doc. Epic / story / task. |
| **Flow** | *Where is this work right now?* | [kanban process](/reference/kanban). Backburner → Done. |

Every unit of work has both coordinates. A story sits somewhere in the kanban lanes; so does its parent epic (usually further back in the process); so do the child tasks once work begins. The `/linear` commands themselves span both axes — `/linear:plan-work` operates on decomposition ("is this epic-sized or story-sized?"), `/linear:start` and `/linear:finish` operate on flow (moving a story between lanes), and `/linear:next-steps` combines them (*what's the next **story** in **Todo**?*).

**Translating Scrum's "sprint" language.** Scrum uses a sprint as its sizing unit — an epic is *"too big for one sprint"*. Stride runs kanban, which has no sprints. The kanban equivalent: *"too big to ship as one issue?"*. Same sizing intent, different unit. See [Sprint vs kanban](./agile/sprint-vs-kanban) for the full comparison.

### Mapping to Linear's data model

Linear gives us four primitives worth knowing about here — **Project**, **Milestone**, **Issue**, **Sub-issue** — and more than one way to map the work-breakdown onto them. There isn't a single correct mapping; the right one depends on scale.

| Hierarchy layer | Linear primitive | Stride today |
|:----------------|:-----------------|:-------------|
| **Product / vision** | Project | `Stride >>>` — the whole-product container |
| **Epic** (big initiative) | **Milestone** inside the project (preferred); a dedicated Project only at a scale stride isn't at | *None explicit yet.* The `Stride >>>` project acts as one implicit epic |
| **Story** (slice of value) | Issue | WB-240 — *Stride installer should hash-compare before refusing on conflict* |
| **Iteration** (one agent loop pass) | *Not surfaced in Linear* — lives in the agent's working state | The plan / implement / review passes the agent runs while driving WB-240 to done |
| **Task** (unit of work) | Atomic commit, or Sub-issue for bigger breakdowns | The individual commits on the WB-240 branch — one idea each |

### Three options for the epic layer

There's no single answer to *"where does an epic live in Linear?"* — it depends on product scale. Three plausible mappings, ordered from smallest to largest:

- **Option 1 — No explicit epic layer.** The whole product is one implicit epic. Stories sit directly under the product's project. Fits small products and solo / small-team work. **This is what stride does today.**
- **Option 2 — Milestone = Epic.** The project stays the whole-product container; epics become Milestones *within* the project, and issues get linked to a milestone. Fits a product big enough that named initiatives ("Installer reliability V2") start to earn their own grouping. This is the natural next step for stride when an epic-sized initiative crystallises.
- **Option 3 — Project = Epic.** Each major initiative gets its own Linear Project. Fits large orgs running many parallel initiatives across teams. Probably too heavy for stride — would fragment a single-product codebase across multiple projects.

<mark>**Pick the lightest option that still fits. Premature epics are clutter; missing epics are confusion.**</mark>

**The trajectory for stride is Option 1 → Option 2.** Today we're at Option 1 and that's honest — no epic-sized initiative has crystallised yet. When the first one does, the move is to introduce a **Milestone** inside `Stride >>>` and link the child issues to it. Option 3 stays on the shelf; fragmenting a single-product codebase across multiple Linear Projects would trade clarity for structure we don't need.

**Milestones and flow stay orthogonal.** A Milestone groups issues on the decomposition axis — it doesn't move them through kanban states. Each issue inside a milestone still flows Backburner → Done on its own. That's what keeps the two axes clean: a Milestone is *where an issue belongs* by decomposition, not *where it is* by flow.

### Plan a few, ship, replan

Once you commit to a Milestone, the next question is how many child stories to create up front. The answer is **the first 1–3** — and only those — before shipping anything. After the first story lands, the next 1–3 will be informed by what you learned.

| Why plan 1–3 (agile) | What planning all of them at once (waterfall) costs |
|:---------------------|:----------------------------------------------------|
| You only know enough to plan a few stories well — beyond that you're guessing | Locks in design decisions before requirements force them |
| Each shipped story changes the context — story 4 might look different after 1–3 land | The backlog goes stale before you reach it |
| 1–3 fits in working memory; the user can review them as a coherent set | Bulk creation bypasses real review and bloats the board |
| Leaves the milestone open to *act, then adjust* — feedback from a shipped story shapes the next plan | Pretends the future is knowable; closes doors before you need to |

`/linear:plan-work` enforces this by asking only for "the first 1–3 stories" when the epic path fires. When those land, run `/linear:next-steps` against the milestone and plan the next 1–3 — same loop, fresh context.

### The task layer lives in commits

Stride doesn't lean on Linear's sub-issue feature today; the task layer usually lives in **git history** instead. An issue becomes a feature branch, the branch accumulates atomic commits (each one a task-sized idea), and the PR ships them together as a coherent story. Sub-issues stay available for the rarer case where a story genuinely splits into independently-trackable tasks.

That's a stride-specific choice worth naming: **stride's atomic commit discipline is already doing the work of the "task" layer**. If the Linear view of a story looks like it's missing a layer, that's why — the layer's there, it just lives in the commit log.

### The iteration layer lives in the agent loop

Between *story* and *task* sits a layer that classic Scrum / Jira vocabulary doesn't have a name for: the **iteration** — one pass of the agent's loop toward the story. Plan, implement, review, refine; each pass is one iteration. A small story might ship in a single iteration. A larger one might take five or six.

This layer **doesn't surface on the kanban board**. The story sits in *Doing*; the iterations happen *underneath* it. The human watches the story move through lanes; the agent watches the iterations.

Why call it out at all then? Because once you name it, two things get clearer:

- **What "Doing" actually contains.** A story in *Doing* isn't a single act of work — it's an open-ended loop the agent is currently running. The lane name describes the *story's* state; the *iterations* are the substrate.
- **Where the loop's discipline applies.** Plan-review cycles, value checklists, exit gates — these belong to the iteration, not the story. Naming the layer gives those mechanisms a home.

This is **not** a Scrum sprint. A Scrum sprint is a *time-box across a whole team*; an iteration here is *one loop pass inside one story for one agent*. They share the word "iterate" and nothing else. The vocabulary borrowed from older agile sources (sprint, iteration, cycle) gets used inconsistently across the industry — stride uses *iteration* for this concept and reserves *sprint* for the Scrum sense (which stride doesn't run; see [Sprint vs kanban](./agile/sprint-vs-kanban)).

For a worked example of the iteration layer running visibly, see telic-loop projects (e.g. `foo`'s `sprints/sprint-3/.loop/`), where each sprint shipped a story-sized slice over multiple named iterations (`iter 1–5`). Telic's "sprint" ≈ stride's "story"; telic's "iter" ≈ stride's "iteration".

The strategic counterpart to the iteration layer — *who decides what stories to feed the loop in the first place* — is the **orchestrator**. See [Orchestrator and loop](./orchestrator-and-loop) for how the two modes compose into a long-lived-project shape.

### Shaping the `/linear` commands

Knowing which layer you're at changes what a command should do. `/linear:plan-work` already uses "one issue = one deliverable" as its atomicity rule, and splits when the description contains "and". That's story-shaped thinking. Where the frame unlocks new moves:

- **`/linear:plan-work`** — when the ask is epic-sized ("improve checkout experience"), the right move is to flag *this is bigger than one issue*, create a **Milestone** inside the current project to hold the child stories, and link each issue to that milestone as it's created — rather than one issue with a long description. Today the command reads a pre-existing project from `.linear_project` and creates issues inside it; it doesn't yet create or link milestones.
- **`/linear:next-steps`** — should reason about the next story *within a project*, not scan all issues flat.
- **`/linear:start`** — already operates at story level: one issue → one branch → one PR → N atomic commits (the tasks).
- **`/linear:finish`** — closes the story and the PR. If the parent project has more open stories, it could nudge toward the next one.

None of these are shipped behaviours yet; they're the candidate moves the frame unlocks.

### A concrete example: stride itself

The `Stride >>>` Linear project is the **whole-product container** — not an epic on its own. The vision behind it (*build a CLI for atomic commits and Linear workflow that turns AI speed into maintainable codebases*) acts as one big implicit epic at stride's current scale. That's **Option 1** from the table above: no separate epic layer yet, because nothing has grown big enough to warrant one.

Recent issues inside the project behave like stories:

- **WB-240** — *Installer should hash-compare before refusing on conflict.* Slice of user value: consumers who already have codefu installed can now install stride without a type-mismatch refusal.
- **WB-238** — *Write stride paths to the consumer's `.gitignore` on install.* Slice of user value: consumers don't need to edit `.gitignore` by hand.
- **WB-234** — *Installer deletes files outside its footprint.* Slice of user value: the consumer's existing files survive a stride install.

Each was independently shippable, independently revertible, and sized to one feature branch. None needed sub-issues — the task layer sat in the commits.

When an epic-sized initiative genuinely crystallises — say *"Installer reliability V2"* covering WB-234, WB-238, WB-240 as a coherent theme — the natural move is to shift to **Option 2** and introduce a **Milestone** inside `Stride >>>` to hold them. That's a decision to make only when the grouping earns its place; until then, the flat story list does the job.

<mark>**The first Milestone we create will be the real test of this frame.**</mark> Whether Option 2 actually helps in practice (or whether the grouping feels like extra ceremony) only becomes visible once an epic is live. Until that feedback arrives, the commitment is to the *mechanism* (Milestone), not to any particular epic.

## Open question: non-user-facing work

The user-story frame fits when work is user-facing — *"As a user, I can X"*. But plenty of legitimate work has no user in the sentence: **rotating secrets on the backend**, upgrading a build system, migrating a database engine.

Stride has this shape of work too. The recent refactor extracting gitignore section helpers (commit `6d30531`) has no user in the sentence — it's a pure restructure for internal clarity. Neither does "fix recurring ruff format churn" (branch `wb-88`). These are real, they ship, and the "as a user" template doesn't fit.

How do we account for that?

Three possibilities worth exploring — none chosen yet:

- **Stretch the frame** — *"As an operator, I can rotate secrets without downtime."* Cast system-facing work in story form with a non-end-user actor (operator, SRE, future maintainer). Keeps the uniform shape across all work.
- **Accept the frame has limits** — epics contain stories *and* technical items. A story is one shape of child, not the only shape. Honest about the fact that not every useful slice of work fits the "as a user" sentence.
- **Drop the frame for certain work** — some epics are purely operational and decompose into tasks directly, no story layer. Accepts two kinds of epics instead of one.

This question is live. The shape of the answer will likely come from seeing which pattern survives first contact with a real stride engagement — *feedback from action*, not resolution in advance.
