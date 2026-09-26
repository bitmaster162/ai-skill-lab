#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json, re, sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'

release=json.loads((LIVE/'_release.json').read_text(encoding='utf-8')).get('release_id')
MAX_NON_FONT_TOTAL=(556 if release in {'R143_R136_A1_A8_CLOSEOUT','R144_ICON_CACHE_PARITY','R145_PWA_INSTALLABILITY'} else 536 if release=='R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH' else 526)*1024  # R142: bounded global footer/content growth; prior releases unchanged
MAX_FONT_TOTAL=84*1024
MAX_FONT_FILE=54*1024
MAX_HTML=24*1024
MAX_CSS=36*1024
MAX_IMAGE=128*1024
MAX_INLINE_JS=24*1024
IMPORT_RE=re.compile(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)', re.I)

class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.subresources=[]; self.stylesheets=0; self.in_script=False; self.script_external=False; self.buf=[]; self.inline_scripts=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='link':
            rel=set((a.get('rel') or '').lower().split())
            href=a.get('href','')
            if 'stylesheet' in rel:
                self.stylesheets+=1; self.subresources.append(('stylesheet',href))
            elif rel & {'icon','manifest','preload','modulepreload'}:
                self.subresources.append(('/'.join(sorted(rel)),href))
        elif tag in {'img','source','video','audio','iframe'}:
            src=a.get('src') or a.get('srcset') or ''
            if src:self.subresources.append((tag,src))
        elif tag=='script':
            src=a.get('src','')
            if src:self.subresources.append(('script',src));self.script_external=True
            else:self.in_script=True;self.script_external=False;self.buf=[]
    def handle_data(self,data):
        if self.in_script:self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.in_script:
            self.inline_scripts.append(''.join(self.buf));self.in_script=False;self.buf=[]

def external(url:str)->bool:
    u=urlparse(url)
    return bool(u.scheme or u.netloc) and not url.startswith('data:')

errors=[]; checks=0
files=[p for p in LIVE.rglob('*') if p.is_file() and p.name!='_release.json']
font_files=[p for p in files if p.suffix.lower()=='.woff2']
font_total=sum(p.stat().st_size for p in font_files)
non_font_total=sum(p.stat().st_size for p in files if p not in font_files)
total=font_total+non_font_total
checks+=1
if non_font_total>MAX_NON_FONT_TOTAL:errors.append(f'non-font payload {non_font_total} > {MAX_NON_FONT_TOTAL}')
checks+=1
if font_total>MAX_FONT_TOTAL:errors.append(f'font payload {font_total} > {MAX_FONT_TOTAL}')
checks+=1
if len(font_files)!=2:errors.append(f'woff2 files {len(font_files)} != 2')
for font in font_files:
    checks+=1
    if font.stat().st_size>MAX_FONT_FILE:errors.append(f'{font.relative_to(LIVE)} {font.stat().st_size} > {MAX_FONT_FILE}')

css_files=sorted(LIVE.rglob('*.css'))
for css in css_files:
    rel=css.relative_to(LIVE).as_posix(); checks+=1
    if css.stat().st_size>MAX_CSS:errors.append(f'{rel} {css.stat().st_size} > {MAX_CSS}')
    text=css.read_text(encoding='utf-8')
    for raw in IMPORT_RE.findall(text):
        checks+=1
        if external(raw):
            errors.append(f'{rel}: external CSS import {raw}')
            continue
        target=(LIVE/raw.split('?',1)[0].split('#',1)[0].lstrip('/')).resolve()
        live=LIVE.resolve()
        if target!=live and live not in target.parents:
            errors.append(f'{rel}: CSS import escapes live root {raw}')
        elif not target.is_file():
            errors.append(f'{rel}: missing CSS import {raw}')

for p in sorted(LIVE.rglob('*.html')):
    rel=p.relative_to(LIVE).as_posix(); size=p.stat().st_size; checks+=1
    if size>MAX_HTML:errors.append(f'{rel}: HTML {size} > {MAX_HTML}')
    a=Audit();a.feed(p.read_text(encoding='utf-8'))
    checks+=1
    if a.stylesheets!=1:errors.append(f'{rel}: expected exactly 1 stylesheet, got {a.stylesheets}')
    inline_bytes=sum(len(x.encode('utf-8')) for x in a.inline_scripts); checks+=1
    if inline_bytes>MAX_INLINE_JS:errors.append(f'{rel}: inline script bytes {inline_bytes} > {MAX_INLINE_JS}')
    for kind,url in a.subresources:
        checks+=1
        if external(url):errors.append(f'{rel}: external {kind} subresource {url}')

for p in sorted(LIVE.rglob('*')):
    if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif','.avif'}:
        checks+=1
        if p.stat().st_size>MAX_IMAGE:errors.append(f'{p.relative_to(LIVE)}: image {p.stat().st_size} > {MAX_IMAGE}')

print(f'performance_checks={checks} total_bytes={total} non_font_bytes={non_font_total} font_bytes={font_total} css_files={len(css_files)} files={len(files)}')
if errors:
    print('STATIC_PERFORMANCE_FAIL');[print('-',e) for e in errors];sys.exit(1)
print('STATIC_PERFORMANCE_PASS')
