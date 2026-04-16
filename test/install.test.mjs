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

describe("deepMerge", () => {
  it("merges into empty settings", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());

    deepStrictEqual(Object.keys(settings), ["hooks"]);
    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });

  it("preserves existing user hooks", () => {
    const settings = {
      hooks: {
        UserPromptSubmit: [
          { hooks: [{ type: "command", command: "my_custom.sh" }] },
        ],
      },
    };
    deepMerge(settings, cloneConfig());

    strictEqual(settings.hooks.UserPromptSubmit.length, 2);
    strictEqual(
      settings.hooks.UserPromptSubmit[0].hooks[0].command,
      "my_custom.sh",
    );
  });

  it("preserves existing non-hook settings", () => {
    const settings = {
      includeCoAuthoredBy: false,
      permissions: { deny: ["Bash(rm -rf :*)"] },
    };
    deepMerge(settings, cloneConfig());

    strictEqual(settings.includeCoAuthoredBy, false);
    deepStrictEqual(settings.permissions.deny, ["Bash(rm -rf :*)"]);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });
});

describe("dedupeHooks", () => {
  it("does not duplicate on re-install", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());

    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });

  it("does not duplicate after three installs", () => {
    const settings = {};
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());
    deepMerge(settings, cloneConfig());

    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(settings.hooks.PreToolUse.length, 1);
  });
});
