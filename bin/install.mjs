#!/usr/bin/env node

import {
  chmodSync,
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcRoot = join(__dirname, "..");
const destRoot = process.cwd();

const HOOK_CONFIG = {
  hooks: {
    UserPromptSubmit: [
      {
        hooks: [
          {
            type: "command",
            command:
              "$CLAUDE_PROJECT_DIR/.claude/hooks/userpromptsubmit/inject_design_principles.sh",
          },
        ],
      },
    ],
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
  },
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

const DIRS = [
  ".claude/skills/commit",
  ".claude/skills/craft",
  ".claude/commands/linear",
  ".claude/hooks",
  ".claude/docs/patterns/git",
  ".claude/docs/concepts",
  ".claude/docs/principles",
  "tools",
];

const HOOKS = [
  ".claude/hooks/do_commit.sh",
  ".claude/hooks/pretooluse/block_bare_git_commit.sh",
  ".claude/hooks/userpromptsubmit/inject_design_principles.sh",
];

function resolveTypeMismatch(dest) {
  const src = join(srcRoot, dest);
  const full = join(destRoot, dest);
  if (!existsSync(full)) return;
  const srcIsDir = lstatSync(src).isDirectory();
  const destIsDir = lstatSync(full).isDirectory();
  if (srcIsDir !== destIsDir) rmSync(full, { recursive: true, force: true });
}

function copyDir(dir) {
  const src = join(srcRoot, dir);
  if (!existsSync(src)) return;
  resolveTypeMismatch(dir);
  mkdirSync(join(destRoot, dir), { recursive: true });
  cpSync(src, join(destRoot, dir), { recursive: true });
}

function makeExecutable(hook) {
  const path = join(destRoot, hook);
  if (existsSync(path)) chmodSync(path, 0o755);
}

function copyFiles() {
  DIRS.forEach(copyDir);
  HOOKS.forEach(makeExecutable);
}

const EXAMPLE_FILES = [".mcp.json.example"];

function copyExampleFiles() {
  for (const file of EXAMPLE_FILES) {
    const src = join(srcRoot, file);
    if (existsSync(src)) cpSync(src, join(destRoot, file));
  }
}

const LINEAR_OAUTH = {
  linear: {
    command: "npx",
    args: ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
  },
};

const LINEAR_API_KEY = {
  "linear-org1": {
    command: "npx",
    args: [
      "-y",
      "mcp-remote",
      "https://mcp.linear.app/mcp",
      "--header",
      "Authorization:Bearer ${LINEAR_ORG1_API_KEY}",
    ],
    env: { LINEAR_ORG1_API_KEY: "${LINEAR_ORG1_API_KEY}" },
  },
  "linear-org2": {
    command: "npx",
    args: [
      "-y",
      "mcp-remote",
      "https://mcp.linear.app/mcp",
      "--header",
      "Authorization:Bearer ${LINEAR_ORG2_API_KEY}",
    ],
    env: { LINEAR_ORG2_API_KEY: "${LINEAR_ORG2_API_KEY}" },
  },
};

function isApiKey(method) {
  return method === "api" || method === "apikey";
}

function readMcpConfig(path) {
  if (!existsSync(path)) return { mcpServers: {} };
  const config = JSON.parse(readFileSync(path, "utf8"));
  config.mcpServers = config.mcpServers || {};
  return config;
}

function writeMcpConfig(path, config) {
  writeFileSync(path, `${JSON.stringify(config, null, 2)}\n`);
}

async function configureMcp() {
  const method = await ask(
    "Linear: OAuth (single org) or API key (multiple orgs)? (oauth/api) ",
  );
  const servers = isApiKey(method) ? LINEAR_API_KEY : LINEAR_OAUTH;
  const mcpPath = join(destRoot, ".mcp.json");
  const config = readMcpConfig(mcpPath);
  deepMerge(config.mcpServers, servers);
  writeMcpConfig(mcpPath, config);
  console.log(
    isApiKey(method)
      ? "Configured Linear MCP (API key — add LINEAR_ORG1_API_KEY and LINEAR_ORG2_API_KEY to ~/.env)"
      : "Configured Linear MCP (OAuth — browser login on first use)",
  );
}

function mergeSettings() {
  const settingsPath = join(destRoot, ".claude/settings.local.json");
  mkdirSync(dirname(settingsPath), { recursive: true });

  let settings = {};
  if (existsSync(settingsPath)) {
    settings = JSON.parse(readFileSync(settingsPath, "utf8"));
  }

  deepMerge(settings, HOOK_CONFIG);
  writeFileSync(settingsPath, `${JSON.stringify(settings, null, 2)}\n`);
}

async function main() {
  console.log("\nstride — All the speed. None of the mess.\n");

  // Copy skill and command files
  copyFiles();
  copyExampleFiles();
  console.log("Copied:");
  console.log("  .claude/skills/commit/     (4-pass atomic commit skill)");
  console.log("  .claude/commands/linear/   (Linear workflow commands)");
  console.log("  .claude/hooks/             (commit hook scripts)");
  console.log("  .claude/docs/              (principles, patterns, concepts)");
  console.log("  tools/                     (cross-model feedback script)");
  console.log("  .mcp.json.example          (Linear MCP server reference)");

  // Configure Linear MCP
  await configureMcp();

  // Merge settings into local (gitignored) settings
  const settingsPath = join(destRoot, ".claude/settings.local.json");
  const settingsExist = existsSync(settingsPath);

  if (settingsExist) {
    const answer = await ask(
      "\nMerge hook config into existing .claude/settings.local.json? (y/n) ",
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
      ? "Merged hooks into .claude/settings.local.json"
      : "Created .claude/settings.local.json with hook config",
  );

  console.log("\nDone. Available skills:");
  console.log("  /commit              — 4-pass atomic git commits");
  console.log("  /linear:check        — verify MCP connections");
  console.log("  /linear:start        — implement a Linear issue");
  console.log("  /linear:plan-work    — create a Linear issue");
  console.log("  /linear:fix          — address PR review feedback");
  console.log("  /linear:finish       — merge and close");
  console.log("  /linear:next-steps   — review priorities\n");
}

main();
