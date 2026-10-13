#!/usr/bin/env python3
"""Reproduce an unpublished static site candidate; preserve the sealed release.

python -B scripts/build_site_form_preview_r1.py --out <NEW_DIRECTORY> --receipt <JSON>
No network, package installs, production writes or release-gate changes.
The React source and this static adapter implement the same readiness behavior.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from verify_site_metadata_preview_r1 import CHANGES, Html, script_hashes

ROOT = Path(__file__).resolve().parents[1]
SEALED = ROOT / 'deploy/live'
BASE = 'ab48f07ec41c6a0cb5761bb8a9ad601f56fbf8f3'
RELEASE = 'SITE_FORM_READINESS_CANDIDATE_R1_20261014'
COPY = {
    'en': ('The form is not ready yet. You can contact us directly.',
           'Direct contacts: Telegram, WhatsApp, LINE or email'),
    'ru': ('Форма пока не готова к отправке. Можно связаться напрямую.',
           'Прямые контакты: Telegram, WhatsApp, LINE или email'),
}

def require(ok: bool, message: str) -> None:
    if not ok: raise RuntimeError(message)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git(*args: str) -> bytes:
    p = subprocess.run(['git','--no-optional-locks','-C',str(ROOT),*args],capture_output=True,timeout=15)
    require(p.returncode == 0, 'Git read failed')
    return p.stdout

def verify_manifest(folder: Path) -> dict:
    m = json.loads((folder/'_release.json').read_bytes())
    names = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p.name != '_release.json'}
    require(names == {f['path'] for f in m['files']} and len(names) == m['file_count'], 'Manifest inventory drift')
    for f in m['files']:
        p = (folder/f['path']).resolve()
        require(p.is_relative_to(folder.resolve()) and p.is_file(), 'Manifest path unsafe')
        b=p.read_bytes()
        require(len(b)==f['size'] and sha(b)==f['sha256'], 'Manifest mismatch: '+f['path'])
    aggregate=''.join(f"{f['path']}\t{f['size']}\t{f['sha256']}\n" for f in m['files']).encode()
    require(sha(aggregate)==m['payload_sha256'],'Manifest aggregate mismatch')
    return m

def build(out: Path) -> dict:
    out=out.resolve()
    require(not out.exists() and ROOT not in out.parents and out!=ROOT,'Use new output outside the repository')
    require(not git('diff',BASE,'--','deploy/live'),'Sealed release was modified')
    original=verify_manifest(SEALED)
    require(original['release_id']=='T1_6F2_ADULT_FIRST_TASKS_R1','Parent release drift')
    # Copy into a new staging location, omitting its parent's immutable manifest.
    shutil.copytree(SEALED,out,ignore=shutil.ignore_patterns('_release.json'))
    for source,rel,field,count,before,after in CHANGES:
        require(after in (ROOT/source).read_text(encoding='utf-8'),'Metadata source drift')
        p=out/rel;s=p.read_text(encoding='utf-8')
        require(s.count(before) in (3,4),'Metadata occurrence drift')
        p.write_bytes(s.replace(before,after).encode('utf-8'))
    for locale,rel in [('ru','start.html'),('en','en/start.html')]:
        p=out/rel;s=p.read_text(encoding='utf-8')
        form='<form class="leadForm" id="application-form">'
        require(s.count(form)==1,'Static form not unique')
        old_notes=re.findall(r'<noscript><p class="formNote">[^<]*</p></noscript>',s)
        require(len(old_notes)==1,'Old form fallback not unique')
        s=s.replace(old_notes[0],'',1)
        note,contact=COPY[locale]
        s=s.replace(form,form[:-1]+' data-lead-state="unready">'+
                    '<p class="formNote" data-lead-readiness role="status">'+note+'</p>'+
                    '<p class="formNote" data-lead-direct-contact><a href="#contact-channels">'+contact+'</a></p>',1)
        old='<button class="workshopButton workshopButtonPrimary formSubmit" type="submit">'
        require(s.count(old)==1,'Submit button not unique')
        s=s.replace(old,old[:-1]+' disabled>',1)
        script=re.findall(r'<script\b[^>]*src="/start-brief.js"[^>]*></script>',s)
        require(len(script)==1,'Brief script not unique')
        s=s.replace(script[0],script[0]+'<script src="/lead-form-runtime.js" defer></script>',1)
        p.write_bytes(s.encode('utf-8'))
    brief=out/'start-brief.js';raw=brief.read_bytes()
    split=b'(function(){"use strict";const form=document.querySelector("#application-form");'
    require(raw.count(split)==1,'Legacy form adapter boundary drift')
    prefix=raw.split(split,1)[0]
    require(prefix.endswith(b'\n'),'Brief prefix boundary changed')
    brief.write_bytes(prefix)
    runtime=(ROOT/'public/lead-form-runtime.js').read_bytes()
    (out/'lead-form-runtime.js').write_bytes(runtime)
    # Only the metadata edit changes inline JSON-LD. Form scripts stay external.
    old_hashes,new_hashes=script_hashes(SEALED),script_hashes(out)
    removed,added=old_hashes-new_hashes,new_hashes-old_hashes
    require(len(removed)==len(added)==1,'Unexpected inline-script changes')
    cfg=out/'vercel.json';s=cfg.read_text(encoding='utf-8')
    require(s.count(next(iter(removed)))==1,'Old CSP hash not unique')
    s=s.replace(next(iter(removed)),next(iter(added)),1);cfg.write_bytes(s.encode('utf-8'))
    require("form-action 'none'" in s and "'unsafe-inline'" not in s,'CSP weakened')
    require(all(h in s for h in new_hashes),'Inline script missing from CSP')
    urls=[x.text for x in ET.parse(out/'sitemap.xml').getroot().findall('{*}url/{*}loc')]
    require(len(urls)==54,'Route-count drift')
    for url in urls:
        route=urlsplit(str(url)).path
        rel='index.html' if route=='/' else route.strip('/')+'.html'
        h=Html();h.feed((out/rel).read_text(encoding='utf-8'))
        require(h.h1==1 and h.canonical==[url],'H1/canonical mismatch: '+route)
        require(0<len(h.title)<=60 and 0<len(h.meta.get('description',''))<=160,'Editorial length mismatch: '+route)
    require((out/'sitemap.xml').read_bytes()==(SEALED/'sitemap.xml').read_bytes(),'Sitemap dates changed')
    changed=sorted(p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and
                   (not (SEALED/p.relative_to(out)).exists() or p.read_bytes()!=(SEALED/p.relative_to(out)).read_bytes()))
    expected=sorted(['en.html','en/start.html','en/guides/ai-safety-for-kids.html','start.html',
                     'start-brief.js','lead-form-runtime.js','vercel.json'])
    require(changed==expected,'Unexpected preview file changes: '+repr(changed))
    files=[]
    for p in sorted((p for p in out.rglob('*') if p.is_file()),key=lambda p:p.relative_to(out).as_posix()):
        b=p.read_bytes();files.append({'path':p.relative_to(out).as_posix(),'size':len(b),'sha256':sha(b)})
    require(len(files)==99,'Candidate should have 99 payload files')
    aggregate=''.join(f"{f['path']}\t{f['size']}\t{f['sha256']}\n" for f in files).encode()
    manifest={'schema':'ai-skill-lab.static-release.v1','release_id':RELEASE,'file_count':len(files),
              'files':files,'payload_sha256':sha(aggregate)}
    (out/'_release.json').write_bytes((json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8'))
    verify_manifest(out);verify_manifest(SEALED)
    return {'release_id':RELEASE,'payload_sha256':manifest['payload_sha256'],'routes_checked':54,
            'members_checked':99,'preview_changed_files':changed+['_release.json'],'metadata_preserved':True,
            'sealed_release_preserved':True,'sitemap_dates_preserved':True,'csp_directives_preserved':True,
            'out':str(out),'production_changes':0,'release_admission':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True,type=Path);p.add_argument('--receipt',required=True,type=Path)
    a=p.parse_args();require(not a.receipt.exists(),'Receipt already exists')
    report=build(a.out);a.receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True))
