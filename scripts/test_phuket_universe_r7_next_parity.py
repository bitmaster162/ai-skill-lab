#!/usr/bin/env python3
"""Compare Next's 56 prerendered route semantics against local R7 HTML preview."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/phuket_universe_u3'))
from preview import need
from build_phuket_universe_r7 import ROOT,render

sys.stdout.reconfigure(encoding="utf-8")
NEXT=ROOT/".next/server/app"

class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[];self.teasers=0;self.h1=0;self.html_lang=""
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t=="html":self.html_lang=a.get("lang","")
        if t=="h1":self.h1+=1
        if "data-u3-universe-teaser" in a:self.teasers+=1
        if t=="a" and "data-universe-event" in a:self.links.append(a)

def data(markup: bytes) -> DOM:
    p=DOM();p.feed(markup.decode("utf-8"));p.close();return p

def main():
    files=render()
    routes=[k for k in files if k.endswith(".html") and k!="404.html"]
    need(len(routes)==56,"Next parity route count")
    for k in sorted(routes):
        target=NEXT/k
        need(target.is_file(),"Next route missing: "+k)
        a=data(files[k]);b=data(target.read_bytes())
        loc="en" if k.startswith("en/") or k=="en.html" else "ru"
        expected="/en/phuket-universe" if loc=="en" else "/phuket-universe"
        for desc,d in [("static",a),("next",b)]:
            universe=[x for x in d.links if x["data-universe-event"]=="universe_click"]
            project=[x for x in d.links if x["data-universe-event"]=="project_click"]
            need(len(universe)==1 and universe[0].get("href")==expected,
                 f"{k}: {desc} U3 footer link mismatch")
            need(len(project)==(5 if k in ("phuket-universe.html","en/phuket-universe.html") else 0),
                 f"{k}: {desc} project markers mismatch")
            need(d.teasers==(1 if k in ("phuket.html","en/phuket.html") else 0),
                 f"{k}: {desc} teaser mismatch")
            need(d.h1==1 and d.html_lang==loc,f"{k}: {desc} semantic mismatch")
        need([(x["data-universe-event"],x["href"]) for x in a.links] ==
             [(x["data-universe-event"],x["href"]) for x in b.links],
             "Next/static event mapping mismatch: "+k)
    print("U3_NEXT_STATIC_SEMANTIC_PARITY_PASS routes=56 ru=28 en=28",flush=True)
if __name__=="__main__":main()
