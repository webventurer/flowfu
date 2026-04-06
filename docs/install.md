# Install

```bash
npx github:webventurer/flowfu
```

This copies skills, commands, hooks, and tools into your project's `.claude/` directory and merges hook config into your existing `settings.json`.

## Requirements

### Claude Code

Install the [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI:

```bash
npm install -g @anthropic-ai/claude-code
```

### Linear MCP server

The `/linear` commands need Linear's [official MCP server](https://linear.app/docs/mcp). There are two ways to connect — **OAuth** (simplest) or **API key** (needed for multiple workspaces).

Copy `.mcp.json.example` to `.mcp.json` and choose your approach:

#### OAuth (single workspace)

Uses browser-based login — no keys to manage:

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
    }
  }
}
```

On first use, a browser window opens to authenticate. The token is cached locally.

#### API key (multiple workspaces)

When you need separate connections to different Linear workspaces — for example, a personal workspace and a team workspace — use API keys via the `Authorization` header:

```json
{
  "mcpServers": {
    "linear-personal": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.linear.app/mcp",
        "--header",
        "Authorization:Bearer ${LINEAR_PERSONAL_API_KEY}"
      ],
      "env": {
        "LINEAR_PERSONAL_API_KEY": "${LINEAR_PERSONAL_API_KEY}"
      }
    },
    "linear-team": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.linear.app/mcp",
        "--header",
        "Authorization:Bearer ${LINEAR_TEAM_API_KEY}"
      ],
      "env": {
        "LINEAR_TEAM_API_KEY": "${LINEAR_TEAM_API_KEY}"
      }
    }
  }
}
```

Each entry points to the same `mcp.linear.app/mcp` endpoint but authenticates with a different key. Add the keys to your `~/.env`:

```
LINEAR_PERSONAL_API_KEY=lin_api_...
LINEAR_TEAM_API_KEY=lin_api_...
```

Get your API keys at [linear.app/settings/api](https://linear.app/settings/api) — one per workspace.

#### Verify the connection

```
/linear:check
```

This confirms that each configured Linear server responds and shows which workspace it's connected to.

### GitHub CLI

Install the [GitHub CLI](https://cli.github.com/) (`gh`) for PR operations:

```bash
brew install gh                # macOS
# or: https://cli.github.com/ for other platforms
```

Then authenticate:

```bash
gh auth login
```

## Python tools

The cross-model feedback loop in `/linear:plan-work` uses a Python script to send drafts to ChatGPT via [OpenRouter](https://openrouter.ai/). Dependencies are managed inline with [uv](https://docs.astral.sh/uv/) — no venv or `pip install` needed.

```bash
brew install uv                # macOS
# or: curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add your OpenRouter API key to `~/.env`:

```
OPEN_ROUTER_API_KEY=sk-or-...
```

Get your key at [openrouter.ai/keys](https://openrouter.ai/keys).

## What gets installed

```bash
.claude/
├── skills/commit/           # skill + workflow + reference docs
├── commands/linear/         # 5 commands + reference docs
├── hooks/                   # commit wrapper + bare-commit blocker
└── docs/                    # supporting patterns and concepts
```

The install script merges hook config into your existing `.claude/settings.json` — it won't overwrite your other settings.

## Known limitations

### No versioning

There's no version number, changelog, or upgrade path. When you install, you get the current state of the repo. If you install again later, files are overwritten with whatever's current — no diff, no migration notes.

**What this means:** you won't know what changed between installs. If the repo goes private or gets renamed, your project still works (the files are local), but updates stop with no warning.

**Workaround:** pin to a specific commit if stability matters:

```bash
npx github:webventurer/flowfu#<commit-sha>
```

### Hook scripts require bash

The commit safety hook (`block_bare_git_commit.sh`) is a shell script. If it fails — wrong shell, missing permissions, Windows without WSL — the enforcement disappears silently. The agent will happily use bare `git commit` without the four-pass methodology.

**Check it's working:** if you can run `.claude/hooks/do_commit.sh --help` without errors, you're fine. If not, check that the scripts are executable (`chmod +x .claude/hooks/*.sh`).

### Settings merge strategy

When you already have a `.claude/settings.json`, the install script asks before merging. If you say yes, it uses a deep merge:

- **Objects** are merged recursively — your keys are preserved, flowfu's keys are added alongside
- **Arrays** (like hook lists) are appended with deduplication — if a hook already exists, it's skipped
- **Scalar values** — flowfu's value wins if both sides set the same key

The merge is additive — it never removes your existing settings. But if you have a hook on the same event with different behaviour, both will run. Review `.claude/settings.json` after install if you have existing hooks.
