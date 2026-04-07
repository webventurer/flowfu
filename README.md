# flowfu

**All the speed. None of the mess.**

AI agents write code fast. But without structure, that speed turns into entropy — monolithic commits, untraceable history, and a codebase you're afraid to touch by day thirty.

flowfu gives you **atomic commits** — every change is one idea, independently revertible, with a reason attached. You get AI speed *and* a git history you can trust. That's the trade: you don't have to choose between fast and clean.

Everything installs as plain markdown into your `.claude/` directory. No runtime dependencies, no lock-in — read it, change it, make it yours.

## What you get

**`/linear`** — Five commands covering the full development cycle. Plan work, create issues, implement on a branch, handle PR feedback, merge and close — all driven from Claude Code, all synced with [Linear](https://linear.app). Issues flow through your board automatically as you work.

![Kanban board](docs/public/kanban-board.svg)
*Issues flow from Backlog through In Progress to Done — driven entirely by `/linear` commands.*

**`/commit`** — Four-pass atomic commits, called by `/linear` at every commit point. The agent stages selectively, checks coherence, verifies formatting, and writes commit messages that explain *why*, not just what. Every commit is one complete logical change, independently revertible.

![Commit pipeline](docs/public/commit-pipeline.svg)
*Four passes separate content decisions from formatting standards — catching the mistakes AI agents make.*

**`/craft`** — Structured prompt generation using the **C.R.A.F.T.** framework (Context, Role, Action, Format, Target). Built into `/linear:plan-work --craft` to sharpen issue descriptions *before* the agent drafts them. Without it, the agent works from whatever you typed — ambiguity in, ambiguity out. With it, you get a clear problem statement, well-scoped goals, and acceptance criteria that the agent can actually execute against.

## The loop

The skills aren't independent — each one feeds the next.

`/craft` sharpens the problem. `/linear` turns it into a tracked issue and manages the full lifecycle. `/commit` records each change as one atomic, revertible unit. Remove any piece and the loop still works, but the output gets worse.

## Install

```bash
npx github:webventurer/flowfu
```

This copies skills, commands, hooks, and docs into your project. It merges hook config into your existing `.claude/settings.json` (or creates one). Nothing is installed globally.

## Quick start

```bash
# Verify Linear MCP connections
/linear:check

# See what needs doing
/linear:next-steps

# Plan and create an issue
/linear:plan-work "add dark mode toggle"

# Implement it — branch, code, test, PR
/linear:start PG-123

# Commit your changes
/commit

# Address review feedback
/linear:fix PG-123

# Merge, clean up, done
/linear:finish PG-123
```

## Why this exists

Vibe coding is great on day one. By day ten you can't tell which change broke things. By day thirty you're afraid to touch anything. By day ninety you're rewriting from scratch.

flowfu trades a few minutes of setup for months of maintainability. Atomic commits make reverting safe. Linear integration makes priorities visible. Structured prompts make the agent's starting point explicit. The structure compounds — as AI models improve, it gets *more* from them, not less.

Read more about [agentic engineering](docs/reference/agentic-engineering.md) — the philosophy behind the approach.

## Docs

Full documentation at the [docs site](https://webventurer.github.io/flowfu) or run locally:

```bash
pnpm dev
```

## Built by

![flowfu](docs/public/flowfu-hero.svg)

[@mikemindel](https://github.com/mikemindel)

## License

[MIT](LICENSE)
