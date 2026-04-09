# Linear MCP setup

> **AI Assistant Note**: Reference this document when setting up Linear integration for a new project.

This guide covers how to connect Claude Code to Linear via the MCP server.

## Quick reference

**Prerequisites**: A Linear workspace and Claude Code with the Linear MCP server configured.

**Commands at a glance** (ordered by workflow):

| Command | What it does |
|:--------|:-------------|
| `/linear:check` | Verify MCP connections — confirm each Linear server responds |
| `/linear:next-steps` | Review priorities, surface PRs needing fix, recommend what to work on next |
| `/linear:plan-work` | Draft and create a Linear issue with optional `--research` and `--craft` flags |
| `/linear:start` | Branch, implement, validate, open PR, and review the diff in the terminal |
| `/linear:fix` | Address GitHub PR review feedback, validate, push, and comment on the PR |
| `/linear:finish` | Squash merge an approved PR, delete branches, mark issue Done |

See [workflow.md](workflow.md) for detailed command docs and typical flow.

## Setting up the Linear MCP server

### 1. Configure the MCP server

Copy `.mcp.json.example` to `.mcp.json` and choose OAuth (single org) or API key (multiple orgs). See the [install guide](/install#linear-mcp-server) for both configurations.

### 2. Verify the connection

Run `/linear:check` to confirm each configured Linear server responds. It calls `list_teams` on each server and reports which workspace it's connected to.

### 3. Install the Linear GitHub integration

Linear's [GitHub integration](https://linear.app/settings/integrations/github) connects PRs to issues automatically. Without it, `/linear:start` creates PRs that Linear doesn't know about — you lose status sync, auto-transitions, and the PR link on the issue.

**Install the GitHub App:**

1. Go to **Linear Settings** → **Integrations** → **GitHub**
2. Click **Connect** and authorize the GitHub App for your organisation
3. Select which repositories Linear can access

**What it enables:**

| Feature | Without integration | With integration |
|:--------|:-------------------|:-----------------|
| PR linked on issue | Manual | Automatic (via branch name) |
| Issue status on PR merge | Manual | Auto-transitions to Done |
| PR status visible in Linear | No | Yes (open, merged, closed) |
| Branch name linking | No | `username/pg-123-feature` links to PG-123 |

The `/linear:start` command already names branches in the format Linear expects (e.g. `mike/pg-205-add-dark-mode`). Once the integration is installed, Linear picks up the link automatically.

## Adapting for your project

The commands resolve the Linear project from a `.linear_project` file in the repo root. If this file does not exist, `/next-steps` and `/plan-work` will ask which project to use and save the selection.

- **Team**: resolved from `.linear_project` (or ask the user on first run)
- **Project**: read from `.linear_project`

---

*Setup once, then let the commands handle the Linear ceremony.*
