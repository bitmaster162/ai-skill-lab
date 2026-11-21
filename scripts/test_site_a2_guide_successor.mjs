/**
 * Exact SITE-A1/A2 guide-source admission tests.
 * Compiles the existing TypeScript with locally installed typescript,
 * runs the actual listGuides export with original and tampered release bytes.
 * No filesystem mutations, network, booking, forms, or deployment.
 */
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
import vm from "node:vm";
import { createRequire } from "node:module";
import test from "node:test";
import ts from "typescript";

const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(path.join(repo, "lib/guides.ts"), "utf8");
const compiled = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2022,
    esModuleInterop: true,
  },
  reportDiagnostics: true,
});
assert.deepEqual((compiled.diagnostics ?? []).filter(x => x.category === ts.DiagnosticCategory.Error), []);
const liveManifest = readFileSync(path.join(repo, "deploy/live/_release.json"));
const originalManifest = execFileSync("git", ["show",
  "b40470c884715ec580edd0beefb175d50ea0e660:deploy/live/_release.json"], { cwd: repo });
const originalAdmission = readFileSync(path.join(repo, "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json"));
const digest = bytes => createHash("sha256").update(bytes).digest("hex");
assert.equal(digest(originalManifest), "79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889");
assert.equal(digest(originalAdmission), "fb4a04354f1a99a2d2d0cc7b5364403b2b520406660cdeb9d4ce3eaf865c7034");

function guideRoutes(manifestBytes, admissionBytes, overrides = new Map()) {
  const fakeFs = {
    ...fs,
    readFileSync(file, ...args) {
      const name = path.normalize(String(file));
      if (overrides.has(name)) return overrides.get(name);
      if (name === path.join(repo, "deploy/live/_release.json")) return Buffer.from(manifestBytes);
      if (name === path.join(repo, "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json")) return Buffer.from(admissionBytes);
      return fs.readFileSync(file, ...args);
    },
  };
  const exports = {};
  const fakeModule = { exports };
  const require = name => {
    if (name === "node:fs") return fakeFs;
    if (name === "node:path") return path;
    if (name === "node:crypto") return createRequire(import.meta.url)("node:crypto");
    throw new Error("Unapproved module import: " + name);
  };
  vm.runInNewContext(compiled.outputText, {
    require, module: fakeModule, exports, process: { cwd: () => repo }, Buffer, console, Date,
  }, { filename: "lib/guides.ts (transpiled)", timeout: 4000 });
  const adult = "ai-first-tasks-for-adults";
  return {
    ru: fakeModule.exports.listGuides("ru").some(x => x.slug === adult),
    en: fakeModule.exports.listGuides("en").some(x => x.slug === adult),
  };
}

test("exact new successor yields both RU and EN guide routes", () => {
  assert.deepEqual(guideRoutes(originalManifest, originalAdmission), { ru: true, en: true });
});
test("tampered manifest denies both guide routes", () => {
  const altered = Buffer.from(originalManifest);
  altered[20] ^= 1;
  assert.deepEqual(guideRoutes(altered, originalAdmission), { ru: false, en: false });
});
test("tampered admission denies both guide routes", () => {
  const altered = Buffer.from(originalAdmission);
  altered[20] ^= 1;
  assert.deepEqual(guideRoutes(originalManifest, altered), { ru: false, en: false });
});
test("unknown patch id denies both guide routes", () => {
  const modified = JSON.parse(originalManifest.toString("utf8"));
  modified.patch_id = "UNAUTHORIZED_PATCH";
  assert.deepEqual(guideRoutes(Buffer.from(JSON.stringify(modified)), originalAdmission), { ru: false, en: false });
});

test("the frozen analytics R3 payload still admits both existing locales", () => {
  const revision = "3b77fdf9d3a48571420ef588bbf33e72e53df71a";
  const atR3 = rel => execFileSync("git", ["show", revision + ":" + rel], {cwd:repo});
  const parents = ["deploy/live/index.html", "deploy/live/en/method.html"];
  const files = new Map(parents.map(rel => [path.join(repo, rel), atR3(rel)]));
  const r3 = atR3("deploy/live/_release.json");
  assert.equal(digest(r3), "9758df02a2c862c643cd87c5005176ff3751ca72011ffbdaacd7112588043c73");
  assert.deepEqual(guideRoutes(r3, originalAdmission, files), {ru:true, en:true});
  assert.deepEqual(guideRoutes(r3, originalAdmission), {ru:false, en:false});
});

test("the sealed donor successor admits both existing guide locales", () => {
  assert.deepEqual(guideRoutes(liveManifest, originalAdmission), {ru:true, en:true});
});
test("an edited successor manifest or shipped byte denies both locales", () => {
  const hidden = {ru:false, en:false};
  assert.deepEqual(guideRoutes(Buffer.concat([liveManifest, Buffer.from(" ")]), originalAdmission), hidden);
  for (const rel of ["deploy/live/guides/ai-first-tasks-for-adults.html",
    "deploy/live/en/guides/ai-first-tasks-for-adults.html", "deploy/live/analytics/preferences.js"]) {
    const file = path.join(repo, rel);
    const changed = Buffer.concat([readFileSync(file), Buffer.from(" ")]);
    assert.deepEqual(guideRoutes(liveManifest, originalAdmission, new Map([[file, changed]])), hidden);
  }
});
