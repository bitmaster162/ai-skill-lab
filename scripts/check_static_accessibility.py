#!/usr/bin/env python3
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'

class Audit(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.h1=0; self.lang=None; self.has_main=False; self.has_skip=False; self.links=[]; self.buttons=[]; self._link=None; self._button=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='html': self.lang=a.get('lang')
        if tag=='h1': self.h1+=1
        if tag=='main': self.has_main=True
        if a.get('id'): self.ids.append(a['id'])
        if tag=='a':
            self._link={'href':a.get('href',''),'text':'','aria':a.get('aria-label',''),'target':a.get('target'),'rel':a.get('rel',''),'class':a.get('class','')}; self.links.append(self._link)
            if 'skip' in a.get('class','') and a.get('href')=='#main': self.has_skip=True
        if tag=='button':
            self._button={'text':'','aria':a.get('aria-label',''),'class':a.get('class',''),'live':a.get('aria-live','')}; self.buttons.append(self._button)
    def handle_endtag(self, tag):
        if tag=='a': self._link=None
        if tag=='button': self._button=None
    def handle_data(self, data):
        if self._link is not None: self._link['text']+=data
        if self._button is not None: self._button['text']+=data

errors=[]; checks=0; pages=0
for p in sorted(LIVE.rglob('*.html')):
    pages += 1
    rel=p.relative_to(LIVE).as_posix()
    a=Audit(); a.feed(p.read_text(encoding='utf-8'))
    checks += 1
    if a.lang not in {'ru','en'}: errors.append(f'{rel}: invalid/missing html lang {a.lang!r}')
    if rel!='404.html':
        checks += 3
        if a.h1 != 1: errors.append(f'{rel}: h1 count={a.h1}, expected 1')
        if not a.has_main: errors.append(f'{rel}: missing main')
        if not a.has_skip: errors.append(f'{rel}: missing skip link to #main')
    dup=[x for x,n in Counter(a.ids).items() if n>1]
    checks += 1
    if dup: errors.append(f'{rel}: duplicate ids {dup}')
    for link in a.links:
        checks += 1
        if not (link['text'].strip() or link['aria'].strip()): errors.append(f"{rel}: empty link {link['href']}")
        if link['target']=='_blank':
            checks += 1
            if 'noopener' not in link['rel']: errors.append(f"{rel}: target=_blank without noopener {link['href']}")
    for button in a.buttons:
        checks += 1
        if not (button['text'].strip() or button['aria'].strip()): errors.append(f'{rel}: empty button')
        if 'briefCopy' in button['class']:
            checks += 1
            if button['live'] != 'polite': errors.append(f'{rel}: briefCopy must use aria-live=polite')

css=(LIVE/'style.css').read_text(encoding='utf-8')
for marker in [':focus-visible{outline:3px solid #4f8cff', '@media(prefers-reduced-motion:reduce)', 'min-height:48px']:
    checks += 1
    if marker not in css: errors.append(f'style.css: missing accessibility marker {marker}')

print(f'accessibility_checks={checks} pages={pages}')
if errors:
    for e in errors: print('FAIL:',e)
    sys.exit(1)
print('STATIC_ACCESSIBILITY_PASS')
