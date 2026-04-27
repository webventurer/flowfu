# Orchestrator and loop

> **Status**: Research stage. Three working positions: (a) stride and telic-loop compose into a **two-mode shape** — orchestrator (strategic) and loop (tactical) — that maps cleanly onto the human + agents pattern; (b) the orchestrator runs **continuously, not once** — "design it all upfront" is the waterfall trap in agile clothing; (c) the human stays gated on **replan moments and PR review**, fully out of the loop within an iteration. This doc is the conceptual frame; the build steps are sketched here but not committed to.

Stride owns the durable layers — Linear issues, branches, atomic commits, PRs. Telic owns the [iteration layer](./epics-and-user-stories#the-iteration-layer-lives-in-the-agent-loop) — the loop passes that drive one story to done. Put them together and you get a shape that works for a long-lived project run by one human plus many agents: an **orchestrator** that decomposes scope into the next right slices, and a **loop** that takes each slice and ships it.

This doc is about how those two pieces fit, why they should stay separate, and what's load-bearing about the split.

## The two cognitive modes

Orchestration and execution aren't just different functions — they're different *cognitive modes*, with different cadences and different human involvement. Treating them as one process bundles concerns that should stay apart.

| | **Orchestrator** | **Loop** |
|:--|:--|:--|
| **Mode** | Strategic | Tactical |
| **Question** | *What's the next right slice?* | *How do I drive this slice to done?* |
| **Cadence** | Occasional — between merges | Continuous — within a story |
| **Substrate** | Linear (issues, milestones, project) + git history | Feature branch + `.loop/iter-N/` artifacts |
| **Human role** | In the loop — gating each replan | Out of the loop — PR review only |
| **Output** | The next 1–3 stories, value-shaped | A merged PR that ships one story |

<mark>**The orchestrator decides what's worth doing; the loop makes sure it's done properly.**</mark>

## The waterfall trap

The seductive version of this idea is: *the human comes up with an app idea, the orchestrator designs all of it, drops 40 cards into Linear, and loops execute them one by one.* That's waterfall in agile clothing.

By the third card shipping, the first one has revealed something that should have changed cards 5, 12, and 27. The plan ages out faster than it ships. Worse: the cards in Linear *look* authoritative — they were planned upfront — so the loop charges ahead executing stale decisions.

The failure mode is the same one Dave Thomas critiques in [What agile really means](./agile/what-agile-really-means): *prediction in advance instead of feedback from action*. Big-bang orchestration is a prediction. Continuous orchestration is feedback.

## The shape that works

The orchestrator runs **continuously, not once**. After each PR merges, it looks again: what did we learn? What's the next right slice? Re-prioritise, re-decompose, re-shape — and only *then* feed the next story to the loop.

Concretely:

- **The vision/epic stays stable; the story list churns.** You declare the app idea once (PROJECT_VISION-style), and the decomposition into stories evolves as you ship. Stable spine, mutable ribs.
- **The orchestrator produces just enough.** The next 1–3 stories, refined to value-shape. Not 40. Not the whole app. This is what stride's `/linear:plan-work` is reaching toward — and `/linear:next-steps` is the reassessment side of the same idea.
- **The loop is fully autonomous within one story.** Card moves Todo → Doing when a loop picks it up; loop runs iterations until self-check passes; PR opens; card moves to In Review.
- **The human reviews the PR.** This is the hard cap from [Sprint vs kanban](./agile/sprint-vs-kanban#the-real-wrinkle-two-caps-not-one) — *only the human holds design coherence at the system level*. AI can resolve line-level conflicts; only the human can tell whether N parallel streams still hang together as a system.
- **Orchestrator + human reconvene at replan moments**, not constantly. Every N merged PRs, or when something surprising lands, the human and orchestrator look again. *This* is where the human intervenes — not during loop execution, but at the planning seams.

## How the layers stack

The orchestrator-and-loop split sits on top of the [epic / story / iteration / task hierarchy](./epics-and-user-stories#the-work-breakdown-hierarchy) — it doesn't replace it. The split is about *who is operating at which layer*:

| Layer | Who operates here | Visibility |
|:------|:------------------|:-----------|
| **Epic / Vision** | Human (orchestrator-assisted) | Stable; rarely re-opened |
| **Story** | Orchestrator + human gating | Linear board — every card visible |
| **Iteration** | Loop, autonomously | `.loop/iter-N/` artifacts on the branch — *not* on the board |
| **Task** | Loop, as atomic commits | Git history on the branch |

The board shows the *story* layer flowing Backburner → Done. The iteration layer happens *underneath* a single story-card sitting in Doing — it's the substrate of how that card gets driven to done, not its own stream of work.

## Where the human sits

The human's attention is the scarce resource. The split is designed around protecting it.

| Activity | Human in the loop? |
|:---------|:-------------------|
| Declaring the vision/epic | Yes — and only here is it big-bang |
| Approving the next 1–3 stories | Yes — gates each replan |
| Loop execution within a story | No — agent runs autonomously, self-checks |
| PR review on each shipped story | Yes — design coherence cap |
| Replan after merge | Yes — orchestrator proposes, human approves |

<mark>**Start human-gated at the orchestrator layer. Loosen only as the loop's self-check track record earns it.**</mark>

Fully autonomous orchestrator = more throughput but design drift risk. Human-gated orchestrator = slower but coherent. The bet is that the cost of a bad replan compounds across many stories, while the cost of a bad iteration is bounded to one story's PR — so the human gate belongs at the orchestrator layer, not the loop layer.

## What this would mean to build

Roughly in priority order — the first piece ships standalone value before the others land:

1. **Orchestrator command** that takes a vision + current Linear state and proposes the *next* 1–3 stories (not all of them). Likely a `/linear:plan-next` or extension of `/linear:plan-work`. Today `/linear:plan-work` already uses "one issue = one deliverable" as its atomicity rule — what's missing is the *just enough* discipline and the *reassess-after-merge* trigger.
2. **Loop entrypoint that targets a Linear issue**, not a foo-style sprint dir. Pulls issue, creates branch, runs `.loop/iter-N/` cycles with a value-checklist gate, opens PR, transitions issue from Doing to In Review.
3. **Replan trigger** — after each merge, orchestrator reassesses backlog. Could be human-invoked at first (`/linear:plan-next` run manually); autonomous later, once the track record justifies dropping the gate.

The first two end at the same place; the first one ships value sooner.

## Worked example

Roughly how a long-lived project would run under this shape:

1. **Human** writes `PROJECT_VISION.md` for the app. One paragraph; no card list yet.
2. **Orchestrator** (`/linear:plan-next`) reads the vision and proposes the first 2 stories: *"As a user, I can sign in with Google"* and *"As a user, I can see my dashboard after sign-in."* Creates them as Linear issues in Todo.
3. **Human** glances at the two stories, adjusts wording, approves.
4. **Loop** picks up the sign-in story → moves it to Doing → creates branch → runs iterations (plan, implement, test, self-check) → opens PR → moves story to In Review.
5. **Human** reviews PR. Merges. Story moves to Done.
6. **Orchestrator** re-runs. Notices that during the sign-in build, a *session expiry* concern surfaced that wasn't in the original plan. Proposes the next 2 stories: *"Dashboard"* (revised based on what sign-in returned) + *"Session expiry handling"* (new — not in the upfront plan).
7. **Human** approves the new shape. Loop picks up the next story.
8. Repeat — vision stable, story list evolving with what each merge reveals.

The thing that *wouldn't* have happened under big-bang orchestration: step 6 catching the session-expiry gap. Under "design it all upfront", session expiry would have been planned in advance based on a guess, *or* missed entirely and only caught in production.

## Open questions / what I'm not saying

- **This doc is a frame, not a build commitment.** Whether the integration is worth building depends on use case. For long-lived products run by one human plus agents — yes. For 30-min throwaway demos like `foo` — no, the structure overhead doesn't pay back; just use telic-loop directly.
- **"Orchestrator" is not (yet) a separate process or agent.** Today it's a *role* the human + `/linear` commands play together. Whether it should become a long-running autonomous process is a downstream question — and the answer probably stays "no" until the loop's self-check track record earns it.
- **The replan cadence is unsolved.** "Every N merged PRs" or "when something surprising lands" are heuristics, not a rule. The right answer probably emerges from running it — *feedback from action* — not from deciding upfront. Watch for the signal: if the human is intervening between every PR, replan is too rare; if cards routinely go stale before being picked up, replan is too late.
- **This is not a new methodology.** It's stride's existing kanban + the iteration layer + an honest naming of where the human sits. The novelty is in *naming the orchestrator layer explicitly* and committing to *continuous, not big-bang*. Both are clarifications, not inventions.
