#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import sys
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy/live'
problems=[]; checks=0
telegram_words=('telegram',)
for p in sorted(LIVE.rglob('*.html')):
    soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    for a in soup.find_all('a', href=True):
        href=a.get('href','').strip()
        text=' '.join(a.stripped_strings).strip().lower()
        if any(w in text for w in telegram_words):
            checks+=1
            if not href.startswith('https://t.me/'):
                problems.append(f'{p.relative_to(ROOT)} labels Telegram but href={href!r}: {text!r}')
        if href in ('/start','/en/start'):
            checks+=1
            if 'message on telegram' in text or 'написать в telegram' in text or 'open telegram' in text or 'открыть telegram' in text:
                problems.append(f'{p.relative_to(ROOT)} internal Start CTA masquerades as direct Telegram: {text!r}')
# Start pages must still expose one direct Telegram action.
for rel in ('deploy/live/start.html','deploy/live/en/start.html'):
    soup=BeautifulSoup((ROOT/rel).read_text(encoding='utf-8'),'html.parser')
    direct=[a for a in soup.find_all('a',href=True) if a['href'].startswith('https://t.me/')]
    checks+=1
    if not direct: problems.append(f'{rel} missing direct Telegram action')
if problems:
    for x in problems: print('FAIL:',x)
    sys.exit(1)
print(f'cta_semantics_checks={checks}')
print('CTA_SEMANTICS_PASS')
