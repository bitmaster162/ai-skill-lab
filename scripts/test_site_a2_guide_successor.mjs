/**
 * Exact SITE-A1/A2 guide-source admission tests.
 * Compiles the existing TypeScript with locally installed typescript,
 * stubs ONLY two pinned file reads, and calls the actual listGuides export.
 * No filesystem mutations, network, booking, forms, or deployment.
 */
import assert from "node:assert/strict";
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
const originalManifest = readFileSync(path.join(repo, "deploy/live/_release.json"));
const originalAdmission = readFileSync(path.join(repo, "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json"));
const digest = bytes => createHash("sha256").update(bytes).digest("hex");
assert.equal(digest(originalManifest), "11d341f50a1ed97b4c1335f27524a2383b2db92a52a19d44a33674e4013dd727");
assert.equal(digest(originalAdmission), "9102807cee2df87332543e53f83d8b645d81876d9cf6bd1ad26745df0f83eadd");

function guideRoutes(manifestBytes, admissionBytes) {
  const fakeFs = {
    ...fs,
    readFileSync(file, ...args) {
      const name = path.normalize(String(file));
      if (name === path.join(repo, "deploy/live/_release.json")) return Buffer.from(manifestBytes);
      if (name === path.join(repo, "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json")) return Buffer.from(admissionBytes);
      return fs.readFileSync(file, ...args);
    },
  };
  const exports = {};
  const module = { exports };
  const require = name => {
    if (name === "node:fs") return fakeFs;
    if (name === "node:path") return path;
    if (name === "node:crypto") return createRequire(import.meta.url)("node:crypto");
    throw new Error("Unapproved module import: " + name);
  };
  vm.runInNewContext(compiled.outputText, {
    require, module, exports, process: { cwd: () => repo }, Buffer, console, Date,
  }, { filename: "lib/guides.ts (transpiled)", timeout: 4000 });
  const adult = "ai-first-tasks-for-adults";
  return {
    ru: module.exports.listGuides("ru").some(x => x.slug === adult),
    en: module.exports.listGuides("en").some(x => x.slug === adult),
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
