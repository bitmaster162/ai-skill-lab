#!/usr/bin/env python3
"""E3.3 exact action-focused headings, per-route source/static layout and E3.1 baseline seal."""
from __future__ import annotations
from pathlib import Path
import re,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
# Baseline SHA pins prove the ONLY HTML change on each target route is the approved H1.
ROUTES = {'/': {'old': '<h1>Освойте ИИ так, чтобы <em>результат остался у вас.</em></h1>',
       'new': '<h1>Освойте ИИ так, чтобы <em>результат остался у вас.</em></h1>',
       'base_sha256': 'd623a217960abebf2748513daa10c9bace5bb38266216fa7c3979509c8269b52',
       'text': 'Освойте ИИ так, чтобы результат остался у вас.'},
 '/kids': {'old': '<h1>ИИ — не кнопка<br/><em>«сделай за меня».</em></h1>',
           'new': '<h1>Свой проект с ИИ —<br/><em>вместе со взрослым.</em></h1>',
           'base_sha256': '310a1d8f3856da9d4dc506c65db4209cfd0941130b983632cee89fb60c739a8f',
           'text': 'Свой проект с ИИ — вместе со взрослым.'},
 '/en/kids': {'old': '<h1>AI is not a button<br/><em>that does it for you.</em></h1>',
              'new': '<h1>Their own AI project —<br/><em>with an adult alongside.</em></h1>',
              'base_sha256': '60effce7e3ba7f1a6fdb07c2e6eac17a593e0e6a5a6cb04eca7092b32e71d132',
              'text': 'Their own AI project — with an adult alongside.'},
 '/teens': {'old': '<h1>Не просто пользоваться ИИ.<br/><em>Собирать и объяснять.</em></h1>',
            'new': '<h1>Исследовать, писать код<br/><em>и собирать портфолио с ИИ.</em></h1>',
            'base_sha256': '12a3879fe7b0da0bd07d9127450e028628ee93a148f92ea3bac9788763a2c7ce',
            'text': 'Исследовать, писать код и собирать портфолио с ИИ.'},
 '/en/teens': {'old': '<h1>Do more than use AI.<br/><em>Build it. Explain it.</em></h1>',
               'new': '<h1>Research, code<br/><em>and build a portfolio with AI.</em></h1>',
               'base_sha256': '731e2233406f22f9f248fd5dd8719a617e8faff3dc2352fb8622770fdf35bbb8',
               'text': 'Research, code and build a portfolio with AI.'},
 '/personal': {'old': '<h1>Не курс про ИИ,<br/><em>а ваш рабочий процесс.</em></h1>',
               'new': '<h1>ИИ вокруг<br/><em>вашей реальной задачи.</em></h1>',
               'base_sha256': '9a9de0d342f68b6794481ae87c58da9f6dd6e08ee735017d7425acba28f7ec0d',
               'text': 'ИИ вокруг вашей реальной задачи.'},
 '/en/personal': {'old': '<h1>Not a course about AI.<br/><em>Your own working system.</em></h1>',
                  'new': '<h1>AI around<br/><em>your real task.</em></h1>',
                  'base_sha256': 'c6b0d5cab5f8e9d43140824e1cbe438c5b757e73c7944af4b868f2131f9cb704',
                  'text': 'AI around your real task.'},
 '/business': {'old': '<h1>Не «добавить ИИ».<br/><em>Изменить один процесс.</em></h1>',
               'new': '<h1>Обучить команду<br/><em>и проверить ИИ на одном процессе.</em></h1>',
               'base_sha256': 'd1c9140e501ff51a4a38c226c8547a24e0e08ee3c55ca205531df7f0d7c19226',
               'text': 'Обучить команду и проверить ИИ на одном процессе.'},
 '/en/business': {'old': '<h1>Do not add AI.<br/><em>Change one process.</em></h1>',
                  'new': '<h1>Train the team<br/><em>and test AI on one process.</em></h1>',
                  'base_sha256': '14dde7781a2b7c0139997798d12f1918c0ccf190f307068e80488d39ea5ddefb',
                  'text': 'Train the team and test AI on one process.'},
 '/start': {'old': '<h1>Сначала fit.<br><em>Потом программа.</em></h1>',
            'new': '<h1>Начните с бесплатного звонка<br><em>на 15 минут.</em></h1>',
            'base_sha256': '36cd8ce6a8d0475247482613fd8f85fb130d661e3ec21bdef14b116f1c5c25a2',
            'text': 'Начните с бесплатного звонка на 15 минут.'},
 '/en/start': {'old': '<h1>Fit first.<br><em>Program second.</em></h1>',
               'new': '<h1>Start with a free<br><em>15-minute call.</em></h1>',
               'base_sha256': '94c95343366eca03b68373881f9de9e30c55fa74a641a407709dafdaef8f3ea5',
               'text': 'Start with a free 15-minute call.'},
 '/pricing': {'old': '<h1>Знайте цену.<br><em>Фиксируйте scope.</em></h1>',
              'new': '<h1>Цены известны заранее.<br><em>Объём работ — письменно.</em></h1>',
              'base_sha256': '0088810a9f42af504258f20cb04556907e6cd7c093ea707d52e73fcafe95b546',
              'text': 'Цены известны заранее. Объём работ — письменно.'},
 '/en/pricing': {'old': '<h1>Know the price.<br><em>Define the scope.</em></h1>',
                 'new': '<h1>Prices up front.<br><em>Scope in writing.</em></h1>',
                 'base_sha256': '3904198e46277963c95734ad94f042ca3eefa7fac53d650aed0f6032c532ea0d',
                 'text': 'Prices up front. Scope in writing.'},
 '/phuket': {'old': '<h1>Локально на Пхукете.<br><span>И без географии online.</span></h1>',
             'new': '<h1>На Пхукете — очно.<br><span>Из любой страны — онлайн.</span></h1>',
             'base_sha256': 'e7841eaf58936ee109e26b79d8bdf99a67432e2c25227beb7b8aea77233435a1',
             'text': 'На Пхукете — очно. Из любой страны — онлайн.'},
 '/en/phuket': {'old': '<h1>Local in Phuket.<br><span>Borderless online.</span></h1>',
                'new': '<h1>In person on Phuket.<br><span>Online from anywhere.</span></h1>',
                'base_sha256': 'b57a3e3f55fbc804666fd568440f3961c12bcc6602e9868ee312cc14ec85cc39',
                'text': 'In person on Phuket. Online from anywhere.'}}
