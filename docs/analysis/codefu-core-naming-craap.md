# CRAAP analysis: Is "codefu-core" the right wrapper?

> Critical analysis of whether "codefu-core" accurately represents what this project actually is — an automatic Kanban board at its heart.

## Original output summary

**codefu-core** is marketed as a set of Claude Code skills that turn vibe coders into agentic engineers. It installs three skills (`/commit`, `/linear`, `/craft`) as plain markdown into `.claude/`. The README frames it around the "solid foundation" metaphor — vibe coding builds on quicksand, codefu-core gives you bedrock.

**The claim being examined:** codefu-core is fundamentally an automatic Kanban board. Does the name "codefu-core" serve or obscure that identity?

---

## Critique and refine

### What codefu-core actually does

Strip away the philosophy and marketing, and the **operational core** is:

| What happens | Mechanism |
|:-------------|:----------|
| Work appears on a board | `/linear:plan-work` creates issues in Linear |
| Work gets prioritised | `/linear:next-steps` reads the board state |
| Work moves through columns automatically | `/linear:start` moves Backlog → Doing → In Review |
| Work completes automatically | `/linear:finish` moves to Done, merges, cleans up |
| PR feedback loops back | `/linear:fix` handles review cycles |

That's a **Kanban automation layer**. The board moves itself as you work. `/commit` and `/craft` are supporting acts — they make the work *better*, but the backbone is the automated board lifecycle.

### The naming problem

"codefu-core" tells you nothing about what this is. Break it down:

| Component | What it communicates |
|:----------|:---------------------|
| **codefu** | Martial arts + code. "Mastery of code." Branding, not function |
| **core** | This is the essential/base part of a larger thing called "codefu" |

A developer encountering "codefu-core" for the first time would guess: code generation tool? CLI framework? Linting library? The name gives zero signal about Kanban, workflow automation, or issue lifecycle management.

### The "core" suffix problem

"core" implies this is a library extracted from a larger product — the way `react-core`, `angular-core`, or `express-core` would be the kernel of a bigger framework. But codefu-core isn't a programmatic library. It's a set of **markdown instructions** for an AI agent. The "core" suffix sets an expectation of extensibility via code (import, extend, compose) that doesn't match the reality (copy markdown, edit it).

### What the name gets right

- **Brand continuity** — if codefu is your broader body of AI-assisted engineering research, then codefu-core as the distributable extract makes sense *within your ecosystem*
- **Memorability** — "codefu" is short, distinctive, and easy to type
- **Aspiration** — "fu" (mastery) signals this is about discipline, not shortcuts — aligned with the anti-vibe-coding message

### Weaknesses

| Issue | Severity |
|:------|:---------|
| Name doesn't describe function | High |
| "core" implies a library/SDK, not a methodology | Medium |
| No hint of Kanban, workflow, or automation | High |
| Requires reading README to understand what it is | Medium |
| Search discoverability is poor — "codefu" returns nothing relevant | Medium |

---

## Risk potential and unforeseen issues

### Identity risk: What are you selling?

The README leads with the **vibe coding vs agentic engineering** framing — a philosophical argument. The actual product is workflow automation. This creates a gap:

- **What the name says:** "I will make you a code master"
- **What the README says:** "I will save you from vibe coding"
- **What the product does:** "I will move your Kanban cards automatically while enforcing commit discipline"

Three different pitches. A developer who needs a Kanban automation layer won't find this. A developer attracted by "codefu" might expect something more transformative than issue lifecycle management.

### The real value proposition is buried

The README leads with the vibe coding vs agentic engineering philosophy. The Kanban board is the second visual. But neither is the real sell — the real sell is **atomic commits**: a git history where every change is one idea, independently revertible, with a reason attached. That's what vibe coding destroys, and it's buried under layers of philosophy and board mechanics.

### Risk of over-abstraction

Calling it "codefu-core" abstracts away what makes it concretely useful. Compare:

| Name | What you expect | What you get |
|:-----|:----------------|:-------------|
| codefu-core | Vague mastery tool | Kanban automation + commit discipline |
| linear-flow | Linear workflow automation | Closer to reality |
| agentic-board | AI-driven Kanban | Descriptive but niche |

The abstract name forces reliance on documentation to explain value. A descriptive name carries the value proposition in itself.

### Counter-risk: Being too literal

