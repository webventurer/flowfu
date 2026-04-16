import { deepStrictEqual, strictEqual } from "node:assert";
import { describe, it } from "node:test";

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

const HOOK_MATCHERS = [
  "block_bare_git_commit.sh",
  "inject_design_principles.sh",
];

function isStrideHook(entry) {
  return HOOK_MATCHERS.some((m) => JSON.stringify(entry).includes(m));
}

function removeHooks(settings) {
  if (!settings.hooks) return settings;
  for (const event of ["UserPromptSubmit", "PreToolUse", "PostToolUse"]) {
    const hooks = settings.hooks[event];
    if (!Array.isArray(hooks)) continue;
    settings.hooks[event] = hooks.filter((h) => !isStrideHook(h));
    if (settings.hooks[event].length === 0) delete settings.hooks[event];
  }
  return settings;
}

const STRIDE_HOOKS = {
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

function cloneConfig() {
  return JSON.parse(JSON.stringify(STRIDE_HOOKS));
}

describe("install → uninstall round-trip", () => {
  it("fresh install then uninstall leaves empty hooks", () => {
    const settings = {};

    deepMerge(settings, cloneConfig());
    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);

    removeHooks(settings);
    strictEqual(settings.hooks.UserPromptSubmit, undefined);
    strictEqual(settings.hooks.PreToolUse, undefined);
  });

  it("install with existing user hooks then uninstall preserves user hooks", () => {
    const userHook = { hooks: [{ type: "command", command: "my_custom.sh" }] };
    const settings = {
      includeCoAuthoredBy: false,
      hooks: {
        UserPromptSubmit: [JSON.parse(JSON.stringify(userHook))],
        PostToolUse: [],
      },
      permissions: { deny: ["Bash(rm -rf :*)"] },
    };

    deepMerge(settings, cloneConfig());
    strictEqual(settings.hooks.UserPromptSubmit.length, 2);
    strictEqual(settings.hooks.PreToolUse.length, 1);
    strictEqual(settings.includeCoAuthoredBy, false);
    deepStrictEqual(settings.permissions.deny, ["Bash(rm -rf :*)"]);

    removeHooks(settings);
    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(
      settings.hooks.UserPromptSubmit[0].hooks[0].command,
      "my_custom.sh",
    );
    strictEqual(settings.hooks.PreToolUse, undefined);
    strictEqual(settings.includeCoAuthoredBy, false);
  });

  it("re-install then uninstall still cleans up correctly", () => {
    const settings = {};

    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());
    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);

    removeHooks(settings);
    strictEqual(settings.hooks.UserPromptSubmit, undefined);
    strictEqual(settings.hooks.PreToolUse, undefined);
  });
});
