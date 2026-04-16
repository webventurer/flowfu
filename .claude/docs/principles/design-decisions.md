# Design decisions

> **AI Assistant Note**: Before every design choice — naming, structure, scope, abstraction, dependency — check it against these principles. They are not guidelines to consider; they are constraints to obey.

| # | Principle | Meaning |
|:--|:----------|:--------|
| 1 | [Choose the path that makes change easier](#choose-the-path-that-makes-change-easier) | The universal principle |
| 2 | [Postpone decisions](#postpone-decisions) | Don't decide until a requirement forces you to |
| 3 | [One reason to change](#one-reason-to-change) | SRP for code, commits, PRs, issues |
| 4 | [Be atomic](#be-atomic) | One purpose per unit of work |
| 5 | [Do the simplest thing that works](#do-the-simplest-thing-that-works) | Obvious over clever |
| 6 | [YAGNI](#yagni--you-aint-gonna-need-it) | Don't build it until you need it |

## Choose the path that makes change easier

> "When faced with two or more alternatives that deliver roughly the same value, **take the path that makes future change easier**."
> — David Thomas & Andrew Hunt, *The Pragmatic Programmer*

This is the universal principle. Every other principle in this document is a specific expression of it.

When you choose between two approaches and the immediate value is roughly equal, ask: **which one leaves more options open?** Pick that one. The future developer — human or AI — will inherit your decision. Make it a gift, not a burden.

## Postpone decisions

Any decision you make in advance of an explicit requirement is just a guess. Don't decide; **preserve your ability to make a decision later** when you must.

When the future cost of doing nothing equals the current cost, postpone the decision. **Wait for a new requirement** — it supplies the exact information you need to make the next design decision.

If code has no dependencies and changes to it have no consequences, it doesn't matter if it's imperfect. When it acquires dependencies, those dependencies will supply the information you need to make good design decisions.

## One reason to change

A function, class, or module should have **one reason to change**. If describing it requires the word "and" to join unrelated ideas, it has too many responsibilities. Split it.

This applies to commits, PRs, and issues too — not just code.

## Be atomic

One commit, one purpose. One function, one job. One PR, one deliverable. If you can describe it without "and" joining unrelated ideas, it's atomic. If you can't, split it.

Atomicity is not about size — a rename across 30 files is atomic. A single file with a bug fix and an unrelated refactor is not. **Purpose is everything.**

## Do the simplest thing that works

Prefer the obvious solution over the clever one. The best code is code you don't write — and the second best is code anyone can read.

## YAGNI — You Ain't Gonna Need It

Don't build it until you need it. Three similar lines are better than a premature abstraction. An unused extension point is not foresight — it's clutter that the next developer must understand, maintain, and work around.

## The test

Before committing to a design choice, ask:

1. **Does this close doors?** If yes, can we avoid closing them?
2. **Does this add complexity for a requirement that doesn't exist yet?** If yes, remove it.
3. **Would a developer seeing this for the first time understand why it's here?** If no, simplify.

*Design is more the art of preserving changeability than it is the act of achieving perfection.*
