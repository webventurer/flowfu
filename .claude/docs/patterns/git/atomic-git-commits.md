# Atomic git commits

**Required reading**: [Atomicity](../../concepts/atomicity.md) — the underlying principle that this document applies to git commits.

**Commit workflow**: The four-pass commit workflow (content, standards, final review, post-commit) lives in `.claude/skills/commit/` — use `/commit` to execute it.

## Overview

Atomic git commits follow the principle of "one responsibility per commit" - just like one responsibility per class and one responsibility per method. Each commit should represent one complete, logical change that makes sense on its own and leaves the codebase in a working state.

## 🎯 The atomic principle

### What makes a commit atomic?

An atomic commit is:

- **One complete idea** - Everything needed for a single logical change
- **Self-contained** - Can be understood and reviewed independently
- **Functional** - All tests pass after the commit
- **Reversible** - Can be reverted without breaking other functionality

### It's not about size

Atomic commits are **not** about keeping commits small. A single atomic commit might include:

- Multiple files modified
- New tests written
- Documentation updated
- Configuration changes

The key is that **all changes relate to one logical improvement** which can include new features, refactoring, a documentation update, a configuration change, a fix etc.

The atomic principle is about logical cohesion; the commit should represent one complete, logical improvement to the codebase.

### Common AI atomicity mistakes

AI assistants frequently group files into commits based on the wrong criteria. These are **not** valid reasons for combining changes into one commit:

- **Modified in the same session** - Files changed during one conversation are not automatically one atomic commit. Each logical change gets its own commit regardless of when it was made.
- **Sharing a prefix** - Using `docs:` on two unrelated documentation changes does not make them atomic. The prefix describes the type; atomicity requires a shared logical purpose.
- **Requested as one task** - Being asked "update the docs and fix the bug" is two tasks and two commits, even though it was one instruction.
- **Touching the same area** - Editing three files in `src/auth/` for different reasons is three commits, not one "auth changes" commit.
- **"While I was in there" changes** - Noticing a typo while fixing a bug does not make the typo part of the bug fix. Separate commits.

**The test**: If you removed any file from the commit, would the remaining files still represent the same complete logical change? If removing a file leaves a hole, it belongs. If removing a file leaves a perfectly coherent commit, it does not belong.

## Commit prefixes

### Standard prefixes

Using consistent prefixes helps categorize commits and makes git history more scannable. Here are the standard prefixes we use, following the Conventional Commits standard:

**Feature and development**:

- `feat:` - New features or functionality
- `build:` - Changes that affect the build system or external dependencies

**Maintenance and fixes**:

- `fix:` - Bug fixes and corrections
- `perf:` - A code change that improves performance
- `ci:` - Changes to our CI configuration files and scripts

**Code quality**:

- `refactor:` - Code restructuring without changing functionality
- `style:` - Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- `test:` - Adding missing tests or correcting existing tests

**Documentation and build**:

- `docs:` - Documentation only changes
- `build:` - Changes that affect the build system, dependencies, or development tools

### Using prefixes with scope

Prefixes can be enhanced with scope information in parentheses:

**Examples**:

- `feat(auth):` - New authentication feature
- `fix(api):` - API-related bug fix
- `docs(git):` - Git-related documentation
- `test(models):` - Tests for data models
- `refactor(utils):` - Utility function refactoring

### Capitalization and casing

- **Prefixes are always lowercase**: `feat:`, `fix:`, `style:`
- **The subject line is always sentence case**: `Add new feature`, `Fix critical bug`

This is the standard convention and is critical for automated tools that parse commit messages.

- ✅ `docs(git): Add branch management guide`
- ❌ `Docs(git): Add branch management guide`
- ❌ `docs(git): add branch management guide`

This maintains readability while providing clear categorization of changes.

### 📝 The Conventional Commits standard

