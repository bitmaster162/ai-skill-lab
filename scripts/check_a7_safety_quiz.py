#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
SOURCE=ROOT/"components/SafetyMiniCheck.tsx"
SCRIPT=LIVE/"safety-quiz.js"

RU_MARKERS=[
    "МИНИ-ТЕСТ · ТОЛЬКО В БРАУЗЕРЕ",
    "Совпадают ли эти пять правил с вашим пониманием?",
    "Ничего не отправляется и не сохраняется.",
    "Если ChatGPT используется с ребёнком младше 13 лет",
    "Что требуется пользователю 13–18 лет",
    "Кто ведёт заявку, расписание, оплату",
    "Что не нужно вводить в AI-задания без необходимости?",
    "Что делать, если AI отвечает уверенно?",
    "Проверить ответы",
]
EN_MARKERS=[
    "MINI-CHECK · LOCAL ONLY",
    "Do these five safety rules match your understanding?",
    "Nothing is sent or stored.",
    "If ChatGPT is used with a child under 13",
    "What do users ages 13–18 need",
    "Who handles applications, scheduling, payment",
    "What should not be entered into AI assignments unless genuinely needed?",
    "What should you do when AI sounds confident?",
    "Check answers",
]
FORBIDDEN_JS=("fetch(","XMLHttpRequest","WebSocket","sendBeacon","localStorage","sessionStorage","indexedDB")
errors=[]; checks=0

def req(ok,msg):
    global checks
    checks+=1
    if not ok: errors.append(msg)

class QuizParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.quiz=0; self.questions=0; self.correct=[]; self.radios=0; self.buttons=0; self.results=0; self.script=False
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if "data-safety-quiz" in d: self.quiz+=1
        if "data-safety-question" in d:
            self.questions+=1; self.correct.append(d.get("data-correct"))
        if tag=="input" and d.get("type")=="radio": self.radios+=1
        if "data-safety-check" in d: self.buttons+=1
        if "data-safety-result" in d: self.results+=1
        if tag=="script" and d.get("src")=="/safety-quiz.js": self.script=True

source=SOURCE.read_text(encoding="utf-8")
for marker in RU_MARKERS+EN_MARKERS:
    req(marker in source,f"source missing {marker!r}")
req(source.count('id: "')==10,"source must define 10 localized question rows")
req('fetch(' not in source,"source quiz must not call fetch")
req("localStorage" not in source and "sessionStorage" not in source,"source quiz must not use browser storage")
req("not a safety certification" in source and "не является сертификатом безопасности" in source,"source must disclaim certification")

for rel,markers in [("safety.html",RU_MARKERS),("en/safety.html",EN_MARKERS)]:
    raw=(LIVE/rel).read_text(encoding="utf-8")
    p=QuizParser(); p.feed(raw)
    req(p.quiz==1,f"{rel}: quiz count={p.quiz}")
    req('class="notice safetyQuiz"' in raw,f"{rel}: Workshop notice reuse missing")
    req('class="btn ghost" type="button" data-safety-check' in raw,f"{rel}: Workshop button reuse missing")
    req(p.questions==5,f"{rel}: question count={p.questions}")
    req(p.correct==["a","a","a","a","b"],f"{rel}: correct sequence={p.correct}")
    req(p.radios==10,f"{rel}: radio count={p.radios}")
    req(p.buttons==1,f"{rel}: check button count={p.buttons}")
    req(p.results==1,f"{rel}: result count={p.results}")
    req(p.script,f"{rel}: safety-quiz.js missing")
    for marker in markers:
        req(marker in raw,f"{rel}: missing {marker!r}")
    req("safety certification" in raw or "сертификатом безопасности" in raw,f"{rel}: certification disclaimer missing")

js=SCRIPT.read_text(encoding="utf-8")
for term in FORBIDDEN_JS:
    req(term not in js,f"safety-quiz.js forbidden capability {term}")
for marker in ["data-safety-quiz","data-safety-question","data-safety-result","data-safety-check","5/5"]:
    req(marker in js,f"safety-quiz.js missing {marker}")
req(js.count("addEventListener")==1,"safety-quiz.js must have one event listener site")
req(SCRIPT.stat().st_size<=1800,f"safety-quiz.js too large: {SCRIPT.stat().st_size}")

for rel in ["app/globals.css","deploy/live/workshop.css"]:
    css=(ROOT/rel).read_text(encoding="utf-8")
    req("A7_SAFETY_QUIZ_R1" in css,f"{rel}: A7 marker missing")
    req(".safetyQuiz{margin:38px 0}" in css and ".safetyQuiz fieldset{min-width:0;margin:12px 0;padding:14px}" in css,f"{rel}: minimal quiz CSS contract missing")

print(f"A7_SAFETY_QUIZ_CHECK checks={checks} source=1 static=2 questions=5 script_bytes={SCRIPT.stat().st_size}")
if errors:
    print("A7_SAFETY_QUIZ_FAIL")
    for e in errors: print("-",e)
    sys.exit(1)
print("A7_SAFETY_QUIZ_PASS")
