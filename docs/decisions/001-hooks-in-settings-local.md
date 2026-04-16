# 001 — Install hooks into settings.local.json, not settings.json

**Date:** 2026-04-16
**Status:** Accepted

## Context

When stride (or any tool) installs hooks into a target repo, it needs to write hook configuration somewhere in `.claude/`. There are two options:

- **`settings.json`** — committed to version control, shared by the team
- **`settings.local.json`** — gitignored, local to the developer's machine

Previously, the installer merged hook config into `settings.json`.

## Decision

**Install hook config into `settings.local.json`.**

This applies to stride, codefu, and any future tool that installs hooks into a target repo.

## Why

`settings.json` belongs to the target repo. Writing into it means:

- **Git noise** — every install/uninstall creates a diff in committed files
- **Merge conflicts** — if the target repo updates its own hooks, installs from the toolchain collide
- **Coupling** — the target repo's committed settings become dependent on which tools each developer has installed

`settings.local.json` is gitignored — it's the developer's machine-local layer. Installing there means:

- No changes to version-controlled files
- Each developer can install/uninstall independently
- The target repo's committed hooks remain untouched

Claude Code **concatenates and deduplicates** hook arrays across `settings.json` and `settings.local.json`, so hooks from both files run together. There is no clobbering.

## Consequences

- The install script writes to `.claude/settings.local.json` instead of `.claude/settings.json`
- The uninstall script strips hooks from `.claude/settings.local.json` instead of `.claude/settings.json`
- Target repos that previously had stride hooks in `settings.json` should move them to `settings.local.json` (or re-run the installer)
