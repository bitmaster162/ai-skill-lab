#!/usr/bin/env python3
from pathlib import Path
from datetime import date
from bs4 import BeautifulSoup
import re,sys
ROOT=Path(__file__).resolve().parents[1]
expected_age='https://help.openai.com/en/articles/8313401'
expected_parent='https://help.openai.com/en/articles/12315553-parental-controls-on-chatgpt-faq/'
max_age_days=90
checks=0
for rel in ['deploy/live/safety.html','deploy/live/en/safety.html']:
    p=ROOT/rel; soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
    node=soup.select_one('[data-policy-verified]')
    if not node:
        print(f'YOUTH_POLICY_DATE_MISSING {rel}'); sys.exit(1)
    try: d=date.fromisoformat(node.get('data-policy-verified'))
    except Exception:
        print(f'YOUTH_POLICY_DATE_INVALID {rel}'); sys.exit(1)
    age=(date.today()-d).days
    if age<0 or age>max_age_days:
        print(f'YOUTH_POLICY_STALE {rel} age_days={age} max={max_age_days}'); sys.exit(1)
    checks+=1
    hrefs={a.get('href') for a in soup.find_all('a')}
    for u in [expected_age,expected_parent]:
        if u not in hrefs:
            print(f'YOUTH_POLICY_SOURCE_MISSING {rel} {u}'); sys.exit(1)
        checks+=1
# Source pages must carry the same provenance date and both official source URLs.
for rel in ['app/safety/page.tsx','app/en/safety/page.tsx']:
    text=(ROOT/rel).read_text(encoding='utf-8')
    for token in ['data-policy-verified="2026-08-15"',expected_age,expected_parent]:
        if token not in text:
            print(f'YOUTH_POLICY_SOURCE_PARITY_FAIL {rel} {token}'); sys.exit(1)
        checks+=1
print(f'YOUTH_POLICY_FRESHNESS_PASS checks={checks} verified=2026-08-15 max_age_days={max_age_days}')
