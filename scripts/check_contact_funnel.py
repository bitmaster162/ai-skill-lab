#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
TG='https://t.me/BiTFormer'
README=ROOT/'README.md'
problems=[]; checked=0
# Static: external Telegram href is allowed only on Start pages.
for p in sorted((ROOT/'deploy/live').rglob('*.html')):
    rel=p.relative_to(ROOT/'deploy/live').as_posix()
    text=p.read_text(encoding='utf-8')
    direct=len(re.findall(r'href=["\']https://t\.me/BiTFormer',text))
    checked += 1
    if rel in {'start.html','en/start.html'}:
        if direct < 1: problems.append(f'{rel}: Start page has no direct Telegram exit')
    elif direct:
        problems.append(f'{rel}: {direct} direct Telegram href(s) outside Start')
# Next route pages: direct messenger reference only on Start pages.
for p in sorted((ROOT/'app').rglob('page.tsx')):
    rel=p.relative_to(ROOT).as_posix(); text=p.read_text(encoding='utf-8'); checked += 1
    direct=('site.telegram' in text or TG in text)
    allowed=rel in {'app/start/page.tsx','app/en/start/page.tsx'}
    if direct and not allowed: problems.append(f'{rel}: direct messenger reference outside Start')
# EN route pages must not link to bare RU /start.
for p in sorted((ROOT/'app/en').rglob('page.tsx')):
    text=p.read_text(encoding='utf-8'); checked += 1
    if p.relative_to(ROOT).as_posix() != 'app/en/start/page.tsx' and re.search(r'href=["\']/start["\']',text): problems.append(f'{p.relative_to(ROOT)}: bare /start link on EN page')
# Static EN pages must not link bare /start.
for p in sorted((ROOT/'deploy/live/en').rglob('*.html')):
    text=p.read_text(encoding='utf-8'); checked += 1
    if p.relative_to(ROOT/'deploy/live').as_posix() != 'en/start.html' and re.search(r'href=["\']/start["\']',text): problems.append(f'{p.relative_to(ROOT)}: bare /start link on EN static page')
readme=README.read_text(encoding='utf-8')
checked += 1
if 'All primary contact CTAs open the configured Telegram URL.' in readme:
    problems.append('README: stale direct-Telegram contact-flow claim')
for marker in [
    'Primary contact CTAs route through `/start` / `/en/start`',
    'only those Start pages expose the configured Telegram exit',
]:
    checked += 1
    if marker not in readme:
        problems.append(f'README: required contact-funnel marker missing {marker!r}')
component=ROOT/'components/ContactButtons.tsx'
ct=component.read_text(encoding='utf-8'); checked += 1
if 'site.telegram' in ct or TG in ct: problems.append('components/ContactButtons.tsx: external messenger exit is not allowed')
print(f'contact_funnel_checks={checked}')
if problems:
    for x in problems: print('FAIL:',x)
    sys.exit(1)
print('CONTACT_FUNNEL_PASS')
