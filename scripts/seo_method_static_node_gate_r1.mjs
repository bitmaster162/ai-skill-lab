// Read-only admission of the exact versioned static-method release for Node QA.
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';

export const EXACT_RELEASE_ID = 'AISL_SEO_METHOD_R1_DRAFT_20261121';
export const EXACT_MANIFEST_SHA256 = 'ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0';
const digest = (b) => createHash('sha256').update(b).digest('hex');
const exactProof = [
  'import sys',
  "sys.path.insert(0,'scripts')",
  'from seo_method_static_release_profile_r1 import verify',
  'proof=verify(require_live=True)',
  "assert proof['status']=='STATIC_PAYLOAD_MATCH_ONLY'",
  "assert proof['file_count']==108 and proof['public_routes']==56",
  "assert proof['changed']==['en/method.html','method.html','sitemap.xml']",
  "assert proof['production_authority'] is False",
].join(';');

export function isVerifiedSeoMethodRelease(root, manifestOverride = null) {
  const raw = manifestOverride === null
    ? fs.readFileSync(path.join(root, 'deploy/live/_release.json'))
    : manifestOverride;
  if (!Buffer.isBuffer(raw)) throw new Error('SEO_METHOD_NODE_DENY_NON_BYTES');
  let obj;
  try { obj = JSON.parse(raw.toString('utf8')); }
  catch { throw new Error('SEO_METHOD_NODE_DENY_JSON'); }
  if (obj.release_id !== EXACT_RELEASE_ID) return false;
  if (obj.patch_id !== EXACT_RELEASE_ID || obj.file_count !== 108 ||
      digest(raw) !== EXACT_MANIFEST_SHA256) {
    throw new Error('SEO_METHOD_NODE_DENY_EXACT_MANIFEST');
  }
  const result = spawnSync('python', ['-B', '-c', exactProof], {
    cwd: root, encoding: 'utf8', timeout: 80000,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
    maxBuffer: 65536,
  });
  if (result.error || result.status !== 0) {
    throw new Error('SEO_METHOD_NODE_DENY_STATIC_PROOF');
  }
  return true;
}

// Consumers of the unchanged historical gates can also validate the sealed child.
export function isVerifiedMethodLineage(root, manifestOverride = null) {
  const raw = manifestOverride ?? fs.readFileSync(path.join(root, 'deploy/live/_release.json'));
  if (!Buffer.isBuffer(raw)) throw new Error('METHOD_LINEAGE_DENY_NON_BYTES');
  let manifest;
  try { manifest = JSON.parse(raw.toString('utf8')); }
  catch { throw new Error('METHOD_LINEAGE_DENY_JSON'); }
  if (!['AISL_ADULT_GA4_OPT_IN_R3_20261121', 'AISL_ADULT_GUIDE_DONORS_R1_20261121',
        'AISL_DIAGNOSTIC_INTENT_R1_20261121', 'AISL_DIAGNOSTIC_INTENT_R2_20261121', 'AISL_SITEMAP_ROUTE_DATES_R1_20261122'].includes(manifest.release_id)) {
    return isVerifiedSeoMethodRelease(root, raw);
  }
  const result = spawnSync('python', ['-B', '-c', [
    'import sys',
    "sys.path.insert(0, 'scripts')",
    'from hashlib import sha256',
    'from adult_analytics_lineage import current_release',
    'release = current_release()',
    'matched = release.active() and sha256(sys.stdin.buffer.read()).hexdigest() == release.MANIFEST_SHA',
    'from seo_method_static_release_profile_r1 import verified_live_lineage',
    'sys.exit(0 if matched and verified_live_lineage() else 1)',
  ].join(';')], {cwd: root, input: raw, timeout: 80000, encoding: 'utf8'});
  if (result.error || result.status !== 0) throw new Error('METHOD_LINEAGE_DENY_EXACT_PROOF');
  return true;
}