A name like "auto-kanban" or "linear-autopilot" would be descriptive but limiting — and would sell the wrong thing (the board, not the commits). If you later add skills beyond Linear (Jira integration, GitHub Projects, standalone mode), a literal name becomes a cage. "codefu-core" has room to grow. The trick is pairing the brand name with a tagline that sells the outcome (trustworthy history) rather than the mechanism (board automation).

---

## Analyse flow and dependencies

### What's actually "core"?

If codefu-core is the core, what's the periphery? Looking at the codefu parent repo:

| In codefu (parent) | In codefu-core | Relationship |
|:--------------------|:---------------|:-------------|
| CRAAP framework | Not included | Research/methodology |
| Harvest skill | Not included | Research extraction |
| AI patterns library | Not included | Knowledge base |
| Integration scripts | Replaced by installer | Distribution mechanism |
| Research docs | Not included | Background knowledge |

So "core" = the three skills that are distributable. Everything else is research, methodology, and internal tooling. This is a valid use of "core" *if the audience knows about codefu*. For everyone else, "core" is meaningless without the context of what it's the core of.

### The dependency on Linear

The name "codefu-core" obscures a hard dependency: **this only works with Linear**. The `/linear` commands are the backbone — remove them and you have a commit skill and a prompt generator. That's useful but it's not "the core of anything."

This means:
- The project is as much "Linear automation" as it is "code mastery"
- The name should arguably acknowledge the workflow/board aspect
- Users who don't use Linear will hit a wall at the most important feature

### Flow of understanding

```
Developer discovers "codefu-core"
    → "What is codefu?" (no answer in the name)
    → Reads README
    → "Oh, it's about vibe coding vs agentic engineering" (philosophical)
    → Scrolls further
    → "Oh, it's three skills for Claude Code" (functional)
    → Scrolls further
    → "Oh, it automates a Kanban board via Linear" (the actual value)
```

The name adds a step to the discovery journey rather than shortcutting it.

---

## Alignment with goal

### What's the actual goal?

From the README and docs, the goal is: **give developers a structured, automated workflow that prevents the entropy of vibe coding**.

The mechanism is: **an AI-driven Kanban lifecycle where issues flow from Backlog to Done automatically, with atomic commits at every stage**.

### Does the name serve the goal?

| Goal aspect | Name alignment |
|:------------|:---------------|
| Structured workflow | No signal |
| Automated board | No signal |
| Anti-vibe-coding | "fu" (mastery) weakly signals discipline |
| Atomic commits | No signal |
| Linear integration | No signal |

