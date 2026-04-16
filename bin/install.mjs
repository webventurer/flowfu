#!/usr/bin/env node

import {
  chmodSync,
  cpSync,
  existsSync,
  lstatSync,
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
  ".claude/stride/docs/patterns/git",
  ".claude/stride/docs/concepts",
  ".claude/stride/docs/principles",
  ".claude/tools",
];

const HOOKS = [
  ".claude/hooks/do_commit.sh",
  ".claude/hooks/pretooluse/block_bare_git_commit.sh",
  ".claude/hooks/userpromptsubmit/inject_design_principles.sh",
];

function abortOnTypeMismatch(dest) {
  const src = join(srcRoot, dest);
  const full = join(destRoot, dest);
  if (!existsSync(full)) return;
  if (lstatSync(src).isDirectory() === lstatSync(full).isDirectory()) return;
  console.error(
    `\nERROR: ${dest} has different type in source vs target.\n` +
      `Source: ${src}\nTarget: ${full}\n` +
      `Stride will not overwrite this — resolve manually and re-run.`,
  );
  process.exit(1);
}

function copyDir(dir) {
  const src = join(srcRoot, dir);
  if (!existsSync(src)) return;
  abortOnTypeMismatch(dir);
  assertUnderClaudeDir(dir);
  mkdirSync(join(destRoot, dir), { recursive: true });
  cpSync(src, join(destRoot, dir), { recursive: true });
}

function assertUnderClaudeDir(dir) {
  if (dir.startsWith(".claude/") || dir === ".claude") return;
  console.error(
    `\nERROR: refusing to write outside .claude/: ${dir}\n` +
      `Stride's install footprint is .claude/ only. This is a bug in DIRS.`,
  );
  process.exit(1);
}

function makeExecutable(hook) {
  const path = join(destRoot, hook);
  if (existsSync(path)) chmodSync(path, 0o755);
}

function copyFiles() {
  DIRS.forEach(copyDir);
  HOOKS.forEach(makeExecutable);
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

function hasLinearMcp(mcpPath) {
  if (!existsSync(mcpPath)) return false;
  const config = JSON.parse(readFileSync(mcpPath, "utf8"));
  const servers = Object.keys(config.mcpServers || {});
  return servers.some((s) => s.toLowerCase().includes("linear"));
}

async function configureMcp() {
  const mcpPath = join(destRoot, ".mcp.json");
  if (hasLinearMcp(mcpPath)) {
    console.log("Linear MCP already configured in .mcp.json — skipping");
    return;
  }
  const method = await ask(
    "Linear MCP: oauth (single org), api (multiple orgs), or none? [none] ",
  );
  if (!method || method === "none" || method === "n" || method === "skip") {
    console.log("Skipped Linear MCP setup");
    return;
  }
  const servers = isApiKey(method) ? LINEAR_API_KEY : LINEAR_OAUTH;
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

function installFiles() {
  copyFiles();
  logCopiedFiles();
}

function logCopiedFiles() {
  console.log("Copied to .claude/:");
  console.log("  skills/commit/   (4-pass atomic commit skill)");
  console.log("  commands/linear/ (Linear workflow commands)");
  console.log("  hooks/           (commit hook scripts)");
  console.log("  stride/docs/     (principles, patterns, concepts)");
  console.log("  tools/           (cross-model feedback script)");
}

async function confirmSettingsMerge() {
  const answer = await ask(
    "\nMerge hook config into existing .claude/settings.local.json? [Y/n] ",
  );
  return !answer || answer === "y" || answer === "yes";
}

async function installHookConfig() {
  const existed = existsSync(join(destRoot, ".claude/settings.local.json"));
  if (existed && !(await confirmSettingsMerge())) {
    console.log(
      "Skipped settings merge. You can add the hooks manually — see README.",
    );
    return false;
  }
  mergeSettings();
  console.log(
    existed
      ? "Merged hooks into .claude/settings.local.json"
      : "Created .claude/settings.local.json with hook config",
  );
  return true;
}

function logAvailableSkills() {
  console.log("\nDone. Available skills:");
  console.log("  /commit              — 4-pass atomic git commits");
  console.log("  /linear:check        — verify MCP connections");
  console.log("  /linear:start        — implement a Linear issue");
  console.log("  /linear:plan-work    — create a Linear issue");
  console.log("  /linear:fix          — address PR review feedback");
  console.log("  /linear:finish       — merge and close");
  console.log("  /linear:next-steps   — review priorities\n");
}

async function main() {
  console.log("\nstride — All the speed. None of the mess.\n");
  installFiles();
  await configureMcp();
  if (!(await installHookConfig())) return;
  logAvailableSkills();
}

main();
