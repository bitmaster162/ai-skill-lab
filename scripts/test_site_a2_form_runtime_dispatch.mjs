import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { verifySiteA2FormRuntime } from "./site_a2_form_runtime_dispatch.mjs";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const m=readFileSync(path.join(root,"deploy/live/_release.json"));
const a=readFileSync(path.join(root,"data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json"));
test("pinned SITE-A2 release selects inherited R31 form runtime",()=>assert.equal(verifySiteA2FormRuntime(m,a),true));
test("tampered manifest denied",()=>assert.throws(()=>verifySiteA2FormRuntime(Buffer.concat([m,Buffer.from(" ")]),a),/DENY SHA/));
test("tampered admission denied",()=>assert.throws(()=>verifySiteA2FormRuntime(m,Buffer.concat([a,Buffer.from(" ")])),/DENY SHA/));
test("unknown patch denied",()=>{
  const wrong=JSON.parse(m.toString("utf8"));wrong.patch_id="UNAUTHORIZED_PATCH";
  assert.throws(()=>verifySiteA2FormRuntime(Buffer.from(JSON.stringify(wrong)),a),/DENY SHA/);
});
test("missing manifest bytes denied",()=>assert.throws(()=>verifySiteA2FormRuntime(m.subarray(0,m.length-1),a),/DENY SHA/));