Our commit message format is based on the [Conventional Commits specification](https://www.conventionalcommits.org/), a widely adopted standard that creates a lightweight but explicit structure for commit messages.

**Why it matters**:

- **Automation**: Allows tools to automatically generate changelogs, determine version bumps (following Semantic Versioning), and trigger builds.
- **Clarity**: Creates a clear and scannable commit history for human developers.
- **Consistency**: Provides a shared, explicit language for describing changes.

### Template

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- **`<type>`**: Must be one of the lowercase prefixes (`feat`, `fix`, `docs`, etc.).
- **`<description>`**: A short summary of the change in sentence case.
- **`<body>`**: A longer, more detailed explanation of the _what_ and _why_.
- **`<footer>`**: Used for referencing issue numbers (e.g., `Fixes #123`).

By following this standard, we ensure our commit history is not only human-readable but also machine-readable, enabling powerful automation and improving our development workflow.

## Commit message format

We combine the above with the **Chris Beams style** - human-readable logs that AI can also understand:

### Template

```text
Capitalized imperative subject line

Optional longer body explaining the *why*, not just the what.
```

### Example

```bash
Fix null values in user profile

When users didn't have complete profile data, nulls caused crashes.
This patch ensures default values are set for all required fields.
```

### Example with optional actions

```bash
Update documentation: Use .content instead of .page class

Semantic Purpose: .content describes the semantic role (content container)
rather than location (page). This provides:

- Better semantic clarity about the container's purpose
- Improved reusability across different content areas
- Consistency with actual implementation in page.module.scss
- More flexible naming that works for articles, modals, etc.

Documentation now matches the codebase implementation.
```

## 🎨 Writing great commit messages

### Subject line rules

1. **Use imperative mood** - "Fix", not "Fixed" or "Fixes"
2. **Capitalize first letter** - "Add feature" not "add feature"
3. **Limit to 50 characters** - Forces concise, clear descriptions
4. **No period at end** - Subject lines are like email subjects

### Imperative examples

✅ **Good (Imperative)**:

- Add UNIFIED account type
- Fix rate limit bursts
- Update fetch_balance to pass coins
- Refactor \_build_balance_params

❌ **Avoid (Non-imperative)**:

- Added UNIFIED account type
- Fixes rate limit bursts
- Updating fetch_balance
- Refactored build_balance_params

### The "if applied" test

A good subject line completes this sentence:

> "If applied, this commit will **[your subject line]**"

Examples:

- "If applied, this commit will **Add user authentication**"
- "If applied, this commit will **Fix memory leak in parser**"

### Body guidelines

1. **Wrap at 72 characters** - Ensures readability in all git tools
2. **Explain the WHY** - Not just what changed, but why it was necessary
3. **Provide context** - Help future developers understand the decision
4. **Reference issues** - Link to tickets, discussions, or requirements

### Adding warmth and humanity

While staying technical, commit messages can be warm and inviting:

**In the WHY section, consider**:

- Acknowledging the human impact: "This makes the experience less frustrating for users"
- Explaining the care behind decisions: "The new filename better reflects..."
- Using inclusive language: "helps future developers" rather than just "improves code"
- Showing empathy: "When users encountered this error, it was confusing..."

**Examples of warm technical writing**:

❄️ **Cold but correct**:

```bash
Fix validation bug

Null check added to prevent NPE in payment processing.
```

🔥 **Warm and technical**:

```bash
Fix payment validation for incomplete user data

When users had incomplete billing addresses, payment validation
would crash instead of showing helpful error messages. This
change adds proper null checks and returns meaningful feedback
to guide users toward successful completion.
```

The warm version explains the same technical fix but acknowledges the user experience and shows care for both users and future maintainers.

### Commit message width conventions

👉 **So: 50 chars for the subject, 72 for the body.**
That's the sweet spot almost every style guide (and git log formatting) assumes.

## 📊 Benefits of atomic commits

### For you

- **Easier debugging** - Use `git bisect` to find exactly when issues were introduced
- **Cleaner history** - Each commit tells a clear story
- **Better reviews** - Reviewers can understand each change independently
- **Safe experiments** - Easy to revert specific changes without affecting others

### For future developers

- **Clear intent** - Each commit explains why a change was made
- **Easier maintenance** - Can modify or revert specific functionality
- **Better archaeology** - `git blame` and `git log` provide meaningful context
- **Reduced confusion** - No mixed concerns in single commits

### For AI assistance

- **Better context** - AI can understand the purpose of each change
- **Clearer patterns** - Atomic commits help AI learn your coding patterns
- **Improved suggestions** - AI can reference specific, logical changes
- **Enhanced code review** - AI tools can provide better insights on focused changes

## 🎯 Common scenarios

### Adding a new feature

```bash
Add user profile photo upload

Implements file upload with validation, resizing, and S3 storage.
Includes error handling for unsupported formats and file size limits.

- Add upload endpoint with multipart/form-data support
- Implement image validation and resizing pipeline
- Configure S3 bucket with proper permissions
- Add comprehensive error handling and user feedback
- Include tests for all upload scenarios
```

### Fixing a bug

```bash
fix: Fix null pointer exception in payment processing

When users had incomplete billing addresses, payment validation
would throw NPE instead of showing helpful error message.

- Add null checks for all address fields
- Return validation errors instead of throwing exceptions
- Add tests covering edge cases with missing data
```

### Refactoring code

```bash
refactor: Extract email validation into reusable service

Email validation logic was duplicated across registration,
profile updates, and invitation flows. Consolidating into
a single service improves maintainability and consistency.

- Create EmailValidationService with comprehensive rules
- Replace inline validation in UserController
- Update ProfileController to use new service
- Add unit tests for all validation scenarios
```

### Configuration changes

```bash
config: Update database connection pool settings

Increased concurrent users were causing connection timeouts.
Tuning pool size and timeout values based on load testing results.

- Increase max pool size from 10 to 25
- Reduce connection timeout from 30s to 10s
- Add connection health check interval
- Update monitoring alerts for new thresholds
```

## 🚫 What not to commit atomically

Avoid mixing these concerns in single commits:

### Mixed changes

❌ **Don't mix**:

- Feature implementation + unrelated bug fix
- Code changes + dependency updates
- Multiple unrelated refactors
- Feature code + formatting changes

✅ **Do separate**:

- One commit for the feature
- Separate commit for the bug fix
- Dedicated commit for dependency updates

### Work-in-progress

❌ **Avoid**:

- "WIP: half-implemented feature"
- "Debugging commit"
- "Temporary changes"

✅ **Instead**:

- Use branches for work-in-progress
- Squash/rebase before merging to main
- Keep main history clean and atomic

## 🔄 Integration with development workflow

### With feature branches

```bash
# Create feature branch
git checkout -b feature/user-authentication

# Make atomic commits on the branch
git commit -m "Add user registration endpoint"
git commit -m "Implement password hashing service"
git commit -m "Add login session management"

# Before merging, ensure each commit is atomic
git rebase -i main

# Merge to main with clean, atomic history
git checkout main
git merge feature/user-authentication
```

### With code review

Atomic commits make code review much more effective:

- Each commit can be reviewed independently
- Reviewers can understand the progression of changes
- Easy to request changes to specific commits
- Clear approval process for each logical change

## 📚 Why Chris Beams style?

### Pros

- **Natural English** - Reads like proper sentences
- **Rich context** - Body explains the reasoning behind changes
- **Human readable** - Easy to understand in `git log`
- **AI friendly** - Clear structure that AI can parse and understand
- **Flexible** - Works for any type of project or team

### Cons addressed

- **No built-in automation** - We prioritize human readability over tooling
- **Style drift** - This document establishes consistent standards
- **Less structured** - The imperative + body format provides sufficient structure

## 🎯 Success metrics

You're writing good atomic commits when:

### Readability

- ✅ Each commit tells a complete story
- ✅ The history reads like a logical progression
- ✅ New team members can understand the evolution
- ✅ `git log --oneline` provides a clear project timeline

### Functionality

- ✅ Every commit passes all tests
- ✅ Each commit represents a working state
- ✅ Individual commits can be deployed independently
- ✅ Easy to bisect and identify when issues were introduced

### Maintainability

- ✅ Can revert specific features without affecting others
- ✅ Easy to cherry-pick commits to other branches
- ✅ Clear understanding of why each change was made
- ✅ Simple to modify or extend existing functionality

## 🔧 Tools and tips

### Git aliases

Add these to your `.gitconfig`:

```ini
[alias]
    # Better commit message editing
    c = commit --verbose

    # Amend previous commit
    amend = commit --amend --no-edit

    # Interactive rebase for squashing
    squash = rebase -i HEAD~

    # Beautiful log display
    lg = log --oneline --graph --decorate
```

### IDE integration

Configure your editor to:

- Show git blame inline
- Highlight lines over 72 characters in commit messages
- Provide commit message templates
- Run tests automatically before commits

## 💡 Remember

> "Make each commit a gift to your future self"

When you write atomic commits with clear messages, you're not just documenting code changes - you're creating a knowledge base that helps everyone understand how and why your system evolved.

Every commit should be something you'd be proud to show in a code review, and something that would help you debug an issue six months from now.

---

_The best commits are atomic, clear, and tell the story of your code's evolution._

## 🤔 Atomic commit Q&A

### Q: How do I know if multiple changes in one file represent one atomic commit or multiple?

**A: Apply the logical coherence test**

Even when multiple changes are in the same file, ask yourself:

**✅ One atomic commit when**:
- All changes serve the same logical purpose
- All changes work together toward a single goal
- You would describe the changes as one enhancement/fix
- Reverting would remove one complete functional improvement

**❌ Multiple atomic commits when**:
- Changes serve different purposes or solve different problems
- Changes could be developed/tested independently
- You would describe them as separate improvements
- Reverting one part wouldn't affect the value of the other parts

**Example - One atomic commit**:
```bash
File: docs/patterns/git/atomic-git-commits.md
Changes:
- Add "Fix formatting first" step
- Add "Identify multiple changes" step
- Add troubleshooting section for pre-commit hooks
- Update verification checklist

Assessment: ✅ One atomic commit
Reason: All changes serve one goal - "enhance atomic commit process to prevent violations"
```

**Example - Multiple atomic commits**:
```bash
File: src/utils.js
Changes:
- Fix bug in validateEmail function
- Add new formatPhoneNumber function
- Refactor existing parseDate function

Assessment: ❌ Should be 3 separate commits
Reason: Bug fix, new feature, and refactoring are independent logical changes
```

### Q: What if my atomic commit touches many files?

**A: File count doesn't determine atomicity - logical coherence does**

**✅ Perfectly atomic examples with many files**:
- Renaming a function across 15 files (one logical change: function rename)
- Adding a new feature that requires component + styles + tests + docs (one logical change: complete feature)
- Fixing a bug that requires changes in model + controller + view + tests (one logical change: bug fix)

**The test**: Can you revert this commit and remove exactly one complete logical improvement? If yes, it's atomic regardless of file count.

### Q: How do I verify a commit is atomic after making it?

**A: Use the atomic commit verification checklist**

1. **✅ One Complete Logical Change**: Does this commit represent one coherent improvement?
2. **✅ Can Be Reverted Independently**: Can I revert this without breaking other functionality?
3. **✅ Single Responsibility**: Does it have one clear purpose and scope?
4. **✅ Cohesive Changes**: Do all modifications serve the same logical purpose?
5. **✅ Complete Working State**: Is everything fully functional after this commit?
6. **✅ Clear Single Story**: Can readers understand one complete improvement from this commit?

**Red flags that suggest non-atomic commits**:
- Commit message lists multiple unrelated changes
- Reverting would remove functionality that could stay
- Changes solve different problems or add unrelated features
- You struggle to write a coherent commit message

### Q: What about "cleanup" or "formatting" commits mixed with features?

**A: Keep them separate - always**

**❌ Wrong**:
```bash
git commit -m "Add user validation feature and fix formatting issues"
# Mixes: new functionality + maintenance
```

**✅ Right**:
```bash
# First: Clean up formatting
git commit -m "style: Fix formatting issues across user components"

# Then: Add feature
git commit -m "feat: Add user validation with email and phone checks"
```

**Why this matters**: You want to be able to revert the feature without losing formatting fixes, or vice versa.

## Appendix: Chris Beams style

See [Chris Beams commit style](../../../../.claude/skills/commit/references/chris-beams-commit-style.md) — the 7 rules and example template that our commit format is built on.
