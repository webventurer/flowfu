#!/usr/bin/env node

import { existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const destRoot = process.cwd();

if (existsSync(join(destRoot, "bin/install.mjs"))) {
  console.error("Cannot uninstall from the flowfu repo itself.");
  process.exit(1);
}

const DIRS = [
  ".claude/skills/commit",
  ".claude/skills/craft",
  ".claude/commands/linear",
  ".claude/hooks",
  ".claude/docs/patterns/git",
  ".claude/docs/concepts",
  "tools",
];

const EXAMPLE_FILES = [".mcp.json.example"];

const HOOK_MATCHER = "block_bare_git_commit.sh";

function removeDir(dir) {
  const full = join(destRoot, dir);
  if (existsSync(full)) rmSync(full, { recursive: true, force: true });
}

function removeFile(file) {
  const full = join(destRoot, file);
  if (existsSync(full)) rmSync(full);
}

function removeHookConfig() {
  const settingsPath = join(destRoot, ".claude/settings.json");
  if (!existsSync(settingsPath)) return;

  const settings = JSON.parse(readFileSync(settingsPath, "utf8"));
  const hooks = settings.PreToolUse;
  if (!Array.isArray(hooks)) return;

  settings.PreToolUse = hooks.filter(
    (h) => !JSON.stringify(h).includes(HOOK_MATCHER),
  );
  if (settings.PreToolUse.length === 0) delete settings.PreToolUse;

  writeFileSync(settingsPath, `${JSON.stringify(settings, null, 2)}\n`);
}

function main() {
  console.log("\nflowfu — uninstalling\n");

  DIRS.forEach(removeDir);
  EXAMPLE_FILES.forEach(removeFile);
  removeHookConfig();

  console.log("Removed:");
  console.log("  .claude/skills/commit/     (4-pass atomic commit skill)");
  console.log("  .claude/skills/craft/      (CRAFT prompt skill)");
  console.log("  .claude/commands/linear/   (Linear workflow commands)");
  console.log("  .claude/hooks/             (commit hook scripts)");
  console.log("  .claude/docs/              (supporting documentation)");
  console.log("  tools/                     (cross-model feedback script)");
  console.log("  .mcp.json.example          (Linear MCP server reference)");
  console.log("  PreToolUse hook            (from .claude/settings.json)");
  console.log("\nNote: .mcp.json was not modified — remove Linear servers manually if needed.");
  console.log("Done.\n");
}

main();
