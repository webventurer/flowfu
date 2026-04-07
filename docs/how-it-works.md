# How it works

flowfu installs as plain markdown files in your project's `.claude/` directory. No runtime dependencies, no build step — Claude Code reads the files and follows the instructions.

## What gets installed

```
your-project/
└── .claude/
    ├── skills/
    │   ├── commit/          # /commit skill
    │   │   ├── SKILL.md     # Principles, coherence test, atomicity rules
    │   │   └── WORKFLOW.md  # Four-pass execution sequence
    │   └── craft/           # /craft skill
    │       └── SKILL.md     # CRAFT prompt framework
    ├── commands/
    │   └── linear/          # /linear:* commands
    │       ├── start.md     # Implement an issue
    │       ├── finish.md    # Merge + mark Done
    │       ├── fix.md       # Address PR feedback
    │       ├── plan-work.md # Create + refine issues
    │       └── next-steps.md# Show priorities
    ├── docs/                # Foundational knowledge
    │   ├── concepts/        # Core ideas (atomicity, SRP)
    │   ├── patterns/        # Reusable approaches (git patterns)
    │   └── principles/      # Guiding rules
    └── hooks/               # Safety enforcement
        └── do_commit.sh     # Commit wrapper
```

## The three layers

### 1. Knowledge (`.claude/docs/`)

Foundational concepts the agent needs to understand *why* things work a certain way. The commit skill references `atomic-git-commits.md` as required reading — without it, the agent would follow rules without understanding the reasoning behind them.

### 2. Skills and commands (`.claude/skills/`, `.claude/commands/`)

Executable instructions the agent follows step by step. Each skill has:

- **SKILL.md** — the principles, decision rules, and reference material
- **WORKFLOW.md** — the exact execution sequence

**Skills** live in `.claude/skills/` and are invoked directly (`/commit`, `/craft`). A skill has its own `SKILL.md` (principles and rules) and `WORKFLOW.md` (execution steps) — it's a self-contained methodology the agent internalises.

**Commands** live in `.claude/commands/` and are namespaced (`/linear:start`, `/linear:finish`). Each command is a single markdown file describing one discrete action. Commands are grouped by integration — all five Linear commands share context but execute independently.

The distinction: a skill teaches the agent *how to think* about a problem (atomic commits, prompt crafting). A command tells the agent *what to do* in a specific situation (start an issue, merge a PR).

### 3. Safety (`.claude/hooks/`)

Hooks that enforce discipline at the tool level:

- Block bare `git commit` — forces use of the `/commit` skill
- Run security checks on file edits
- Validate formatting standards

**Important:** the hooks are shell scripts. If they fail silently (permissions, wrong shell, Windows without WSL), the safety net disappears — the agent will use bare `git commit` without the four-pass methodology. See the [install guide's known limitations](/install#hook-scripts-require-bash) for how to verify they're working.

## The `/commit` four-pass methodology

When you run `/commit`, the agent doesn't just stage and commit. It runs four distinct passes, each with a different cognitive focus:

| Pass | Focus | What it catches |
|:-----|:------|:----------------|
| **Pre-flight** | Formatting, change inventory | Files grouped by session instead of by purpose |
| **Content** | Selective staging, coherence | Hitchhiker files that don't belong to this change |
| **Standards** | Message format, checklists | Missing prefix, "and" in the subject, wrong mood |
| **Review** | Sanity check, verification | Last chance to catch anything before it lands |

The separation matters because of **content focus blindness** — both people and AI consistently miss formatting standards while focused on content logic. Dedicated passes prevent this.

## The `/linear` five-command lifecycle

The six commands map to how work actually moves through a board:

```
/linear:check      →  verify MCP connections
/linear:plan-work  →  create an issue
/linear:next-steps →  see what needs doing
/linear:start      →  branch, implement, PR
/linear:fix        →  address review feedback
/linear:finish     →  merge, clean up, Done
```

Each command knows about Linear statuses, GitHub PRs, and git branches. The agent moves issues through Backlog → To do → Doing → In review → Done automatically as work progresses.

## The cross-model feedback loop

`/linear:plan-work` optionally sends issue drafts to ChatGPT via OpenRouter for a second opinion before creating the issue. Three voices — Claude proposes, ChatGPT challenges, you steer — sharpen the issue through cross-model perspectives.

This requires an OpenRouter API key. See the [install guide](/install) for setup.

## What the install script does

When you run `npx github:webventurer/flowfu`, the script (`bin/install.mjs`) does four things:

1. **Copies files** into your project's `.claude/` directory — skills, commands, hooks, docs, and the `tools/` folder
2. **Sets permissions** — makes hook scripts (`do_commit.sh`, `block_bare_git_commit.sh`) executable
3. **Merges settings** — if you already have a `.claude/settings.json`, it asks before merging. If you say no, nothing is touched. If you don't have one, it creates a minimal config with the commit hook wired up
4. **Prints a summary** — shows what was installed and which commands are available

The merge is additive — it adds flowfu's hooks alongside your existing config using a deep merge with deduplication. It never removes or overwrites your existing settings.

**If something goes wrong:** the script only writes to `.claude/` and `tools/` inside your project. Delete those directories to fully uninstall. There are no global side effects.

## Customising

The "no lock-in" promise means you can change anything. Here's what's safe to edit and what to be careful with:

| What | Safe to edit? | Notes |
|:-----|:--------------|:------|
| Commit prefixes | Yes | Edit `.claude/skills/commit/SKILL.md` — change the prefix table |
| Commit message rules | Yes | Edit `SKILL.md` and `WORKFLOW.md` — your rules, your standards |
| Linear command behaviour | Yes | Edit files in `.claude/commands/linear/` — each command is a standalone markdown file |
| Hook scripts | Yes | Edit or remove scripts in `.claude/hooks/` — update `settings.json` to match |
| Foundational docs | Yes | Edit `.claude/docs/` — these shape the agent's understanding |
| Settings deny list | Yes | Add your own deny rules to `.claude/settings.json` |
| Adding new skills | Yes | Create a new directory under `.claude/skills/` with a `SKILL.md` — Claude Code auto-discovers it |

**Pulling upstream updates:** there's no automatic upgrade path. If you want to pick up changes from flowfu, re-run the install script — it will overwrite files but won't remove your additions. For heavy customisation, fork the repo and maintain your own version.

## Why markdown

Every file is readable, editable, and version-controlled. You can:

- **Read** the full methodology before installing
- **Customise** any rule or workflow to match your team's standards
- **Fork** the skills and evolve them independently
- **Review** changes to the skills in pull requests, just like code

There's no black box. The agent's instructions are your instructions.
