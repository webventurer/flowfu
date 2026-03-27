#!/usr/bin/env node

import {
  chmodSync,
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcRoot = join(__dirname, "..");
const destRoot = process.cwd();

const HOOK_CONFIG = {
  PreToolUse: [
    {
      matcher: "Bash",
      hooks: [
        {
          type: "command",
          command:
            "$CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse/block_bare_git_commit.sh",
        },
      ],
    },
  ],
};

function ask(question) {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer.trim().toLowerCase());
    });
  });
}

function deepMerge(base, overlay) {
  for (const [key, val] of Object.entries(overlay)) {
    base[key] = mergeValue(base[key], val);
  }
  return base;
}

function mergeValue(existing, val) {
  if (isObject(existing) && isObject(val)) return deepMerge(existing, val);
  if (Array.isArray(existing) && Array.isArray(val))
    return dedupeHooks(existing, val);
  return val;
}

function isObject(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}

function dedupeHooks(existing, incoming) {
  for (const item of incoming) {
    const isDupe = existing.some(
      (e) => JSON.stringify(e) === JSON.stringify(item),
    );
    if (!isDupe) existing.push(item);
  }
  return existing;
}

function copyFiles() {
  const dirs = [
    ".claude/skills/commit",
    ".claude/skills/craft",
    ".claude/commands/linear",
    ".claude/hooks",
    ".claude/docs/patterns/git",
    ".claude/docs/concepts",
  ];

  for (const dir of dirs) {
    const src = join(srcRoot, dir);
    const dest = join(destRoot, dir);
    if (existsSync(src)) {
      mkdirSync(dest, { recursive: true });
      cpSync(src, dest, { recursive: true });
    }
  }

  // Ensure hook scripts are executable
  const hooks = [
    ".claude/hooks/do_commit.sh",
    ".claude/hooks/pretooluse/block_bare_git_commit.sh",
  ];
  for (const hook of hooks) {
    const path = join(destRoot, hook);
    if (existsSync(path)) chmodSync(path, 0o755);
  }
}

function mergeSettings() {
  const settingsPath = join(destRoot, ".claude/settings.json");
  mkdirSync(dirname(settingsPath), { recursive: true });

  let settings = {};
  if (existsSync(settingsPath)) {
    settings = JSON.parse(readFileSync(settingsPath, "utf8"));
  }

  deepMerge(settings, HOOK_CONFIG);
  writeFileSync(settingsPath, `${JSON.stringify(settings, null, 2)}\n`);
}

async function main() {
  console.log("\n@codefu/core — atomic commits + Linear workflow\n");

  // Copy skill and command files
  copyFiles();
  console.log("Copied:");
  console.log("  .claude/skills/commit/     (4-pass atomic commit skill)");
  console.log("  .claude/commands/linear/   (Linear workflow commands)");
  console.log("  .claude/hooks/             (commit hook scripts)");
  console.log("  .claude/docs/              (supporting documentation)");

  // Merge settings
  const settingsPath = join(destRoot, ".claude/settings.json");
  const settingsExist = existsSync(settingsPath);

  if (settingsExist) {
    const answer = await ask(
      "\nMerge hook config into existing .claude/settings.json? (y/n) ",
    );
    if (answer !== "y" && answer !== "yes") {
      console.log(
        "Skipped settings merge. You can add the hooks manually — see README.",
      );
      return;
    }
  }

  mergeSettings();
  console.log(
    settingsExist
      ? "Merged hooks into .claude/settings.json"
      : "Created .claude/settings.json with hook config",
  );

  console.log("\nDone. Available skills:");
  console.log("  /commit              — 4-pass atomic git commits");
  console.log("  /linear:start        — implement a Linear issue");
  console.log("  /linear:plan-work    — create a Linear issue");
  console.log("  /linear:fix          — address PR review feedback");
  console.log("  /linear:finish       — merge and close");
  console.log("  /linear:next-steps   — review priorities\n");
}

main();
