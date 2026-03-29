# /commit — Atomic git commits

AI agents make specific atomicity mistakes — grouping changes by session, by shared prefix, or by proximity rather than by purpose. The `/commit` skill catches these through a four-pass methodology that separates content decisions from formatting standards.

![Commit pipeline](/commit-pipeline.svg)
*Four passes separate content decisions from formatting standards — catching the mistakes AI agents make.*

Commit messages follow the [Chris Beams commit style](/reference/commit-style) — the de facto standard for clear, human-readable git history.

## What makes a commit atomic?

An atomic commit is:

- **One complete idea** — everything needed for a single logical change
- **Self-contained** — can be understood and reviewed independently
- **Functional** — all tests pass after the commit
- **Reversible** — can be reverted without breaking other functionality

It's not about size. A single atomic commit might touch many files — what matters is that **all changes relate to one logical improvement**. If you can revert it and remove exactly one complete improvement, it's atomic.

## Common AI atomicity mistakes

AI assistants frequently group files into commits based on the wrong criteria:

- **Modified in the same session** — files changed during one conversation are not automatically one commit
- **Sharing a prefix** — using `docs:` on two unrelated doc changes does not make them atomic
- **Requested as one task** — "update the docs and fix the bug" is two commits
- **Touching the same area** — editing three files in `src/auth/` for different reasons is three commits
- **"While I was in there" changes** — noticing a typo while fixing a bug does not make the typo part of the bug fix

## The four passes

| Pass | Action | Goal |
|:-----|:-------|:-----|
| 0 | **Pre-flight** | Fix formatting, identify atomic changes |
| 1 | **Content** | Stage selectively, verify one logical change |
| 2 | **Standards** | Verify message format against checklists |
| 3 | **Final review** | Sanity check before committing |
| 4 | **Post-commit** | Verify atomicity after committing |

## Pass 0: Pre-flight

Run the formatter first. Every time. If the pre-commit hook finds things to fix, it changes the working tree but not the staged copy — leaving an orphaned diff after every commit.

Then review what changed with `git status` and `git diff`.

**Per-file independence gate**: if 2+ files are changed, write one sentence per file describing what it does independently. If a sentence is incomplete without another file, they belong together. If every sentence stands alone, each is a separate commit.

## Pass 1: Content

Stage the right files for one atomic change:

1. **Stage selectively** — `git add` specific files, not `git add -A`
2. **Review staged changes** — `git diff --cached`
3. **Verify completeness** — are all files needed for this change staged?
4. **Apply the coherence test** — does removing any file leave a hole?

**The coherence test**: if you removed any file from the commit, would the remaining files still represent the same complete logical change? If removing a file leaves a hole, it belongs. If removing a file leaves a perfectly coherent commit, it doesn't belong.

## Pass 2: Standards

Draft the commit message and verify formatting.

### Subject line checklist

- No "and" in the subject — if present, split into separate commits
- Standard prefix used (`feat:`, `docs:`, `fix:`, `refactor:`, `style:`, `test:`, `build:`, etc.)
- Subject capitalised after colon ("feat: Add feature" not "feat: add feature")
- Imperative mood ("Add" not "Added" or "Adds")
- Under 50 characters total
- No period at end
- Completes: "If applied, this commit will **[your subject]**"

### Body checklist

- Blank line after subject
- Wrap at 72 characters
- Explains **why**, not just what changed
- Start with explanatory paragraph before bullet points
- Show care for users and future developers

### Warm vs cold

A cold commit message is technically correct but misses the human context:

> Fix validation bug — Null check added to prevent NPE in payment processing.

A warm commit message explains the same fix but acknowledges the impact:

> Fix payment validation for incomplete user data — When users had incomplete billing addresses, payment validation would crash instead of showing helpful error messages. This adds proper null checks and returns meaningful feedback to guide users toward successful completion.

## Pass 3: Final review

Last sanity check before the commit lands:

- Does this commit represent one complete idea?
- Do all tests pass?
- Re-read the commit message — does it tell a complete story?
- Can this be reverted independently?
- Would this make sense to someone reviewing it in 6 months?

