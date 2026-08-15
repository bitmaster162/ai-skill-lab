#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import base64,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]; LIVE=ROOT/'deploy'/'live'
class P(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=False); self.on=False; self.buf=[]; self.s=[]
    def handle_starttag(self,t,a):
        if t=='script' and not dict(a).get('src'): self.on=True; self.buf=[]
    def handle_data(self,d):
        if self.on:self.buf.append(d)
    def handle_endtag(self,t):
        if t=='script' and self.on:self.s.append(''.join(self.buf));self.on=False;self.buf=[]
def h(s): return "'sha256-"+base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()+"'"
obj=json.loads((LIVE/'vercel.json').read_text())
rule=next((x for x in obj.get('headers',[]) if x.get('source')=='/(.*)'),{})
headers={x.get('key'):x.get('value') for x in rule.get('headers',[])}
errors=[]
required={
 'X-Content-Type-Options':'nosniff','Referrer-Policy':'strict-origin-when-cross-origin','X-Frame-Options':'DENY',
 'Permissions-Policy':'camera=(), microphone=(), geolocation=()','X-Permitted-Cross-Domain-Policies':'none'}
for k,v in required.items():
    if headers.get(k)!=v: errors.append(f'{k} mismatch')
csp=headers.get('Content-Security-Policy','')
for directive in ["default-src 'self'","style-src 'self'","connect-src 'none'","object-src 'none'","frame-ancestors 'none'","form-action 'none'","base-uri 'self'"]:
    if directive not in csp: errors.append(f'CSP missing {directive}')
if "'unsafe-inline'" in csp: errors.append('CSP must not use unsafe-inline')
if "'unsafe-eval'" in csp: errors.append('CSP must not use unsafe-eval')
scripts=[]
for p in sorted(LIVE.rglob('*.html')):
    txt=p.read_text(encoding='utf-8')
    if ' style=' in txt: errors.append(f'{p.relative_to(LIVE)} contains inline style attribute')
    q=P();q.feed(txt);scripts.extend(x for x in q.s if x.strip())
for digest in sorted({h(x) for x in scripts}):
    if digest not in csp: errors.append(f'CSP missing inline script hash {digest}')
if errors:
    print('SECURITY_HEADERS_FAIL'); [print('-',e) for e in errors]; sys.exit(1)
print(f'SECURITY_HEADERS_PASS inline_scripts={len(scripts)} unique_hashes={len(set(h(x) for x in scripts))}')
