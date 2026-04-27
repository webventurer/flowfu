# Sprint vs kanban

Sprint and kanban are two different approaches to managing flow. Both sit under the *agile* umbrella — which is why they get conflated — but they make different bets about how work gets done.

## Side-by-side comparison

| | **Sprint** (Scrum) | **Kanban** |
|:--|:--|:--|
| **Cadence** | Fixed time box (1–4 weeks typically) | Continuous flow — no time boxes |
| **Commitment** | Team commits to a chunk of work at sprint start | Per-item, as it's pulled |
| **Ceremonies** | Mandatory: planning, standup, review, retro | Optional; many kanban teams run none |
| **"Done" measure** | *At end of sprint* | *When item ships* |
| **WIP limit** | Implicit — bounded by time | Explicit — per-lane caps ("no more than 3 in Doing") |
| **Change mid-cycle** | Work sealed once sprint starts | Reprioritise anytime |
| **Metric** | Story points per sprint | Throughput, cycle time |

## Which is more effective?

**Neither — it depends on context.** Both work when they fit, both fail when they don't.

### Kanban tends to win when…

- Work arrives continuously and unpredictably (bug fixes, support, ops, emergent priorities)
- Work sizes vary wildly (forcing varied work into 2-week containers creates artificial pressure)
- The team is small enough that ceremonies are overhead, not scaffolding
- Priorities shift faster than a sprint boundary can tolerate
- The team is mature enough to self-regulate WIP without being told to

### Sprints tend to win when…

- Work arrives in chunks big enough to plan, commit to, and demo
- Stakeholders need a predictable cadence ("what's shipping Friday?")
- The team benefits from the rhythm — ceremonies give checkpoints that prevent drift
- The team is newer to flow discipline and the scaffolding helps
- Cross-functional alignment needs forced touchpoints

### What the research says

The **DORA** metrics (from *Accelerate* — Forsgren, Humble, Kim) — deployment frequency, lead time, mean time to recovery, change-fail rate — don't track with *"does your team do Scrum or kanban?"*. High-performing teams exist in both. The predictive variables are **practices**: trunk-based development, test automation, psychological safety, loose coupling. Those cut across methodology.

## The origin story

Why the vocabulary feels tangled:

- **Sprint** comes from **Scrum** — one of the methodologies that signed the Agile Manifesto in 2001.
- **Kanban** comes from **Toyota manufacturing** (1940s–50s), adapted for software in the late 2000s by David Anderson.
- Both got adopted into agile practice, and hybrid forms exist ("Scrumban").

## For stride specifically

[kanban process](/reference/kanban) is clear: stride runs pure kanban. Flow: Backburner → Backlog → Todo → Doing → In Review → Done. Pull rule. WIP caps. **No sprints.**

Why kanban fits stride's context:

| Stride context | Points toward |
|:---------------|:--------------|
| Small / solo team | kanban (ceremonies = overhead) |
| Work arrives as bugs, feature requests, initiatives | kanban (continuous) |
| Work sizes vary from one-line fix to multi-commit feature | kanban (no forced time-box) |
| No external demo cadence driving sprint boundaries | kanban (no artificial rhythm) |
| Priorities can shift between days (e.g. install-blocker surfaces) | kanban (reprioritise anytime) |

<mark>**Stride's kanban is a *fit* decision, not a preference.**</mark>

## When one human works with many agents

A solo-human + many-AI-agents team isn't a classic team — it's **one decision-maker, many executors**. This shape sits outside both Scrum and kanban as originally designed, because both assume humans coordinating with humans. Apply the two frames to it, though, and **kanban fits decisively better — the argument isn't close.**

### Every argument for sprints is about coordinating people

| Mechanism | Human-only team | Human + agents |
|:----------|:----------------|:---------------|
| **Commitment ceremony** | Sprint commit is a social contract people honour | Agents have *zero* commitment cost — they just start. Sprint's core mechanism has nothing to bind |
| **Parallelism** | One dev works serially; parallelism needs multiple people | Multiple agents work in parallel worktrees by default. Pull-based flow is how this natively happens |
| **Velocity metric** | Story points per sprint captures human effort | *Meaningless* — agents have effectively-unbounded throughput capped by review, not effort. Kanban's **cycle time** and **throughput** capture agent reality |
| **Ceremonies** | Standup / planning / retro coordinate humans | Agents don't need standups. Human-only ceremonies = pure overhead |
| **Reprioritisation** | Sprint-seal protects humans from churn | Human can reprioritise between any two agent dispatches. Sprint boundaries fight this |
| **Cadence** | 2-week rhythm gives social structure | Agents can finish tasks in minutes-hours. Waiting for a sprint boundary is pure artificial lag |

Every argument *for* sprints is about coordinating humans with each other. None of them apply when the "team" is one person orchestrating stateless workers.

### The real wrinkle — two caps, not one

Classic solo-dev kanban puts the WIP limit at **Doing** — one person can only do so much. A human-plus-agents model inverts that: Doing has near-unlimited capacity. Spin up more agents, more worktrees. So where does the cap *move* to?

**Two places, both real:**

