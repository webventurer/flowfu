import { strictEqual } from "node:assert";
import { execSync } from "node:child_process";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { after, describe, it } from "node:test";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const strideRoot = join(__dirname, "..");
const fixtureRoot = join("/tmp", `stride-uninstall-${process.pid}`);

function seedInstalled() {
  rmSync(fixtureRoot, { recursive: true, force: true });
  mkdirSync(fixtureRoot, { recursive: true });
  execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
    cwd: fixtureRoot,
    input: "none\nn\n",
    stdio: ["pipe", "pipe", "pipe"],
  });
}

function writeSentinel(relPath, content) {
  const full = join(fixtureRoot, relPath);
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, content);
  return full;
}

function writeSentinelSymlink(relPath, target) {
  const full = join(fixtureRoot, relPath);
  mkdirSync(dirname(full), { recursive: true });
  symlinkSync(target, full);
  return full;
}

function runUninstall() {
  execSync(`node ${join(strideRoot, "bin/uninstall.mjs")}`, {
    cwd: fixtureRoot,
    stdio: ["pipe", "pipe", "pipe"],
  });
}

describe("uninstall footprint", () => {
  after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

  it("removes stride's own hook files", () => {
    seedInstalled();
    runUninstall();

    const strideHook = join(
      fixtureRoot,
      ".claude/hooks/userpromptsubmit/inject_design_principles.sh",
    );
    strictEqual(existsSync(strideHook), false);
  });

  it("preserves consumer files co-located in stride's hook directory", () => {
    seedInstalled();
    const consumer = writeSentinel(
      ".claude/hooks/userpromptsubmit/consumer_owned.sh",
      "consumer hook — must survive",
    );

    runUninstall();

    strictEqual(existsSync(consumer), true);
    strictEqual(readFileSync(consumer, "utf8"), "consumer hook — must survive");
  });

  it("preserves symlinks from other tools (e.g. codefu)", () => {
    seedInstalled();
    const symlinkPath = writeSentinelSymlink(
      ".claude/hooks/userpromptsubmit/codefu_hook.sh",
      "/nonexistent/codefu/source.sh",
    );

    runUninstall();

    strictEqual(lstatSync(symlinkPath).isSymbolicLink(), true);
  });

  it("keeps the shared directory when non-stride files remain", () => {
    seedInstalled();
    writeSentinel(
      ".claude/hooks/userpromptsubmit/consumer_owned.sh",
      "consumer hook",
    );

    runUninstall();

    strictEqual(
      existsSync(join(fixtureRoot, ".claude/hooks/userpromptsubmit")),
      true,
    );
  });

  it("prunes empty directories after removing stride files", () => {
    seedInstalled();

    runUninstall();

    strictEqual(
      existsSync(join(fixtureRoot, ".claude/skills/commit")),
      false,
      "empty stride-owned dir should be pruned",
    );
  });

  it("is idempotent — second run is a no-op", () => {
    seedInstalled();
    runUninstall();

    runUninstall();

    strictEqual(existsSync(join(fixtureRoot, ".claude/skills/commit")), false);
  });
});
