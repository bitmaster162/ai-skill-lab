#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
required={
 'deploy/live/kids.html':['младше 13','взаимодействие с сервисом проводит взрослый','href="/safety"'],
 'deploy/live/en/kids.html':['under 13','actual interaction','href="/en/safety"'],
 'deploy/live/teens.html':['13–17','ChatGPT пользователям младше 18 требуется разрешение родителя или законного представителя','href="/safety"'],
 'deploy/live/en/teens.html':['AGES 13–17','ChatGPT users under 18 require permission from a parent or legal guardian','href="/en/safety"'],
 'app/kids/page.tsx':['младше 13','фактическое взаимодействие','href="/safety"'],
 'app/en/kids/page.tsx':['under 13','actual interaction','href="/en/safety"'],
 'app/teens/page.tsx':['13–17','ChatGPT пользователям младше 18 требуется разрешение родителя или законного представителя','href="/safety"'],
 'app/en/teens/page.tsx':['Ages 13–17','ChatGPT users under 18 require permission from a parent or legal guardian','href="/en/safety"'],
}
checks=0
for rel,needles in required.items():
    text=(ROOT/rel).read_text(encoding='utf-8')
    for n in needles:
        if n not in text:
            print(f'YOUTH_ROUTE_PARITY_FAIL {rel}: missing {n}'); sys.exit(1)
        checks+=1
print(f'YOUTH_ROUTE_PARITY_PASS checks={checks} routes=8')
