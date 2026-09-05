#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
checks=[('components/workshop/WorkshopAudience.tsx', ['Creator: 10 занятий', 'Mini берёт ключевые вводные блоки', 'Studio добавляет 2 занятия']), ('deploy/live/kids.html', ['Creator: 10 занятий', 'Mini берёт ключевые вводные блоки', 'Studio добавляет 2 занятия']), ('components/workshop/WorkshopAudience.tsx', ['Creator: 10 sessions', 'Mini selects the essential introduction', 'Studio adds 2 sessions']), ('deploy/live/en/kids.html', ['Creator: 10 sessions', 'Mini selects the essential introduction', 'Studio adds 2 sessions']), ('components/workshop/WorkshopAudience.tsx', ['Карта из 10 модулей', 'Модули — карта содержания', 'Explorer выбирает ключевые блоки за 6 занятий', 'Portfolio проходит полное ядро за 10', 'Builder добавляет 2 занятия']), ('deploy/live/teens.html', ['Карта из 10 модулей', 'Модули — карта содержания', 'Explorer выбирает ключевые блоки за 6 занятий', 'Portfolio проходит полное ядро за 10', 'Builder добавляет 2 занятия']), ('components/workshop/WorkshopAudience.tsx', ['A 10-module map', 'Modules are a content map', 'Explorer selects the essential blocks in 6 sessions', 'Portfolio covers the full core in 10', 'Builder adds 2 sessions']), ('deploy/live/en/teens.html', ['A 10-module map', 'Modules are a content map', 'Explorer selects the essential blocks in 6 sessions', 'Portfolio covers the full core in 10', 'Builder adds 2 sessions'])]
problems=[]; n=0
for fn,needles in checks:
    text=(ROOT/fn).read_text(encoding='utf-8')
    for x in needles:
        n+=1
        if x not in text: problems.append(f'{fn} missing {x!r}')
if problems:
    print('\n'.join('FAIL: '+p for p in problems)); sys.exit(1)
print(f'curriculum_package_mapping_checks={n} files={len(checks)}')
print('CURRICULUM_PACKAGE_MAPPING_PASS')
