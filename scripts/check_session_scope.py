#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
scan=[*ROOT.joinpath('app').rglob('*.tsx'),*ROOT.joinpath('deploy/live').rglob('*.html')]
forbidden=re.compile(r'\b(?:\d{2,3}\s*[–-]\s*\d{2,3}|\d{2,3})\s*(?:минут|minutes)\b',re.I)
hits=[]
for p in scan:
    text=p.read_text(encoding='utf-8')
    for m in forbidden.finditer(text):
        hits.append(f'{p.relative_to(ROOT)}: {m.group(0)}')
if hits:
    print('SESSION_DURATION_POLICY_FAIL forbidden fixed-duration claims:')
    print('\n'.join(hits)); sys.exit(1)
required={
 'deploy/live/pricing.html':['точная длительность одной сессии','до оплаты'],
 'deploy/live/en/pricing.html':['exact duration of each session','before payment'],
 'deploy/live/faq.html':['Сколько длится одно занятие?','Точная длительность одной сессии'],
 'deploy/live/en/faq.html':['How long is one session?','exact duration of each session'],
 'app/kids/page.tsx':['Длительность по scope','Фиксируем до оплаты'],
 'app/en/kids/page.tsx':['Session duration, schedule and pace are agreed before payment'],
}
checks=0
for rel,needles in required.items():
    text=(ROOT/rel).read_text(encoding='utf-8')
    for n in needles:
        if n not in text:
            print(f'SESSION_DURATION_REQUIRED_FAIL {rel}: {n}'); sys.exit(1)
        checks+=1
print(f'SESSION_DURATION_POLICY_PASS checks={checks} fixed_duration_claims=0')
