#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import base64, hashlib, json

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'
CONFIG=LIVE/'vercel.json'

class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.in_script=False
        self.buf=[]
        self.scripts=[]
    def handle_starttag(self,tag,attrs):
        if tag=='script':
            a=dict(attrs)
            if not a.get('src'):
                self.in_script=True; self.buf=[]
    def handle_data(self,data):
        if self.in_script: self.buf.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self.in_script:
            self.scripts.append(''.join(self.buf))
            self.in_script=False; self.buf=[]

def digest(text:str)->str:
    raw=hashlib.sha256(text.encode('utf-8')).digest()
    return "'sha256-"+base64.b64encode(raw).decode('ascii')+"'"

scripts=[]
for p in sorted(LIVE.rglob('*.html')):
    parser=Scripts(); parser.feed(p.read_text(encoding='utf-8'))
    scripts.extend(x for x in parser.scripts if x.strip())
hashes=sorted({digest(x) for x in scripts})
script_src=' '.join(["'self'",*hashes])
csp='; '.join([
    "default-src 'self'",
    f"script-src {script_src}",
    "style-src 'self'",
    "img-src 'self' data:",
    "font-src 'self'",
    "connect-src 'none'",
    "media-src 'none'",
    "object-src 'none'",
    "frame-src 'none'",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'none'",
    "manifest-src 'self'",
    "worker-src 'none'",
    "upgrade-insecure-requests",
])
obj=json.loads(CONFIG.read_text(encoding='utf-8'))
headers=obj.setdefault('headers',[])
root_rule=next((x for x in headers if x.get('source')=='/(.*)'),None)
if root_rule is None:
    root_rule={'source':'/(.*)','headers':[]}; headers.insert(0,root_rule)
items=root_rule.setdefault('headers',[])
wanted={
    'Content-Security-Policy':csp,
    'X-Content-Type-Options':'nosniff',
    'Referrer-Policy':'strict-origin-when-cross-origin',
    'X-Frame-Options':'DENY',
    'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
    'X-Permitted-Cross-Domain-Policies':'none',
}
by_key={x.get('key'):x for x in items}
for key,value in wanted.items():
    if key in by_key: by_key[key]['value']=value
    else: items.append({'key':key,'value':value})
CONFIG.write_text(json.dumps(obj,separators=(',',':'),ensure_ascii=False)+'\n',encoding='utf-8')
print(f'CSP_BUILD_PASS inline_scripts={len(scripts)} unique_hashes={len(hashes)}')
for h in hashes: print(h)
