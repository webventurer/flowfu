# codefu-core

![CODEFU!](designs/codefu-poster.jpg)

Claude Code skills for **atomic commits** and **Linear workflow**.

Ready to get started? See the **[install guide](INSTALL.md)** for setup instructions, requirements, and API keys.

## Why atomic commits matter

<mark>**When AI agents write code, the quality of git history becomes a make-or-break concern.**</mark>

Agents can produce large volumes of changes in a single session. Without discipline, those changes land as **monolithic commits** — impossible to review, difficult to revert, and dangerous to bisect. Atomic commits solve this by ensuring every commit contains *exactly one complete logical change*.

The `/commit` skill encodes a **four-pass methodology** that separates content decisions from formatting standards. It catches the specific atomicity mistakes that AI agents make — grouping by session, by shared prefix, or by proximity rather than by purpose. Each commit becomes independently revertible, clearly explained, and safe to ship.

## Linear integration

<mark>**The `/linear` commands connect your development workflow directly to [Linear](https://linear.app)**, the issue tracking and project management tool built for modern software teams.</mark>

Rather than context-switching between your editor and a browser, you can plan work, create issues, implement features, handle PR feedback, and close issues — all from within Claude Code. The five commands cover the **full development lifecycle**: from researching a problem and writing a well-structured issue, through to merging an approved pull request and marking it done.

This keeps the agent *grounded in real project priorities* rather than working in isolation.

## Better together

> "When faced with two or more alternatives that deliver roughly the same value, **take the path that makes future change easier**." — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

Together, these skills turn Claude Code from a capable code generator into a **disciplined engineering partner**. Atomic commits make every change traceable and reversible. Linear integration ties every change to a real objective. Both skills are installed as plain markdown files in your `.claude/` directory — no runtime dependencies, no lock-in, and fully customisable to your team's standards.

<mark>**The approach is designed to compound: as AI models improve, the structured documentation gets more from them, not less.**</mark>

## What you get

### /commit — atomic git commits

A four-pass methodology that separates content decisions from formatting standards:

1. **Pre-flight** — fix formatting, identify atomic changes
2. **Content** — stage selectively, verify one logical change
3. **Standards** — verify message format against checklists
4. **Post-commit** — verify atomicity after committing

### /linear — Linear workflow

Five commands that cover the full development cycle. See the [full workflow reference](.claude/commands/linear/reference/workflow.md) for detailed usage and examples.

| Command | What it does |
|:--------|:-------------|
| `/linear:start` | Branch, implement, PR — full cycle from a Linear issue |
| `/linear:plan-work` | Research a problem and create a Linear issue |
| `/linear:fix` | Address PR review feedback |
| `/linear:finish` | Merge approved PR and close the issue |
| `/linear:next-steps` | Review priorities and recommend next work |


## License

[MIT](LICENSE)
