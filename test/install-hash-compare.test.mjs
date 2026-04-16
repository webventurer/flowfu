import { match, notStrictEqual, strictEqual } from "node:assert";
import { execSync } from "node:child_process";
import {
  cpSync,
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
const fixtureRoot = join("/tmp", `stride-hash-compare-${process.pid}`);
const SKILL_REL = ".claude/skills/commit";
const SKILL_FILE_REL = `${SKILL_REL}/SKILL.md`;

function resetFixture() {
  rmSync(fixtureRoot, { recursive: true, force: true });
  mkdirSync(fixtureRoot, { recursive: true });
}

function copyFromStride(relPath, destRelPath = relPath) {
  const src = join(strideRoot, relPath);
  const dest = join(fixtureRoot, destRelPath);
  mkdirSync(dirname(dest), { recursive: true });
  cpSync(src, dest, { recursive: true });
}

function readStride(relPath) {
  return readFileSync(join(strideRoot, relPath), "utf8");
}

function readFixture(relPath) {
  return readFileSync(join(fixtureRoot, relPath), "utf8");
}

function writeFixture(relPath, content) {
  const full = join(fixtureRoot, relPath);
  mkdirSync(dirname(full), { recursive: true });
  writeFileSync(full, content);
  return full;
}

function runInstall() {
  return execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
    cwd: fixtureRoot,
    input: "n\nnone\nn\n",
    stdio: ["pipe", "pipe", "pipe"],
  });
}

function runInstallExpectFailure() {
  try {
    execSync(`node ${join(strideRoot, "bin/install.mjs")}`, {
      cwd: fixtureRoot,
      input: "n\nnone\nn\n",
      stdio: ["pipe", "pipe", "pipe"],
    });
    return null;
  } catch (err) {
    return { status: err.status, stderr: err.stderr.toString() };
  }
}

describe("install hash-compare", () => {
  after(() => rmSync(fixtureRoot, { recursive: true, force: true }));

  it("completes silently when target content matches stride's source", () => {
    resetFixture();
    copyFromStride(SKILL_REL);

    runInstall();

    strictEqual(readFixture(SKILL_FILE_REL), readStride(SKILL_FILE_REL));
  });

  it("surfaces the conflict when target content differs from stride's source", () => {
    resetFixture();
    writeFixture(SKILL_FILE_REL, "consumer modified this skill");

    const result = runInstallExpectFailure();

    notStrictEqual(result, null, "install should exit with non-zero status");
    strictEqual(result.status, 1);
    match(result.stderr, /SKILL\.md/);
    strictEqual(readFixture(SKILL_FILE_REL), "consumer modified this skill");
  });

  it("follows symlinks when a skill is installed as a directory-target symlink", () => {
    resetFixture();
    const external = join(fixtureRoot, "external-tool/skills/commit");
    mkdirSync(dirname(external), { recursive: true });
    cpSync(join(strideRoot, SKILL_REL), external, { recursive: true });
    const symlinkPath = join(fixtureRoot, SKILL_REL);
    mkdirSync(dirname(symlinkPath), { recursive: true });
    symlinkSync(external, symlinkPath);

    runInstall();

    strictEqual(lstatSync(symlinkPath).isSymbolicLink(), true);
    strictEqual(readFixture(SKILL_FILE_REL), readStride(SKILL_FILE_REL));
  });

  it("installs missing files and flags the differing file when mixed", () => {
    resetFixture();
    copyFromStride(SKILL_REL);
    const workflow = join(fixtureRoot, `${SKILL_REL}/WORKFLOW.md`);
    writeFileSync(workflow, "consumer modified this file");
    const skillMd = join(fixtureRoot, SKILL_FILE_REL);
    rmSync(skillMd);

    const result = runInstallExpectFailure();

    notStrictEqual(result, null);
    strictEqual(result.status, 1);
    match(result.stderr, /WORKFLOW\.md/);
    strictEqual(existsSync(skillMd), true);
    strictEqual(readFixture(SKILL_FILE_REL), readStride(SKILL_FILE_REL));
    strictEqual(readFileSync(workflow, "utf8"), "consumer modified this file");
  });
});
