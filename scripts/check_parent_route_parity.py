#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
checks={
 'app/parents/page.tsx':['FOR PARENTS · 8–18','Сам формулирует цель','Проверяет утверждения','Объясняет, что сделал сам','Защищает финальный проект','Что покупает семья','Возрастные правила','Форматы 8–13','Форматы 14–18','Family Concierge','Возраст + интерес + цель'],
 'deploy/live/parents.html':['FOR PARENTS · 8–18','Сам формулирует цель','Проверяет утверждения','Объясняет, что сделал сам','Защищает финальный проект','Что покупает семья','ChatGPT и возраст','Форматы 8–13','Форматы 14–18','Family Concierge','Возраст + интерес + цель'],
 'app/en/parents/page.tsx':['FOR PARENTS · 8–18','Defines the goal','Checks claims','Explains personal contribution','Defends the final project','What the family buys','Age rules','Formats 8–13','Formats 14–18','Family Concierge','Age + interest + goal'],
 'deploy/live/en/parents.html':['FOR PARENTS · 8–18','Defines the goal','Checks claims','Explains personal contribution','Defends the final project','What the family buys','ChatGPT and age','Formats 8–13','Formats 14–18','Family Concierge','Age + interest + goal'],
}
problems=[]; count=0
for rel,needles in checks.items():
    text=(ROOT/rel).read_text(encoding='utf-8')
    for n in needles:
        count+=1
        if n not in text: problems.append(f'{rel} missing {n!r}')
if problems:
    for p in problems: print('FAIL:',p)
    sys.exit(1)
print(f'parent_route_parity_checks={count} surfaces={len(checks)}')
print('PARENT_ROUTE_PARITY_PASS')