The name is **brand-first, function-second**. This is a valid strategy if:
- You're building a recognised brand (Nike doesn't describe shoes)
- The brand has existing recognition (codefu doesn't, yet)
- The discovery path has other signals (search, recommendations, listings)

For a new open-source project competing for attention on GitHub, a descriptive name typically outperforms a brand name in early adoption.

### Alignment verdict

The name aligns with the **aspiration** (code mastery) but not with the **outcome** (trustworthy git history through atomic commits). The mechanism (automated Kanban) is scaffolding — it shouldn't be the headline either. For a project that lives or dies on README-driven discovery, the gap between name and outcome is meaningful.

---

## Perspective

### The skeptic

> "You named your Kanban automation tool 'codefu-core' because it sounds cool, not because it communicates what it does. If I search GitHub for workflow automation, issue lifecycle, or Kanban tools — I'll never find this."

Fair. The name optimises for brand identity over discoverability. For an established product with marketing channels, this is fine. For a GitHub repo that needs to be found by developers searching for solutions, it's a handicap.

### The end-user

> "I installed it because the README was compelling. The name didn't help or hurt — I found it through a recommendation. Once I'm using it, I don't care what it's called."

Also fair. Names matter most for discovery. Once adopted, the name becomes invisible. If your distribution strategy is word-of-mouth and blog posts rather than GitHub search, the name matters less.

### The potential contributor

> "'codefu-core' — is this a game? A coding challenge platform? A framework? I have to read the entire README to know whether I even care."

In open source, contributors self-select by scanning repo names and one-line descriptions. A name that requires explanation filters out casual discoverers.

### The brand strategist

> "codefu is distinctive, memorable, and owns a concept. 'Linear workflow automator' is descriptive but generic and forgettable. You can build a brand around codefu. You can't build a brand around a description."

Valid long-term argument. The question is whether the project is at the stage where brand matters more than discoverability.

---

## Enhanced recommendations

### The core question: What stage is this project at?

| Stage | Best naming strategy |
|:------|:---------------------|
| **Pre-launch / early adoption** | Descriptive. People need to know what it is. |
| **Growing / word-of-mouth** | Hybrid. Brand + subtitle. |
| **Established** | Brand. The name IS the identity. |

codefu-core is at **early adoption**. The recommendation:

### Recommended: Rename to flowfu

**flowfu** — *All the speed. None of the mess.*

| Dimension | Assessment |
|:----------|:-----------|
| **What "flow" signals** | Workflow, continuous movement, Kanban flow — all things the tool actually does |
| **What "fu" signals** | Mastery, discipline — aligned with the anti-vibe-coding message |
| **Brand family** | Keeps the "fu" lineage from codefu. The parent repo is the research lab; flowfu is the distributable product |
| **No "core" suffix** | No false expectation of a library/SDK with import/extend semantics |
| **Discoverability** | "flow" gives a partial signal for developers searching for workflow tools |
| **Length** | Two syllables, six characters, easy to type and say |

**The one weakness:** "flow" could read as "flow state" (productivity/focus) rather than "workflow." But that's arguably a feature — flow state is aspirational, workflow is mechanical. The tool delivers both: the workflow scaffolding that lets the developer stay in flow.

#### Why the tagline matters as much as the name

The name creates recognition. The tagline creates understanding. Together they need to answer "what is this and what does it give me?" in under ten words.

#### Applying FAB to the tagline

The first tagline attempt — *"Atomic commits for the agentic age"* — stopped at the feature. It's like saying "disc brakes for modern cars." True, but the benefit is you can stop safely at speed. The FAB chain for this project:

| | |
|:--|:--|
| **Feature** | Atomic commits, automated workflow, structured prompts |
| **Advantage** | Every change is one idea, independently revertible, with a reason attached |
| **Benefit** | You get AI speed without the entropy. You can change your mind safely. The codebase is still yours to steer six months in. |

The tagline needs to land at the benefit level — what the developer *feels*, not what the tool *does*.

**The recommended pairing:**

> **flowfu** — *All the speed. None of the mess.*

Eight words. No jargon. It tells you:
- **What you keep**: the speed that AI-assisted development gives you
- **What you lose**: the entropy, the tangled history, the fear of touching things
- **The implicit promise**: you don't have to choose between fast and clean

It works because every developer who's vibe-coded past day ten knows exactly what "the mess" is. They've lived it. The tagline names their pain without explaining the mechanism. The README explains the mechanism.

### What happens to "codefu"?

The naming clarifies the relationship between the two repos:

| Repo | Role | Audience |
|:-----|:-----|:---------|
| **codefu** | Research lab — AI patterns, CRAAP framework, harvest skill, experiments | You (and other methodology researchers) |
| **flowfu** | Distributable product — the three skills that ship to developers | Anyone using Claude Code |

"codefu" stays as the parent brand and research home. "flowfu" is what developers install. This is cleaner than "codefu-core" because it doesn't require understanding that a "core" was extracted from a larger thing — flowfu stands on its own.

---

## Verdict

**Is "codefu-core" the right wrapper?** No. It communicates brand (code mastery) without signalling function (workflow discipline, atomic commits). The "core" suffix implies a library extracted from a larger product, but this is markdown instructions for an AI agent. The name requires a full README read before a developer knows whether to care.

**Is this an "automatic Kanban board"?** The Kanban lifecycle is the mechanism, but it's not the product. Nobody cares that a card moved columns. If the board is invisible, it's working. The thing that *matters* is what the developer gets at the end: **a git history they can trust**.

### What's actually being sold

The core product is **atomic commits** — one idea per commit, independently revertible, with a reason attached. That's what vibe coding destroys (monolithic commits, no traceability, "updates" in the git log) and what this tool restores.

The board exists to make atomic commits happen *naturally* rather than by heroic discipline. The workflow tracks issues so the agent works on what was asked for. The craft skill sharpens input so the agent starts from clarity. But the *output* — the thing the developer actually cares about six months later — is the commit history.

**Atomic commits are the unit of trust.** The board, the workflow, the lifecycle — those exist to make atomic commits happen naturally. The board is scaffolding. The commit is the product.

### Recommendation

Rename to **flowfu**. Pair with the tagline: ***All the speed. None of the mess.***

The name signals workflow and discipline. The tagline sells the benefit — you keep AI speed without the entropy that normally comes with it. No jargon, no mechanism, just the promise. Every developer who's vibe-coded past day ten knows what "the mess" is. The tagline names their pain. The README explains the cure.

codefu stays as the research lab. flowfu is the product that ships.

---

*Analysis generated using the CRAAP framework. Updated 2026-03-31*
