# Getting started

codefu-core gives you two Claude Code skills that turn you from a **vibe coder** into an **agentic engineer** — atomic commits that make every change traceable and reversible, and a Linear workflow that ties every change to a real objective.

## Why atomic commits matter

When AI agents write code, the quality of git history becomes a make-or-break concern.

Agents can produce large volumes of changes in a single session. Without discipline, those changes land as **monolithic commits** — impossible to review, difficult to revert, and dangerous to bisect. Atomic commits solve this by ensuring every commit contains *exactly one complete logical change*.

The `/commit` skill encodes a **four-pass methodology** that separates content decisions from formatting standards. It catches the specific atomicity mistakes that AI agents make — grouping by session, by shared prefix, or by proximity rather than by purpose. Each commit becomes independently revertible, clearly explained, and safe to ship.

## Linear integration

The `/linear` commands connect your development workflow directly to [Linear](https://linear.app), the issue tracking and project management tool built for modern software teams.

Rather than context-switching between your editor and a browser, you can plan work, create issues, implement features, handle PR feedback, and close issues — all from within Claude Code. The five commands cover the **full development lifecycle**: from researching a problem and writing a well-structured issue, through to merging an approved pull request and marking it done.

This keeps the agent *grounded in real project priorities* rather than working in isolation.

## Better together

> "When faced with two or more alternatives that deliver roughly the same value, **take the path that makes future change easier**." — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

Vibe coding produces code. Agentic engineering produces **a traceable, reversible, purposeful history of decisions**. Together, `/commit` and `/linear` close that gap — every change is atomic, every change is tied to an objective, and the agent operates with the discipline of a senior engineer rather than the enthusiasm of an intern with root access.

The approach is designed to compound: as AI models improve, the structured documentation gets more from them, not less.

## Next steps

- [Install codefu-core](/install) into your project
- Learn about [atomic commits](/skills/commit)
- Set up the [Linear workflow](/skills/linear)