## Pass 4: Post-commit verification

Verify the commit is truly atomic after it lands. All files should serve the single purpose described in the commit message. No hitchhikers (files that could be removed and leave a coherent change), no stowaways (files that serve a different purpose).

If 2+ commits were made in the session, review them as a set — check that files landed in the right commit and the commits tell a clear story reading the log forward. A file that belongs to commit B but ended up in commit A passes individual review but fails the session check.

## Commit prefixes

Standard prefixes following the [Conventional Commits](https://www.conventionalcommits.org/) specification:

| Prefix | Use for |
|:-------|:--------|
| `feat:` | New features or functionality |
| `fix:` | Bug fixes and corrections |
| `docs:` | Documentation only changes |
| `refactor:` | Code restructuring without changing functionality |
| `style:` | Formatting, whitespace — no logic changes |
| `test:` | Adding or correcting tests |
| `build:` | Build system or dependency changes |
| `perf:` | Performance improvements |
| `ci:` | CI configuration changes |

Prefixes can include a scope: `feat(auth):`, `fix(api):`, `docs(git):`. Prefixes are always lowercase, subject line is always sentence case.

## Example commits

### Adding a feature

> **feat: Add user profile photo upload**
>
> Implements file upload with validation, resizing, and S3 storage.
> Includes error handling for unsupported formats and file size limits.
>
> - Add upload endpoint with multipart/form-data support
> - Implement image validation and resizing pipeline
> - Configure S3 bucket with proper permissions

### Fixing a bug

> **fix: Fix null pointer exception in payment processing**
>
> When users had incomplete billing addresses, payment validation
> would throw NPE instead of showing helpful error message.
>
> - Add null checks for all address fields
> - Return validation errors instead of throwing exceptions

### Refactoring

> **refactor: Extract email validation into reusable service**
>
> Email validation logic was duplicated across registration,
> profile updates, and invitation flows. Consolidating into
> a single service improves maintainability and consistency.

## Q&A

### Multiple changes in one file — one commit or many?

Apply the coherence test. If all changes serve the same logical purpose, it's one commit. If they solve different problems, split them.

**One commit** — all changes enhance the same process:
- Add "fix formatting first" step
- Add "identify multiple changes" step
- Update verification checklist

**Multiple commits** — independent changes that happen to be in the same file:
- Fix bug in `validateEmail` function
- Add new `formatPhoneNumber` function
- Refactor existing `parseDate` function

### What if my commit touches many files?

File count doesn't determine atomicity — logical coherence does. Renaming a function across 15 files is one atomic commit. Adding a feature that needs component + styles + tests + docs is one atomic commit. The test: can you revert it and remove exactly one complete improvement?

### Cleanup mixed with features?

Always separate. You want to be able to revert the feature without losing formatting fixes, or vice versa.

## What not to mix

Avoid combining these in a single commit:

- Feature implementation + unrelated bug fix
- Code changes + dependency updates
- Multiple unrelated refactors
- Feature code + formatting changes

Each gets its own commit — you want to be able to revert the feature without losing the formatting fixes, or vice versa.

## Benefits

### For you
- **Easier debugging** — use `git bisect` to find exactly when issues were introduced
- **Cleaner history** — each commit tells a clear story
- **Better reviews** — reviewers can understand each change independently
- **Safe experiments** — easy to revert specific changes without affecting others

### For future developers
- **Clear intent** — each commit explains why a change was made
- **Better archaeology** — `git blame` and `git log` provide meaningful context
- **Easier maintenance** — can modify or revert specific functionality

### For AI assistance
- **Better context** — AI can understand the purpose of each change
- **Clearer patterns** — atomic commits help AI learn your coding patterns
- **Enhanced code review** — AI tools can provide better insights on focused changes

## Under the hood

This page is the human-readable overview. The full agent specification — including the coherence test edge cases, the pre-commit atomicity trap, and the session coherence check — lives in `.claude/skills/commit/SKILL.md` and `.claude/skills/commit/WORKFLOW.md` inside your project after [installation](/install). Those files are what the agent actually follows when you run `/commit`.
