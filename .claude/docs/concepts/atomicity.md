# Atomicity

> **AI Assistant Note**: When grouping work into commits, functions, transactions, deployments, or any other unit of change, reference this document for the underlying principle. Atomicity applies everywhere a unit of work needs to be coherent, complete, and indivisible.

A unit of work is atomic when it is one complete, indivisible thing. It either happens entirely or not at all. Everything inside it serves one purpose, and nothing inside it could be removed without breaking that purpose.

## 🚨 Quick reference

**The atomic test**: Can you remove any part and still have a coherent whole? If yes, the removed part does not belong. If removing it leaves a hole, it does.

**The revert test**: If you undo this unit of work, does exactly one logical thing disappear? If more than one thing disappears, it was not atomic.

**Atomicity is not about size.** An atomic unit can touch many files, many lines, many systems — as long as all of them serve one indivisible purpose.

## The principle

Atomicity means **one complete logical change**. Not small. Not simple. Complete and singular in purpose.

The word comes from the Greek *atomos* — uncuttable. <mark>An atomic unit of work is one that should not be divided further because dividing it would break the coherence of the change.</mark>

## Where atomicity appears

### Git commits

Each commit should represent one logical improvement. A bug fix is one commit. A feature is one commit. A refactoring is one commit. Mixing a bug fix and a feature in one commit violates atomicity — reverting the commit would undo two unrelated things.

See [atomic git commits](../patterns/git/atomic-git-commits.md) for the full commit-specific methodology.

### Functions and methods

A function should do one thing. This is the [single responsibility principle](../principles/single-responsibility-principle.md) applied at the function level. If a function calculates a total and also sends an email, it is doing two things. The email and the calculation are independently meaningful — they can and should be separated.

### Classes

A class should have one reason to change — one responsibility. If a class handles user authentication and also formats email templates, those are two independent concerns. Changes to email formatting should not require touching authentication logic. Each responsibility belongs in its own class.

### Database transactions

A transaction groups operations that must all succeed or all fail together. Debiting one account and crediting another is atomic — doing only one half is worse than doing neither. This is the textbook definition of atomicity from ACID properties.

### Deployments

A deployment should ship one coherent change. Bundling unrelated features into one deploy makes rollback dangerous — you cannot undo one feature without undoing the other.

### Pull requests

A PR should be one reviewable unit with a single purpose. Mixing unrelated changes makes review harder and merging riskier.

## Atomicity vs size

The most common misunderstanding is that atomic means small. It does not.

- Renaming a function across 30 files is atomic — one logical change
- A single file with a bug fix and an unrelated refactoring is not atomic — two logical changes

**Size is irrelevant. Purpose is everything.** The question is never "how big is this?" but "how many distinct purposes does this serve?"

## How to test for atomicity

### The removal test

For each part of the unit of work, ask: if I removed this part, would the rest still be a coherent, complete change?

- If yes: the removed part does not belong. It serves a different purpose.
- If no: it belongs. Removing it would leave the change incomplete.

### The revert test

If you undid this entire unit of work, would exactly one logical thing disappear from the system?

- If one thing disappears: atomic
- If multiple unrelated things disappear: not atomic

### The description test

Can you describe the unit of work in one sentence without using "and" to join unrelated ideas?

- "Fix null check in payment validation" — atomic
- "Fix null check in payment validation and update the README" — not atomic (unless the README change documents the fix)

## Common violations

### Proximity bias

Changes that are near each other in time, space, or workflow feel like they belong together. They often don't.

- Modified in the same session — not a reason to combine
- In the same file — not a reason to combine
- Part of the same task — not a reason to combine
- Using the same commit prefix — not a reason to combine

### "While I was in there"

Noticing something to fix while working on something else. The noticed fix is a separate unit of work. Do it separately.

### Convenience grouping

Combining things because it is easier to ship them together. Easier now, harder to revert, review, or understand later.

## The relationship to SRP

Atomicity and the [single responsibility principle](../principles/single-responsibility-principle.md) are expressions of the same underlying idea at different scales:

- **SRP** asks: does this code entity have one reason to change?
- **Atomicity** asks: does this unit of work represent one logical change?

SRP is about structure. Atomicity is about action. Both answer the question: **is this one thing or multiple things pretending to be one thing?**

---

*One purpose, one unit. The test is always the same: can you cut it, or is it already indivisible?*
