#!/usr/bin/env python3
from pathlib import Path
from bs4 import BeautifulSoup
import re, sys
ROOT=Path(__file__).resolve().parents[1]
checks=0
required={
 'ru':['Что происходит после сообщения в Telegram?','Когда и на каких условиях происходит оплата?'],
 'en':['What happens after I message on Telegram?','When do I pay, and on what terms?'],
}
for lang,static_rel,source_rel in [
 ('ru','deploy/live/faq.html','app/faq/page.tsx'),
 ('en','deploy/live/en/faq.html','app/en/faq/page.tsx')]:
    html=(ROOT/static_rel).read_text(encoding='utf-8')
    soup=BeautifulSoup(html,'html.parser')
    qs=[' '.join(x.get_text(' ',strip=True).replace('+','').split()) for x in soup.select('.faqlist details > summary, .faqList details > summary')]
    src=(ROOT/source_rel).read_text(encoding='utf-8')
    src_qs=re.findall(r'\["([^"]+\?)",\s*"',src)
    if len(qs)!=10 or len(src_qs)!=10:
        print(f'FAQ_COUNT_FAIL {lang} static={len(qs)} source={len(src_qs)}'); sys.exit(1)
    checks+=2
    if qs!=src_qs:
        print(f'FAQ_ORDER_PARITY_FAIL {lang}\nstatic={qs}\nsource={src_qs}'); sys.exit(1)
    checks+=1
    for q in required[lang]:
        if q not in qs:
            print(f'FAQ_REQUIRED_FAIL {lang} {q}'); sys.exit(1)
        checks+=1
print(f'FAQ_PARITY_PASS checks={checks} questions_ru=10 questions_en=10')