def normalized(h: str)->str:
 return " ".join(re.sub(r"<[^>]+>"," ",h).split())
import json
release=json.loads((LIVE/"_release.json").read_text(encoding="utf8")).get("release_id")
if release in {"E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1","E3_5_HEADING_STRUCTURE_R1",'E3_6_WORKSHOP_HERO_PANEL_R1','T1_6F2_ADULT_FIRST_TASKS_R1'}:
 from check_e3_2_ru_glossary import EXPECTED as E32_TEXT,visible as E32_VISIBLE
else:E32_TEXT={}
E34_PINS=json.loads((ROOT/"data/e3_4_ru_route_sha_pins.json").read_text(encoding="utf-8"))["routes"] if release in {"E3_4_AI_SAFETY_AUDIENCE_R1","E3_5_HEADING_STRUCTURE_R1",'E3_6_WORKSHOP_HERO_PANEL_R1','T1_6F2_ADULT_FIRST_TASKS_R1'} else {}
E35_PINS=json.loads((ROOT/"data/e3_5_heading_pins.json").read_text(encoding="utf-8")) if release in {'E3_5_HEADING_STRUCTURE_R1','E3_6_WORKSHOP_HERO_PANEL_R1','T1_6F2_ADULT_FIRST_TASKS_R1'} else {}
errors=[]
counts={"ru":0,"en":0,"line_splits":0,"em":0,"span":0,"unchanged_root":0}
for route,scope in ROUTES.items():
 rel="index.html" if route=="/" else route.lstrip("/")+".html"
 path=LIVE/rel
 current=path.read_text(encoding="utf-8")
 h1=re.findall(r"<h1\b[^>]*>[\s\S]*?</h1>",current)
 if len(h1)!=1 or h1[0]!=scope["new"]:
  errors.append(f"{route}: exact H1 markup mismatch")
  continue
 if normalized(h1[0])!=scope["text"]:
  errors.append(f"{route}: exact H1 text mismatch")
 if current.count(scope["new"])!=1:
  errors.append(f"{route}: expected H1 occurs not exactly once")
 if release in {"E3_2_RU_GLOSSARY_R1","E3_4_AI_SAFETY_AUDIENCE_R1","E3_5_HEADING_STRUCTURE_R1",'E3_6_WORKSHOP_HERO_PANEL_R1','T1_6F2_ADULT_FIRST_TASKS_R1'} and not route.startswith("/en/"):
  # E3.2 intentionally replaces RU text outside H1; enforce exact route-level
  # visible SHA from its independently tested glossary contract instead.
  expected=E32_TEXT.get(route,{}).get("text_sha256")
  if route in E34_PINS:
   expected=E34_PINS[route]["visible_sha256"]
  if route in E35_PINS.get("routes",{}):
   expected=E35_PINS["routes"][route]["visible_sha256"]
  actual=hashlib.sha256(E32_VISIBLE(current).encode("utf8")).hexdigest()
  if not expected or actual!=expected:errors.append(f"{route}: E3.2 exact RU visible text SHA mismatch")
 elif release in {'E3_5_HEADING_STRUCTURE_R1','E3_6_WORKSHOP_HERO_PANEL_R1','T1_6F2_ADULT_FIRST_TASKS_R1'} and route=="/en/pricing":
  expected_sha=E35_PINS["assets"]["deploy/live/en/pricing.html"]["accepted_sha256"]
  if hashlib.sha256(current.encode("utf-8")).hexdigest()!=expected_sha:
   errors.append(f"{route}: E3.5 exact EN pricing markup changed")
 elif hashlib.sha256(current.replace(scope["new"],scope["old"],1).encode("utf-8")).hexdigest()!=scope["base_sha256"]:
  errors.append(f"{route}: non-H1 static markup byte drift since E3.1 base")
 lang="en" if route.startswith("/en/") else "ru"
 counts[lang]+=1
 if route=="/":
  counts["unchanged_root"]+=1
  if scope["new"]!=scope["old"]:errors.append("/: already-approved H1 changed")
 else:
  counts["line_splits"]+=h1[0].count("<br")
  if route.endswith("phuket"):counts["span"]+=h1[0].count("<span>")
  else:counts["em"]+=h1[0].count("<em>")
