#!/usr/bin/env node
// Offline, source-pinned positive and negative gate tests; never modify source/manifest.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import Module, { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
process.chdir(root);
const require = createRequire(import.meta.url);
const ts = require("typescript");
const sourcePath = path.join(root, "lib", "guides.ts");
const input = fs.readFileSync(sourcePath, "utf8");
const compiled = ts.transpileModule(input, {
  compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, esModuleInterop: true,
  },
  reportDiagnostics: true,
});
assert.equal((compiled.diagnostics || []).filter(d => d.category === ts.DiagnosticCategory.Error).length, 0);
const mod = new Module(sourcePath);
mod.filename = sourcePath;
mod.paths = Module._nodeModulePaths(path.dirname(sourcePath));
mod._compile(compiled.outputText, sourcePath);
const listGuides = mod.exports.listGuides;
assert.equal(typeof listGuides, "function");
const all = locale => listGuides(locale).map(x => x.slug).sort();
const expected = ["ai-first-tasks-for-adults", "ai-safety-for-kids"];
for (const locale of ["ru", "en"]) assert.deepEqual(all(locale), expected);

const manifestPath = path.resolve(root, "deploy/live/_release.json");
const ruGuidePath = path.resolve(root, "guides/aiskillab/ai-first-tasks-for-adults.ru.md");
const originalRead = fs.readFileSync;
const manifestBytes = originalRead.call(fs, manifestPath);
const originalSha = createHash("sha256").update(manifestBytes).digest("hex");
assert.equal(originalSha, "b10b2ad45184e2f19a329dbe22b7e2c18fef0c075f13a31a435abdf83167adc3");

function assertDenied(label, targetPath, content) {
  fs.readFileSync = function(p, ...rest) {
    if (path.resolve(String(p)) === targetPath) {
      return rest[0] === "utf8" ? content.toString("utf8") : content;
    }
    return originalRead.call(this, p, ...rest);
  };
  try {
    for (const locale of ["ru", "en"]) assert.deepEqual(all(locale), ["ai-safety-for-kids"], label);
  } finally {
    fs.readFileSync = originalRead;
  }
}
const rawManifest = JSON.parse(manifestBytes.toString("utf8"));
const replaceManifest = (label, change) => {
  const altered = structuredClone(rawManifest);
  change(altered);
  assertDenied(label, manifestPath, Buffer.from(JSON.stringify(altered), "utf8"));
};
replaceManifest("incorrect patch", m => { m.patch_id = "other-patch"; });
replaceManifest("incorrect parent", m => { m.parent_manifest_sha256 = "0".repeat(64); });
replaceManifest("incorrect payload", m => { m.payload_sha256 = "0".repeat(64); });
replaceManifest("unreviewed new asset", m => { m.files[0].sha256 = "0".repeat(64); });
replaceManifest("incorrect asset count", m => { m.file_count = 108; });
assertDenied("manifest byte drift", manifestPath, Buffer.concat([manifestBytes, Buffer.from(" ")]));
assertDenied("guide markdown mutation", ruGuidePath,
  Buffer.concat([originalRead.call(fs, ruGuidePath), Buffer.from("\nextra")]));
assert.equal(createHash("sha256").update(originalRead.call(fs, manifestPath)).digest("hex"), originalSha);
for (const locale of ["ru", "en"]) assert.deepEqual(all(locale), expected);
console.log("R7C_GUIDE_ADMISSION_PASS positive=2 locales negative=7 fail_closed=true no_disk_writes=true");
