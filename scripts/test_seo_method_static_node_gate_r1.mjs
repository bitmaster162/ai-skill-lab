// Negative fixtures are in-memory; no static release files are modified.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { isVerifiedMethodLineage, isVerifiedSeoMethodRelease, EXACT_MANIFEST_SHA256, EXACT_RELEASE_ID } from './seo_method_static_node_gate_r1.mjs';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const live = fs.readFileSync(path.join(root, 'deploy/live/_release.json'));
const inherited = JSON.parse(live).release_id === 'AISL_ADULT_GA4_OPT_IN_R3_20261121';
const original = inherited ? fs.readFileSync(path.join(root, 'docs/release-candidates/seo-method-r1-20261121/manifest.json')) : live;
const o = JSON.parse(original);
assert.equal(o.release_id, EXACT_RELEASE_ID);
assert.equal(isVerifiedSeoMethodRelease(root), !inherited);
if (inherited) {
  assert.throws(() => isVerifiedSeoMethodRelease(root, original), /STATIC_PROOF/);
  assert.equal(isVerifiedMethodLineage(root, live), true);
  assert.throws(() => isVerifiedMethodLineage(root, Buffer.concat([live, Buffer.from(' ')])), /EXACT_PROOF/);
}
const wrongHash = Buffer.concat([original, Buffer.from(' ')]);
assert.throws(() => isVerifiedSeoMethodRelease(root, wrongHash), /EXACT_MANIFEST/);
assert.throws(() => isVerifiedSeoMethodRelease(root, Buffer.from('{')), /_JSON/);
assert.throws(() => isVerifiedSeoMethodRelease(root, ''), /NON_BYTES/);
assert.equal(isVerifiedSeoMethodRelease(root, Buffer.from(JSON.stringify({ release_id:'UNRECOGNIZED' }))), false);
const replaced = Buffer.from(original.toString('utf8').replace(EXACT_RELEASE_ID, 'AISL_SEO_METHOD_R1_DRAFT_MUTATED'));
assert.throws(() => isVerifiedSeoMethodRelease(root, replaced), /EXACT_MANIFEST/);
assert.equal(EXACT_MANIFEST_SHA256.length,64);
console.log('SEO_METHOD_NODE_GATE_PASS exact_static_sha=1 manifest_tamper_denied=4 unknown_release_ignored=1 production_authority=DENY');
