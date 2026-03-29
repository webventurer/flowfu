# How it works

codefu installs as plain markdown files in your project's `.claude/` directory. No runtime dependencies, no build step — Claude Code reads the files and follows the instructions.

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

Skills are invoked directly (`/commit`). Commands are namespaced (`/linear:start`, `/linear:finish`).

### 3. Safety (`.claude/hooks/`)

Hooks that enforce discipline at the tool level:

- Block bare `git commit` — forces use of the `/commit` skill
- Run security checks on file edits
- Validate formatting standards

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

The five commands map to how work actually moves through a board:

```
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

## Why markdown

Every file is readable, editable, and version-controlled. You can:

- **Read** the full methodology before installing
- **Customise** any rule or workflow to match your team's standards
- **Fork** the skills and evolve them independently
- **Review** changes to the skills in pull requests, just like code

There's no black box. The agent's instructions are your instructions.
