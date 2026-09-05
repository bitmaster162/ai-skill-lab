#!/usr/bin/env python3
"""R98: source/static audience, business and FAQ release contracts."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy/live'
errors = []
checks = 0

def require(condition, message):
    global checks
    checks += 1
    if not condition:
        errors.append(message)

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hrefs = []; self.ids = []; self.text = []; self.inputs = []
        self.h1 = 0; self.forms = 0; self.details = 0; self.skip = 0
        self.canonical = []; self.alternates = {}; self.styles = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script', 'style'): self.skip += 1
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'a': self.hrefs.append(a.get('href', ''))
        if tag == 'input': self.inputs.append(a)
        if tag == 'h1': self.h1 += 1
        if tag == 'form': self.forms += 1
        if tag == 'details': self.details += 1
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a.get('href'))
        if tag == 'link' and a.get('rel') == 'alternate': self.alternates[a.get('hreflang')] = a.get('href')
        if tag == 'link' and a.get('rel') == 'stylesheet': self.styles.append(a.get('href'))
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.text.append(data)

facts = json.loads(read('data/commercial_facts.json'))
source = read('components/workshop/WorkshopAudience.tsx')
match = re.search(r'const programs = (.*?) as const;', source, re.S)
require(bool(match), 'Audience program authority missing')
programs = json.loads(match[1]) if match else {}
require(set(programs) == {'adult', 'teens', 'kids'}, 'Audience track set')
for track, count in [('adult', 5), ('teens', 10), ('kids', 10)]:
    for locale in ('ru', 'en'):
        require(len(programs.get(track, {}).get(locale, [])) == count, f'{track}/{locale} curriculum count')
for token in ('commercialFacts.tracks[audience]', 'sessionDurationMinutes', 'plans.map', 'href={p("/start")}', 'href={p("/safety")}', 'href={p("/parents")}', 'href={p("/family")}'):
    require(token in source, f'Audience contract: {token}')
origin = 'https://ai-skill-lab.vercel.app'
for locale, prefix in [('ru', ''), ('en', 'en/')]:
    for route in ('personal', 'teens', 'kids', 'business', 'faq'):
        rel = f'deploy/live/{prefix}{route}.html'
        html = read(rel); page = Page(); page.feed(html)
        visible = ' '.join(' '.join(page.text).split())
        mount = read(f'app/{prefix}{route}/page.tsx')
        component = 'WorkshopBusiness' if route == 'business' else 'WorkshopFaq' if route == 'faq' else 'WorkshopAudience'
        require(f'<{component} ' in mount and f'locale="{locale}"' in mount, f'{rel}: source mount')
        require(page.h1 == 1 and page.forms == 0, f'{rel}: heading/form boundary')
        require('main' in page.ids and len(page.ids) == len(set(page.ids)), f'{rel}: unique IDs')
        require(page.styles == ['/workshop.css'], f'{rel}: shared CSS')
        require(page.canonical == [origin + '/' + prefix + route], f'{rel}: canonical')
        require(page.alternates == {'ru': origin+'/'+route, 'en': origin+'/en/'+route, 'x-default': origin+'/'+route}, f'{rel}: alternates')
        require(all(not urlsplit(h).scheme and not h.startswith('//') for h in page.hrefs), f'{rel}: external anchor')
        start = '/' + prefix + 'start' + ('#business-brief' if route == 'business' else '')
        require(start in page.hrefs, f'{rel}: Start route')
        require('<header class="workshopHeader">' in html and html.count('data-lab-command-open') == 1, f'{rel}: Workshop navigation')
        for marker in ('fonts.googleapis.com','fonts.gstatic.com','support.js','x-dc','sc-for','sc-if','href="#"','[response time]'):
            require(marker not in html, f'{rel}: forbidden {marker}')
        if route in ('personal','teens','kids'):
            track = 'adult' if route == 'personal' else route
            require(f'audience="{track}"' in mount, f'{rel}: exact audience')
            for plan in facts['tracks'][track]:
                require(all(str(plan[k]) in visible for k in ('name','price',f'sessions_{locale}')), f'{rel}: {plan["name"]} facts')
            require(('60 минут' if locale == 'ru' else '60 minutes') in visible, f'{rel}: duration')
            for _, title, body in programs.get(track, {}).get(locale, []):
                require(title in visible and body in visible, f'{rel}: curriculum {title}')
        if route in ('kids','teens'):
            require('/'+prefix+'safety' in page.hrefs and '/'+prefix+'parents' in page.hrefs, f'{rel}: safety/parents')
            require(('организационный контакт' if locale == 'ru' else 'organizational contact') in visible.lower(), f'{rel}: adult contact')
            require(('младше 13' if locale == 'ru' else 'under 13') in visible if route == 'kids' else ('13–17' in visible), f'{rel}: age boundary')
        if route == 'faq':
            require(page.details == 11, f'{rel}: 11 disclosures')
            question = 'Что происходит после первого сообщения?' if locale == 'ru' else 'What happens after my first message?'
            require(question in visible, f'{rel}: neutral contact question')
        if route == 'business':
            require('data-pilot-simulator' in html and html.count('data-pilot-key=') == 4, f'{rel}: simulator')
            require('data-business-value' in html and html.count('id="r98-business-calculator"') == 1, f'{rel}: calculator runtime')
            require({i.get('id') for i in page.inputs} == {'bv-team','bv-hours','bv-rate','bv-recoverable'}, f'{rel}: four calculator inputs')
            require(all('disabled' in i for i in page.inputs) and '<noscript>' in html, f'{rel}: no-JS boundary')
            for value in ('$890','$390','$1,560','$4,900','$490','$890','35','Ship','Revise','Stop'):
                require(value in visible, f'{rel}: business authority {value}')
            require('сценарий' in visible.lower() if locale == 'ru' else 'scenario' in visible.lower(), f'{rel}: sensitivity disclaimer')

for file in ('WorkshopAudience.tsx','WorkshopBusiness.tsx','WorkshopFaq.tsx'):
    text = read('components/workshop/'+file)
    require('<WorkshopShell ' in text, f'{file}: shared shell')
    for marker in ('t.me/','wa.me/','line.me/','mailto:','tel:','<form','[response time]'):
        require(marker not in text, f'{file}: forbidden {marker}')
calc = read('components/BusinessValueCalculator.tsx')
require('href={startHref}' in calc and '/start#business-brief' in calc and 't.me/' not in calc, 'Calculator internal CTA')
require('data-bv-brief' in calc and 'useSyncExternalStore' in calc, 'Calculator brief/hydration')
all_pages = list(LIVE.rglob('*.html'))
require(len(all_pages) == 47, '47 HTML files')
require(sum('class="workshopHeader"' in p.read_text(encoding='utf-8') for p in all_pages) == 18, '18 Workshop pages')
manifest = json.loads(read('deploy/live/_release.json'))
require(manifest.get('release_id') == 'R98_D3', 'R98_D3 release identity')
require(manifest.get('file_count') == 62, '62 release files')
require(manifest.get('schema') == 'ai-skill-lab.static-release.v1', 'Release schema')

def luminance(value):
    channels = [int(value[i:i+2],16)/255 for i in (1,3,5)]
    linear = [x/12.92 if x <= .04045 else ((x+.055)/1.055)**2.4 for x in channels]
    return sum(x*w for x,w in zip(linear,(.2126,.7152,.0722)))

css_paths = ('components/workshop/WorkshopShell.module.css','deploy/live/workshop.css')
for color in ('#8ab4ff','#5ee0c0','#c9a3ff','#f5f7f9'):
    contrast = (luminance(color)+.05)/(luminance('#0b0d10')+.05)
    require(contrast >= 4.5, f'Audience contrast {color}')
for rel in css_paths:
    css = read(rel)
    for token in ('.audienceHero{','.lessonGrid{','.audiencePrices{','.faqList', '#8ab4ff','#5ee0c0','#c9a3ff'):
        require(token in css, f'{rel}: {token}')
    for token in ('@import','fonts.googleapis.com','fonts.gstatic.com','box-shadow','translateY(','scale('):
        require(token not in css, f'{rel}: forbidden {token}')
workflow = read('.github/workflows/static-qa.yml')
for command in ('python scripts/check_workshop_d3.py','node scripts/check_business_calculator_runtime.mjs'):
    require(workflow.count(command) == 1, f'Workflow command {command}')
print(f'workshop_d3_checks={checks} target_routes=10 public_routes=46 workshop_pages=18')
if errors:
    print('\n'.join('FAIL: '+error for error in errors)); sys.exit(1)
print('WORKSHOP_D3_PASS')
