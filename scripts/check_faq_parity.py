#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
import re, sys
ROOT=Path(__file__).resolve().parents[1]

class FAQParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_summary=False; self.in_p=False; self.summary=[]; self.answer=[]; self.items=[]
    def handle_starttag(self, tag, attrs):
        if tag=='summary': self.in_summary=True; self.summary=[]
        elif tag=='p': self.in_p=True; self.answer=[]
    def handle_endtag(self, tag):
        if tag=='summary': self.in_summary=False
        elif tag=='p':
            self.in_p=False
            if self.summary:
                q=' '.join(''.join(self.summary).replace('+','').split())
                a=' '.join(''.join(self.answer).split())
                self.items.append((q,a)); self.summary=[]; self.answer=[]
    def handle_data(self, data):
        if self.in_summary: self.summary.append(data)
        elif self.in_p: self.answer.append(data)

def source_items(text):
    return re.findall(r'\["([^"]+\?)",\s*"([^"]*)"\]', text)

required={
 'ru':['Что происходит после сообщения в Telegram?','Когда и на каких условиях происходит оплата?','Сколько длится одно занятие?'],
 'en':['What happens after I message on Telegram?','When do I pay, and on what terms?','How long is one session?'],
}
checks=0
for lang,static_rel,source_rel in [
 ('ru','deploy/live/faq.html','app/faq/page.tsx'),
 ('en','deploy/live/en/faq.html','app/en/faq/page.tsx')]:
    parser=FAQParser(); parser.feed((ROOT/static_rel).read_text(encoding='utf-8'))
    static_items=parser.items
    source=source_items((ROOT/source_rel).read_text(encoding='utf-8'))
    if len(static_items)!=11 or len(source)!=11:
        print(f'FAQ_COUNT_FAIL {lang} static={len(static_items)} source={len(source)}'); sys.exit(1)
    checks+=2
    if static_items!=source:
        print(f'FAQ_CONTENT_PARITY_FAIL {lang}\nstatic={static_items}\nsource={source}'); sys.exit(1)
    checks+=1
    qs=[q for q,_ in static_items]
    for q in required[lang]:
        if q not in qs:
            print(f'FAQ_REQUIRED_FAIL {lang} {q}'); sys.exit(1)
        checks+=1
print(f'FAQ_PARITY_PASS checks={checks} questions_ru=11 questions_en=11')
