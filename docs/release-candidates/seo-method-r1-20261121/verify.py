#!/usr/bin/env python3
"""Fail-closed, read-only verification of an unapproved static SEO candidate."""
from pathlib import Path
import hashlib, json, re, zipfile
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PARENT=REPO/'deploy/live'
SHA=lambda x:hashlib.sha256(x).hexdigest()
EXPECTED_PARENT='79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889'
EXPECTED_MANIFEST='ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0'
EXPECTED_ARCHIVE='189f273538137c2d4603a7bd9f25b8969e1deed5c7314c2e5509092ecd89b56d'
oldraw=(PARENT/'_release.json').read_bytes()
newraw=(HERE/'manifest.json').read_bytes()
assert SHA(oldraw)==EXPECTED_PARENT and SHA(newraw)==EXPECTED_MANIFEST
old=json.loads(oldraw);m=json.loads(newraw)
assert m['parent_manifest_sha256']==EXPECTED_PARENT
assert m['release_id']=='AISL_SEO_METHOD_R1_DRAFT_20261121'
assert m['patch_id']=='AISL_SEO_METHOD_R1_DRAFT_20261121'
assert m['file_count']==old['file_count']==108
zipdata=(HERE/'review.zip').read_bytes()
assert SHA(zipdata)==EXPECTED_ARCHIVE
assert (HERE/'review.sha256').read_text().split()[0]==EXPECTED_ARCHIVE
def one_main(b):
 rows=re.findall(rb'<main id="main"[\s\S]*?</main>',b)
 assert len(rows)==1
 return rows[0]
with zipfile.ZipFile(HERE/'review.zip') as z:
 names=z.namelist()
 assert len(names)==len(set(names))==109 and '_release.json' in names
 assert z.read('_release.json')==newraw
 assert set(names)==set(x['path'] for x in m['files'])|{'_release.json'}
 bypath={x['path']:x for x in m['files']}
 assert len(bypath)==108
 for n,x in bypath.items():
  data=z.read(n)
  assert SHA(data)==x['sha256'] and len(data)==x['size'],n
 digest=''.join(f"{x['path']}\t{x['size']}\t{x['sha256']}\n" for x in sorted(m['files'],key=lambda v:v['path'])).encode()
 assert SHA(digest)==m['payload_sha256']
 oldfiles={x['path']:(PARENT/x['path']).read_bytes() for x in old['files']}
 assert all(SHA(oldfiles[x['path']])==x['sha256'] for x in old['files'])
 changed={n for n in bypath if oldfiles[n]!=z.read(n)}
 assert changed=={'method.html','en/method.html','sitemap.xml'},changed
 for name,source,want in [
  ('method.html','app/(ru)/method/page.tsx','ada13cf8a2f95e8443b2a55039c36a9732378b4643d68f15115d9ef8a6ba345c'),
  ('en/method.html','app/(en)/en/method/page.tsx','67aa5fa4440a398bf43c50829fe8e3693b29b76af81e6d490c82b5289919fc59')]:
  assert SHA((REPO/source).read_bytes())==want
  prev,candidate=oldfiles[name],z.read(name)
  before,after=one_main(prev),one_main(candidate)
  assert prev.replace(before,b'__MAIN__',1)==candidate.replace(after,b'__MAIN__',1)
  assert after.count(b'<article')==5 and after.count(b'<h1')==1
  assert b'method-example' in after and b'<form' not in after and b'<script' not in after
  assert b'/_next/' not in candidate and candidate.count(b'<script')==prev.count(b'<script')
  assert candidate== (HERE/name).read_bytes()
  rendered=REPO/'.next/server/app'/name
  if rendered.exists(): assert one_main(rendered.read_bytes())==after,'SSR main mismatch'
  assert b'/workshop.css' in candidate
 old_sitemap=oldfiles['sitemap.xml'].decode()
 for route in ('/method','/en/method'):
  a=f'<loc>https://aiskillab.work{route}</loc><lastmod>2026-10-16</lastmod>'
  b=f'<loc>https://aiskillab.work{route}</loc><lastmod>2026-11-21</lastmod>'
  assert old_sitemap.count(a)==1
  old_sitemap=old_sitemap.replace(a,b)
 assert z.read('sitemap.xml')==old_sitemap.encode()==(HERE/'sitemap.xml').read_bytes()
print('SEO_METHOD_CANDIDATE=PASS files=108 changed=3 manifest='+EXPECTED_MANIFEST+' status=DRAFT_NOT_ADMITTED')
