import { deepStrictEqual, strictEqual } from "node:assert";
import { describe, it } from "node:test";

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

describe("removeHooks", () => {
  it("removes stride UserPromptSubmit hook", () => {
    const settings = {
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
      },
    };
    removeHooks(settings);

    strictEqual(settings.hooks.UserPromptSubmit, undefined);
  });

  it("removes stride PreToolUse hook", () => {
    const settings = {
      hooks: {
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
    removeHooks(settings);

    strictEqual(settings.hooks.PreToolUse, undefined);
  });

  it("preserves user hooks", () => {
    const settings = {
      hooks: {
        UserPromptSubmit: [
          { hooks: [{ type: "command", command: "my_custom.sh" }] },
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
    removeHooks(settings);

    strictEqual(settings.hooks.UserPromptSubmit.length, 1);
    strictEqual(
      settings.hooks.UserPromptSubmit[0].hooks[0].command,
      "my_custom.sh",
    );
    strictEqual(settings.hooks.PreToolUse, undefined);
  });

  it("handles settings with no hooks key", () => {
    const settings = { includeCoAuthoredBy: false };
    removeHooks(settings);

    deepStrictEqual(settings, { includeCoAuthoredBy: false });
  });

  it("handles empty hook arrays", () => {
    const settings = {
      hooks: {
        UserPromptSubmit: [],
        PreToolUse: [],
        PostToolUse: [],
      },
    };
    removeHooks(settings);

    strictEqual(settings.hooks.UserPromptSubmit, undefined);
    strictEqual(settings.hooks.PreToolUse, undefined);
    strictEqual(settings.hooks.PostToolUse, undefined);
  });
});

describe("isStrideHook", () => {
  it("identifies the design principles hook", () => {
    const hook = {
      hooks: [
        { type: "command", command: "path/to/inject_design_principles.sh" },
      ],
    };
    strictEqual(isStrideHook(hook), true);
  });

  it("identifies the git commit blocker hook", () => {
    const hook = {
      matcher: "Bash",
      hooks: [{ type: "command", command: "path/to/block_bare_git_commit.sh" }],
    };
    strictEqual(isStrideHook(hook), true);
  });

  it("does not match user hooks", () => {
    const hook = {
      hooks: [{ type: "command", command: "my_custom_hook.sh" }],
    };
    strictEqual(isStrideHook(hook), false);
  });
});