audience=(ROOT/"components/workshop/WorkshopAudience.tsx").read_text(encoding="utf-8")
matched=re.search(r"const headers = (.*?) as const;",audience,re.S)
if not matched:errors.append("source: Audience headers missing")
else:
 data=json.loads(matched.group(1))
 for audience_name,route in [("kids","kids"),("teens","teens"),("adult","personal")]:
  for lang in ["ru","en"]:
   path="/en/"+route if lang=="en" else "/"+route
   parts=data[audience_name][lang]
   if f"<h1>{parts[1]}<br/><em>{parts[2]}</em></h1>" !=ROUTES[path]["new"]:
    errors.append(f"source: Audience {route}/{lang} not equal to static H1")
other={
 "components/workshop/WorkshopBusiness.tsx":['"Train the team"','"and test AI on one process."','"Обучить команду"','"и проверить ИИ на одном процессе."'],
 "components/workshop/WorkshopStart.tsx":['Start with a free<br/><em>15-minute call.</em>','Начните с бесплатного звонка<br/><em>на 15 минут.</em>'],
 "components/workshop/WorkshopPricing.tsx":['Prices up front.<br/><em>Scope in writing.</em>','Цены известны заранее.<br/><em>Объём работ — письменно.</em>'],
 "app/(ru)/phuket/page.tsx":[ROUTES["/phuket"]["new"].replace("<br>","<br/>")],
 "app/(en)/en/phuket/page.tsx":[ROUTES["/en/phuket"]["new"].replace("<br>","<br/>")],
 "components/workshop/WorkshopHome.tsx":["Освойте ИИ так, чтобы <em>результат остался у вас.</em>"],
}
for rel,tokens in other.items():
 source=(ROOT/rel).read_text(encoding="utf-8")
 for token in tokens:
  if token not in source:errors.append(f"source missing {rel} token {token}")
if counts!={"ru":8,"en":7,"line_splits":14,"em":12,"span":2,"unchanged_root":1}:
 errors.append(f"heading structural counts {counts}")
print(f"E3_3_H1_CHECK routes={len(ROUTES)} ru={counts['ru']} en={counts['en']} two_line={counts['line_splits']} italic={counts['em']} span={counts['span']} protected_html_baselines=15")
if errors:
 print("E3_3_H1_FAIL")
 for x in errors:print("- "+x)
 sys.exit(1)
print("E3_3_H1_PASS")
