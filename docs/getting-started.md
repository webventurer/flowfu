# Getting started

codefu-core gives you two Claude Code skills that turn you from a **vibe coder** into an **agentic engineer** — atomic commits where every commit is one complete conceptual unit of work, and a [Linear](https://linear.app) workflow that lets you plan work, create issues, track progress, and ship features through a structured product management cycle — all without leaving the terminal.

## Why atomic commits matter

When AI agents write code, the quality of git history becomes a make-or-break concern.

Agents can produce large volumes of changes in a single session. Without discipline, those changes land as **monolithic commits** — impossible to review, difficult to revert, and dangerous to bisect. Atomic commits solve this by ensuring every commit contains *exactly one complete logical change*.

The `/commit` skill encodes a **four-pass methodology** that separates content decisions from formatting standards. It catches the specific atomicity mistakes that AI agents make — grouping by session, by shared prefix, or by proximity rather than by purpose. Each commit becomes independently revertible, clearly explained, and safe to ship.

## Linear integration

![Kanban board](/kanban-board.svg)
*Issues flow from Backlog through Doing to Done, driven entirely by `/linear` commands.*

The `/linear` commands connect your development workflow directly to [Linear](https://linear.app). This is an opinionated choice — Linear is keyboard-driven, git-integrated, and built for the way modern software teams actually work. No drag-and-drop boards, no workflow bloat.

Rather than context-switching between your editor and a browser, you can plan work, create issues, implement features, handle PR feedback, and close issues — all from within Claude Code. The five commands cover the **full development lifecycle**: from researching a problem and writing a well-structured issue, through to merging an approved pull request and marking it done.

This keeps the agent *grounded in real project priorities* rather than working in isolation.

## Better together

> "When faced with two or more alternatives that deliver roughly the same value, **take the path that makes future change easier**." — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

Vibe coding produces code. Agentic engineering produces **a traceable, reversible, purposeful history of decisions**. Together, `/commit` and `/linear` close that gap — every change is atomic, every change is tied to an objective, and the agent operates with the discipline of a senior engineer rather than the enthusiasm of an intern with root access.

The approach is designed to compound: as AI models improve, the structured documentation gets more from them, not less.

## App starters

codefu-core gives you the engineering workflow. App starters give you the project scaffold. Each starter is an opinionated template that gets you from zero to a working app in one command — with codefu-core's skills already wired in.

### [app-starter](https://github.com/webventurer/app-starter)

A modern full-stack web app starter — React + TypeScript + Vite on the frontend, Hono + Neon + Clerk + Drizzle on the backend. Every layer is independently replaceable — swap one piece without rewiring the rest. Includes shadcn/ui for components, Biome for formatting, and reference docs that explain every technology choice.

```bash
gh repo clone webventurer/app-starter
./app-starter/scripts/create.sh my-app
```

## Next steps

- [How it works](/how-it-works) — see what gets installed and how the pieces connect
- [Install codefu](/install) into your project
- Learn about [atomic commits](/skills/commit)
- Set up the [Linear workflow](/skills/linear)
- Generate better prompts with [/craft](/skills/craft)
