---
name: commit
description: Create atomic git commits using a four-pass methodology — content, standards, final review, and post-commit verification. Use when committing code or documentation changes. Triggers on "commit", "git commit", or when the user asks to commit changes.
---

# Commit

> Create atomic git commits using a four-pass methodology that separates content decisions from formatting standards.

## Skill documents

| File | Purpose |
|:-----|:--------|
| [SKILL.md](SKILL.md) | Overview, commit format reference, atomicity rules |
| [WORKFLOW.md](WORKFLOW.md) | Four-pass execution sequence |
| [references/chris-beams-commit-style.md](references/chris-beams-commit-style.md) | The 7 rules our format is built on |

---

## When to use

- User asks to commit staged or unstaged changes
- User runs `/commit`
- Changes are ready and the user explicitly requests a commit

## When NOT to use

- User is exploring changes or running `git diff`
- No changes exist to commit
- User has not explicitly asked for a commit

---

## Quick reference

<mark>**One logical change per commit. Separate concerns across four passes: content, standards, final review, post-commit verification.**</mark>

---

## Required reading

Read before executing:

1. `.claude/docs/patterns/git/atomic-git-commits.md` — the full atomic commit methodology and Conventional Commits standard

---

## Key principles

| Principle | What it means |
|:----------|:-------------|
| Atomic | One complete logical change per commit — not by size, by coherence |
| Imperative mood | "Add feature" not "Added feature" — completes "If applied, this commit will..." |
| WHY not what | Body explains the reasoning, not just a list of files |
| Working state | All tests pass after the commit |
| Selective staging | Stage files per logical change, not everything at once |

### Test-driven commits

Every commit should pass all tests:

1. Write failing tests for new functionality
2. Implement the feature
3. Ensure all tests pass
4. Commit the complete change

This ensures each commit represents a working state of the codebase.

---

## The coherence test

> If you removed any file from this commit, would the remaining files still represent the same complete logical change?

- If removing a file leaves a hole → it belongs
- If removing a file leaves a perfectly coherent commit → it does not belong

### The "and" test

<mark>**If your commit message contains "and", you probably have two commits.**</mark> "Add login validation **and** fix header styling" is two changes wearing a trench coat. If you can't describe the commit without "and", split it.

---

## The atomicity balance

Atomicity has two failure modes, not one:

**Over-atomising** (too many commits):
- Splitting a one-line CSS fix and a related prop addition into separate commits
- Committing a function rename separately from updating its callers
- One commit per file when all files serve the same change

**Under-atomising** (too few commits):
- Lumping a bug fix, a new feature, and a formatting cleanup into one commit
- Committing everything changed in a session as a single commit
- Mixing unrelated changes that happened to touch the same area

**The sweet spot**: all changes share a common purpose that you can explain in one sentence. If removing any change leaves a hole, it belongs. If adding another change would require a second explanation, it doesn't.

**The test**: look in both directions. Ask "am I grouping unrelated things?" (under-atomising) AND "am I splitting apart things that need each other?" (over-atomising). When neither question raises a flag, you've found the right granularity.

---

## Common AI atomicity mistakes

<mark>**These are not valid reasons for combining changes into one commit:**</mark>

- **Modified in the same session** — files changed during one conversation are not automatically one atomic commit
- **Sharing a prefix** — using `docs:` on two unrelated documentation changes does not make them atomic
- **Requested as one task** — "update the docs and fix the bug" is two tasks and two commits
- **Touching the same area** — editing three files in `src/auth/` for different reasons is three commits
- **"While I was in there" changes** — noticing a typo while fixing a bug does not make the typo part of the bug fix
- **Produced by the same tool** — a test survey flags 3 files that need tests. Each test suite is its own commit. They share a prefix (`test:`) and came from the same analysis, but removing one leaves the others perfectly coherent
- **Same change in different places** — applying the same refactor to two independent directories is two commits, not one. Each stands alone — either could be reverted without breaking the other
- **Tests for pre-existing code** — <mark>**did the production code exist before this session?**</mark> If yes, tests are a separate `test:` commit. If no (new class + its test file), they belong together

**Example of mixed changes that should be separated**:

```bash
# BAD: Two different logical changes in one commit
git add TODO.md docs/research/ai-coding/what-is-a-frame.md
# This mixes: project management (TODO) + documentation (frame concept)

# GOOD: Separate atomic commits
git add TODO.md
.claude/hooks/do_commit.sh -m "build: Add TODO.md with AI frame loading system entry"

git add docs/research/ai-coding/what-is-a-frame.md
.claude/hooks/do_commit.sh -m "docs: Create comprehensive frame concept documentation"
```

---

## Content focus blindness

Both people and AI consistently miss formatting standards while focused on content logic. The four-pass approach solves this by making standards verification a dedicated step (Pass 2) separate from content decisions (Pass 1).

---

## Commit message format

```text
<type>: <Subject line — 50 chars max>

<Body explaining WHY — wrap at 72 chars>

- Bullet points for specific changes
```

### Standard prefixes

| Prefix | Use for |
|:-------|:--------|
| `feat:` | New features or functionality |
| `fix:` | Bug fixes and corrections |
| `docs:` | Documentation only changes |
| `refactor:` | Code restructuring without changing behaviour |
| `style:` | Formatting, white-space changes |
| `test:` | Adding or updating tests |
| `build:` | Build system or dependency changes |
| `chore:` | Maintenance tasks |
| `perf:` | Performance improvements |
| `ci:` | CI configuration changes |

### Subject line rules

- Standard prefix, lowercase (e.g. `feat:`, `fix:`)
- Capitalize first word after colon ("Add" not "add")
- Imperative mood ("Add" not "Added")
- No period at end
- Under 50 characters total

### Body rules

- Blank line after subject
- Wrap at 72 characters
- Explain WHY, not just what
- Start with explanatory paragraph before bullets
- Add warmth — show care for users and future developers

### Example

```text
fix: Fix null pointer in payment validation

When users had incomplete billing data, validation would crash
instead of showing helpful errors. This adds proper null checks
and returns meaningful validation messages.

- Add null checks for all required fields
- Return validation errors instead of exceptions
- Include tests for edge cases with missing data
```

---

## The pre-commit atomicity trap

Pre-commit hooks can accidentally cause you to commit multiple unrelated files together:

1. You stage one file: `git add file1.js`
2. You run `git commit` and hooks fix OTHER files
3. You run `git add -A` to include the fixes
4. **Result**: your commit now includes unrelated files

**Prevention**: Run the repo's hooks manually in Pass 0 (see [WORKFLOW.md](WORKFLOW.md)). This fixes all formatting upfront so hooks have nothing to fix during the actual commit.

---

## Execution

<mark>**Read and follow every step in [WORKFLOW.md](WORKFLOW.md).**</mark>

---

## The governing principle

> Make each commit a gift to your future self — one complete idea, clearly explained, independently revertible.