- **Review bandwidth** — one human can only read *N* PR diffs per day before quality slips. The queue builds at the *In Review* lane.
- **Merge coherence** — too many parallel worktrees editing overlapping code creates a conflict / integration mess. The pain shows up at merge time, but the cause sits upstream in *Doing*.

Which cap dominates depends on how much the active stories overlap in code:

| Story overlap | Cap that dominates |
|:--------------|:-------------------|
| **Disjoint** stories (different files, different concerns) | review bandwidth |
| **Overlapping** stories (shared files, hot areas) | merge coherence — and it bites first |

For stride today — small codebase, a lot of work touching `bin/install.mjs`, the `.claude/` layout, docs — **merge coherence probably dominates**. Parallel agents on overlapping paths would collide at merge time before the reviewer got saturated.

**What about AI-assisted merges?** Partially — the cap *raises*, it doesn't disappear.

| What AI handles well | What AI still struggles with |
|:---------------------|:-----------------------------|
| Mechanical conflicts (adjacent-line edits, clear winners) | Semantic conflicts that compile and test clean but break integration |
| Non-overlapping edits (git auto-resolves before AI is needed) | Structural conflicts where the right merge shape requires understanding *intent*, not text |
| Running tests post-merge to catch obvious breaks | Design-level coherence — *after N parallel streams landed, does the architecture still hang together, or is it a Frankenstein of competing designs?* |
| Simple semantic merges where both sides' intent is clear | |

<mark>**AI handles conflict at the line level; only a human holds design coherence at the system level.**</mark>

**Two multipliers change the math:**

| Factor | Effect |
|:-------|:-------|
| **Strong test coverage** | Raises the cap — AI-merged code with comprehensive tests passing is high-confidence. Without tests, AI merge is a gamble. |
| **Well-decomposed stories** (see [epic / story / task](../epics-and-user-stories)) | Reduces conflict frequency entirely — disjoint stories don't fight at merge. Better still: **AI can read a well-carved epic plan and route itself through the work accordingly** — picking up non-overlapping slices, sequencing dependencies, not stepping on other agents. Good decomposition multiplied by AI execution is a qualitatively different thing than either alone. |

Both caps are about the *same* bottleneck showing up in different places: the human. As **reviewer**, you can't read more than *N* diffs; as **integrator / conflict-resolver**, you can't hold the shape of *N* overlapping streams. So the WIP discipline in human+agents kanban isn't one cap:

<mark>**How many parallel streams can one human hold the shape of — at both review and merge — before coherence drops?**</mark>

Sprint doesn't help on either side — arguably makes merging worse by bunching concurrent branches, and review worse by bunching PRs at sprint-end.

### The other wrinkle — story decomposition matters more, not less

Multiple agents working in parallel on oversized stories produces merge conflicts, context thrash, and half-implemented features. So the [epic / story / task decomposition](../epics-and-user-stories) isn't optional in this world — it's **load-bearing**. Well-carved atomic stories are how you keep agents from colliding.

So kanban fits — *but* the story-decomposition discipline and the review-lane WIP cap are what make it actually work under agents.

### The torch — what I'm not saying

- **"Kanban pull" is subtly different with agents.** Classic kanban-pull assumes workers choose when to start. Agents usually need to be *dispatched* by the human. Technically it's push-from-human, pull-from-agent-capacity. Doesn't break kanban, but be honest about the mechanics.
- **We may need new vocabulary eventually.** Sprint-vs-kanban was designed for teams of humans. Solo-human + N-agents sits outside that dichotomy. Kanban is the closest fit *today*, but a third model may emerge as the pattern matures. The signal to watch for: if you find yourself inventing terms that don't map cleanly onto either sprint or kanban, that's *friction is information* — something needs a new name. The first such name has already emerged: the **orchestrator + loop** split (see [Orchestrator and loop](../orchestrator-and-loop)) — neither a sprint mechanism nor a pure kanban one, but the shape that fits when one human orchestrates many agent loops.

## Why our agile-sourced docs keep saying "sprint"

Because the source material (Mike Cohn, Jira, Scrum practice) was written when *sprint* was the default sizing unit — Scrum's sprint was THE time-box against which epic / story / task sizes were judged. The sizing *idea* translates fine to kanban; the time-box doesn't.

## The translation that works

| Scrum phrase | Kanban equivalent |
|:-------------|:------------------|
| *"Too big for one sprint"* | *"Too big to be one issue"* |
| *"Fits in a sprint"* | *"Ships as one issue"* |
| *"Story points per sprint"* | *"Cycle time per issue"* |

## The methodology matters less than the practice

The Scrum-or-kanban choice probably matters *less* than people think. A kanban team that doesn't review code is worse than a Scrum team that does. The frameworks are **scaffolding**; the practices inside them are what move the needle. That's Dave Thomas's *"agility"* argument (see [What agile really means](./what-agile-really-means)) in one sentence: **don't sell the frame, cultivate the practice.**

Many teams converge on **hybrids** once they mature. *Scrumban* (sprints + WIP limits) or kanban-with-periodic-retros are common. The binary *"Scrum vs kanban"* choice is more fluid in practice than in slide decks.
