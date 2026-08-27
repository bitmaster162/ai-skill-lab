#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlparse
import re, sys

from public_origin import PUBLIC_ORIGIN

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'
LLMS=LIVE/'llms.txt'
SITEMAP=LIVE/'sitemap.xml'
BASE=PUBLIC_ORIGIN
MAX_BYTES=4096

errors=[]; checks=0
if not LLMS.is_file():
    print('LLMS_TXT_AEO_FAIL')
    print('- missing deploy/live/llms.txt')
    raise SystemExit(1)

raw=LLMS.read_bytes(); checks+=1
if len(raw)>MAX_BYTES: errors.append(f'llms.txt {len(raw)} > {MAX_BYTES}')
try: text=raw.decode('utf-8')
except UnicodeDecodeError as e:
    print('LLMS_TXT_AEO_FAIL'); print('-',e); raise SystemExit(1)

checks+=1
if not text.startswith('# AI Skill Lab\n\n> '): errors.append('invalid H1/summary prefix')
checks+=1
if len(re.findall(r'(?m)^# ',text)) != 1: errors.append('expected exactly one H1')

required_sections=['Start','Learning paths','Studio and evidence','Pricing and policies','About']
for section in required_sections:
    checks+=1
    if f'## {section}' not in text: errors.append(f'missing section: {section}')

checks+=1
if 'Do not infer guarantees or commercial terms from this index.' not in text:
    errors.append('missing anti-inference guidance')

checks+=1
if re.search(r'(?i)(?:[$€£฿]\s*\d|\b\d[\d,.]*\s*(?:USD|EUR|GBP|THB)\b)',text):
    errors.append('hard-coded price/currency found')

checks+=1
if re.search(r'(?mi)^(?:User-agent|Allow|Disallow)\s*:',text):
    errors.append('crawler-policy directive must stay in robots.txt')

urls=re.findall(r'\]\((https?://[^)]+)\)',text)
checks+=1
if len(urls) != 32: errors.append(f'expected 32 canonical links, got {len(urls)}')
for url in urls:
    checks+=1
    if not url.startswith(BASE+'/'): errors.append(f'non-canonical URL: {url}')

locs=set(re.findall(r'<loc>(https?://[^<]+)</loc>',SITEMAP.read_text(encoding='utf-8')))
for url in urls:
    checks+=1
    if url not in locs: errors.append(f'URL not present in sitemap: {url}')

required_paths=[
    '/start','/en/start','/personal','/en/personal','/business','/en/business',
    '/kids','/en/kids','/teens','/en/teens','/studio','/en/studio',
    '/proof','/en/proof','/projects','/en/projects','/pricing','/en/pricing',
    '/terms','/en/terms','/privacy','/en/privacy','/safety','/en/safety'
]
paths={urlparse(u).path for u in urls}
for path in required_paths:
    checks+=1
    if path not in paths: errors.append(f'missing required path: {path}')

print(f'llms_txt_checks={checks} bytes={len(raw)} links={len(urls)}')
if errors:
    print('LLMS_TXT_AEO_FAIL')
    for e in errors: print('-',e)
    sys.exit(1)
print('LLMS_TXT_AEO_PASS')