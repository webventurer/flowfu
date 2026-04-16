#!/usr/bin/env node

import {
  existsSync,
  lstatSync,
  readdirSync,
  readFileSync,
  rmdirSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcRoot = join(__dirname, "..");
const destRoot = process.cwd();

if (existsSync(join(destRoot, "bin/install.mjs"))) {
  console.error("Cannot uninstall from the stride repo itself.");
  process.exit(1);
}

const DIRS = [
  ".claude/skills/commit",
  ".claude/skills/craft",
  ".claude/commands/linear",
  ".claude/hooks",
  ".claude/stride/docs/patterns/git",
  ".claude/stride/docs/concepts",
  ".claude/stride/docs/principles",
  ".claude/tools",
];

const HOOK_MATCHERS = [
  "block_bare_git_commit.sh",
  "inject_design_principles.sh",
];

function walkFiles(root, base = root) {
  const paths = [];
  for (const entry of readdirSync(root)) {
    const full = join(root, entry);
    const stat = lstatSync(full);
    if (stat.isSymbolicLink()) continue;
    if (stat.isDirectory()) paths.push(...walkFiles(full, base));
    else paths.push(relative(base, full));
  }
  return paths;
}

function removeStrideFiles(dir) {
  const srcDir = join(srcRoot, dir);
  const destDir = join(destRoot, dir);
  if (!existsSync(srcDir) || !existsSync(destDir)) return;
  for (const rel of walkFiles(srcDir)) {
    const target = join(destDir, rel);
    if (existsSync(target)) unlinkSync(target);
  }
  pruneEmptyDirs(destDir);
}

function pruneEmptyDirs(dir) {
  if (!existsSync(dir)) return;
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (lstatSync(full).isDirectory()) pruneEmptyDirs(full);
  }
  if (readdirSync(dir).length === 0) rmdirSync(dir);
}

function isStrideHook(entry) {
  return HOOK_MATCHERS.some((m) => JSON.stringify(entry).includes(m));
}

function removeHookConfig() {
  const settingsPath = join(destRoot, ".claude/settings.local.json");
  if (!existsSync(settingsPath)) return;

  const settings = JSON.parse(readFileSync(settingsPath, "utf8"));
  if (!settings.hooks) return;

  for (const event of ["UserPromptSubmit", "PreToolUse", "PostToolUse"]) {
    const hooks = settings.hooks[event];
    if (!Array.isArray(hooks)) continue;
    settings.hooks[event] = hooks.filter((h) => !isStrideHook(h));
    if (settings.hooks[event].length === 0) delete settings.hooks[event];
  }

  writeFileSync(settingsPath, `${JSON.stringify(settings, null, 2)}\n`);
}

function main() {
  console.log("\nstride — uninstalling\n");

  DIRS.forEach(removeStrideFiles);
  removeHookConfig();

  console.log("Removed stride files from .claude/:");
  console.log("  skills/commit/   (4-pass atomic commit skill)");
  console.log("  skills/craft/    (CRAFT prompt skill)");
  console.log("  commands/linear/ (Linear workflow commands)");
  console.log("  hooks/           (commit hook scripts)");
  console.log("  stride/docs/     (principles, patterns, concepts)");
  console.log("  tools/           (cross-model feedback script)");
  console.log("  hooks config     (from settings.local.json)");
  console.log(
    "\nOther files in shared directories (codefu symlinks, your own hooks) left untouched.",
  );
  console.log(
    "Note: .mcp.json was not modified — remove Linear servers manually if needed.",
  );
  console.log("Done.\n");
}

main();
