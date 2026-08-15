#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'

MAX_TOTAL=512*1024
MAX_HTML=24*1024
MAX_CSS=36*1024
MAX_IMAGE=128*1024
MAX_INLINE_JS=24*1024

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
total=sum(p.stat().st_size for p in files)
checks+=1
if total>MAX_TOTAL:errors.append(f'total payload {total} > {MAX_TOTAL}')

css=LIVE/'style.css'; checks+=1
if css.stat().st_size>MAX_CSS:errors.append(f'style.css {css.stat().st_size} > {MAX_CSS}')

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

print(f'performance_checks={checks} total_bytes={total} css_bytes={css.stat().st_size} files={len(files)}')
if errors:
    print('STATIC_PERFORMANCE_FAIL');[print('-',e) for e in errors];sys.exit(1)
print('STATIC_PERFORMANCE_PASS')
