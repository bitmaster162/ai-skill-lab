#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy/live'
RU_MSG='Заявка отправлена. Ответим в течение 1–2 рабочих дней.'
EN_MSG='Application sent. We reply within 1–2 business days.'
TG='https://t.me/BiTFormer'
errors=[]
checks=0

def req(ok: bool, message: str) -> None:
    global checks
    checks += 1
    if not ok:
        errors.append(message)

src=(ROOT/'components/LeadForm.tsx').read_text(encoding='utf-8')
for marker in [RU_MSG,EN_MSG,'data-lead-success-actions','Записаться на диагностику','Book diagnostic','Написать в Telegram','Message on Telegram','href={site.telegram}','start#contact-channels']:
    req(marker in src,f'source LeadForm missing {marker!r}')

js=(LIVE/'start-brief.js').read_text(encoding='utf-8')
for marker in [RU_MSG,EN_MSG,'[data-lead-success-actions]','successActions.hidden=true','successActions.hidden=false']:
    req(marker in js,f'static runtime missing {marker!r}')
req(js.count('fetch(')==1,f'static runtime fetch count={js.count("fetch(")} expected 1')

for rel,en in [('start.html',False),('en/start.html',True)]:
    raw=(LIVE/rel).read_text(encoding='utf-8')
    label='Book diagnostic' if en else 'Записаться на диагностику'
    telegram='Message on Telegram' if en else 'Написать в Telegram'
    req(raw.count('data-lead-success-actions')==1,f'{rel}: success action container count')
    match=re.search(r'<div class="formSuccessActions" data-lead-success-actions hidden>(.*?)</div>',raw,re.S)
    req(bool(match),f'{rel}: hidden success action block missing')
    block=match.group(1) if match else ''
    req(f'href="#contact-channels">{label}</a>' in block,f'{rel}: diagnostic continuation missing')
    req(f'href="{TG}" target="_blank" rel="noopener noreferrer">{telegram}</a>' in block,f'{rel}: Telegram continuation missing')
    req('cal.com' not in block,f'{rel}: success block must not mislabel Cal.com')
    req(raw.count('data-lead-message')==1,f'{rel}: lead message hook count')

for rel in ['app/globals.css','deploy/live/workshop.css']:
    css=(ROOT/rel).read_text(encoding='utf-8')
    req('.formSuccessActions' in css,f'{rel}: success action CSS missing')
    req('.formSuccessActions[hidden]' in css,f'{rel}: hidden contract missing')

print(f'E1_3_POST_SUBMIT_CHECK checks={checks} routes=2')
if errors:
    print('E1_3_POST_SUBMIT_FAIL')
    for error in errors:
        print('-',error)
    sys.exit(1)
print('E1_3_POST_SUBMIT_PASS')
