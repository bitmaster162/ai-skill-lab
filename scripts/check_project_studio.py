#!/usr/bin/env python3
from pathlib import Path
import json
from source_paths import source_path
import re, sys, html
ROOT=Path(__file__).resolve().parents[1]
E32 = json.loads((ROOT / "deploy/live/_release.json").read_text(encoding="utf-8")).get("release_id") == "E3_2_RU_GLOSSARY_R1"
errors=[]; checks=0
source=(ROOT/'components/ProjectStudio.tsx').read_text(encoding='utf-8')
ru_page=source_path(ROOT,'app/projects/page.tsx').read_text(encoding='utf-8')
en_page=source_path(ROOT,'app/en/projects/page.tsx').read_text(encoding='utf-8')
ru_static=html.unescape((ROOT/'deploy/live/projects.html').read_text(encoding='utf-8'))
en_static=html.unescape((ROOT/'deploy/live/en/projects.html').read_text(encoding='utf-8'))

titles_ru=['Детектив фактов','Мир и персонаж','Мини-игра','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules']
if E32:
    titles_ru = ['Детектив фактов','Мир и персонаж','Мини-игра','Система исследования',
                 'Прототип ИИ-помощника','Мини-продукт','Личный исследовательский процесс',
                 'Прототип рабочего процесса','Правила работы с ИИ']
titles_en=['Fact detective' ,'World & character','Mini game','Research OS','AI assistant prototype','Mini-product','Personal research workflow','Process prototype','AI operating rules']
for label,text,titles in [('source',source,titles_ru+titles_en),('static RU',ru_static,titles_ru),('static EN',en_static,titles_en)]:
    for title in titles:
        checks+=1
        if title not in text: errors.append(f'{label}: missing project {title!r}')
for label,text in [('page RU',ru_page),('page EN',en_page),('static RU',ru_static),('static EN',en_static)]:
    for marker in ['Project Studio','EXAMPLE OUTPUTS · NOT TESTIMONIALS']:
        checks+=1
        required = ('ПРИМЕРЫ РЕЗУЛЬТАТОВ · НЕ ОТЗЫВЫ' if E32 and label in ('page RU','static RU') and marker == 'EXAMPLE OUTPUTS · NOT TESTIMONIALS' else marker)
        if required not in text: errors.append(f'{label}: missing {required!r}')
for marker in ['goal','ai','human','artifact','data-project-tags','research','create','build','automate']:
    checks+=1
    if marker.lower() not in source.lower(): errors.append(f'source component: missing {marker!r}')
for label,text in [('static RU',ru_static),('static EN',en_static)]:
    checks+=1
    if text.count('data-project-tags=') != 9: errors.append(f'{label}: expected 9 project cards')
    checks+=1
    if text.count('data-project-filter=') != 5: errors.append(f'{label}: expected 5 filter buttons')
    for marker in ['data-project-studio','project-filter-status','data-project-filter','data-project-tags','<noscript>']:
        checks+=1
        if marker not in text: errors.append(f'{label}: missing {marker!r}')
for label,text,phrases in [
    ('RU',ru_page+ru_static,['не заявления о конкретных клиентах или учениках','ничего не отправляет']),
    ('EN',en_page+en_static,['not claims about specific clients or learners','sends nothing out'])
]:
    for phrase in phrases:
        checks+=1
        if phrase.lower() not in text.lower(): errors.append(f'{label}: missing honesty marker {phrase!r}')
for bad in ['client success story','реальный клиентский кейс','guaranteed outcome','гарантированный результат']:
    checks+=1
    if bad.lower() in (source+ru_page+en_page+ru_static+en_static).lower(): errors.append(f'forbidden claim: {bad}')
if errors:
    print(f'project_studio_checks={checks}')
    [print('FAIL:',e) for e in errors]
    sys.exit(1)
print(f'project_studio_checks={checks} cards=9 filters=5 surfaces=5')
print('PROJECT_STUDIO_PARITY_PASS')
