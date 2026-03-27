# /commit — Atomic git commits

AI agents make specific atomicity mistakes — grouping changes by session, by shared prefix, or by proximity rather than by purpose. The `/commit` skill catches these through a four-pass methodology that separates content decisions from formatting standards.

## The four passes

| Pass | Action | Goal |
|:-----|:-------|:-----|
| 0 | **Pre-flight** | Fix formatting, identify atomic changes |
| 1 | **Content** | Stage selectively, verify one logical change |
| 2 | **Standards** | Verify message format against checklists |
| 3 | **Final review** | Sanity check before committing |
| 4 | **Post-commit** | Verify atomicity after committing |

## Pass 0: Pre-flight

Run the formatter first. Every time. Then review what changed with `git status` and `git diff`.

**Per-file independence gate**: if 2+ files are changed, write one sentence per file describing what it does independently. If a sentence is incomplete without another file, they belong together. If every sentence stands alone, each is a separate commit.

## Pass 1: Content

Stage the right files for one atomic change:

1. Stage selectively — `git add` specific files, not `git add -A`
2. Review staged changes — `git diff --cached`
3. Verify completeness — are all files needed for this change staged?
4. Apply the coherence test — does removing any file leave a hole?

## Pass 2: Standards

Draft the commit message and verify formatting:

### Subject line checklist

- No "and" in the subject — if present, split into separate commits
- Standard prefix used (`feat:`, `docs:`, `fix:`, `refactor:`, `style:`, `test:`, `build:`, etc.)
- Subject capitalised after colon ("feat: Add feature" not "feat: add feature")
- Imperative mood ("Add" not "Added" or "Adds")
- Under 50 characters total
- No period at end

### Body checklist

- Blank line after subject
- Wrap at 72 characters
- Explains **why**, not just what changed
- Start with explanatory paragraph before bullet points

## Pass 3: Final review

Last sanity check — does this commit represent one complete idea? Can it be reverted independently? Would it make sense to someone reviewing it in 6 months?

## Pass 4: Post-commit verification

Verify the commit is truly atomic after it lands:

```bash
git diff --stat HEAD~1 HEAD
git log -1
```

All files should serve the single purpose described in the commit message. No hitchhikers, no stowaways.

If 2+ commits were made in the session, review them as a set — check that files landed in the right commit and the commits tell a clear story.
