#!/usr/bin/env python3
"""U3 offline browser acceptance; 24 cases, no external network or API POST."""
import json,mimetypes,sys
from pathlib import Path
from urllib.parse import urlsplit, unquote
import psutil
from playwright.sync_api import sync_playwright
from preview import render, ROOT, need

sys.stdout.reconfigure(encoding="utf-8")
need(psutil.virtual_memory().available > 2*1024**3, "STOP resource floor")
files,meta=render()
v=json.loads(files["vercel.json"])
headers={h["key"]:h["value"] for row in v["headers"] if row.get("source")=="/(.*)" for h in row["headers"]}
csp=headers.get("Content-Security-Policy")
need(csp and "style-src 'self'" in csp and "font-src 'self'" in csp, "CSP must not weaken")
chrome=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
routes=(("/","index.html"),("/phuket","phuket.html"),("/phuket-universe","phuket-universe.html"),
        ("/en","en.html"),("/en/phuket","en/phuket.html"),
        ("/en/phuket-universe","en/phuket-universe.html"))
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=chrome,headless=True,timeout=22000,
        args=["--disable-background-networking","--disable-component-update","--no-first-run"])
    try:
        for route,_ in routes:
            locale="en" if route=="/en" or route.startswith("/en/") else "ru"
            expected="/en/phuket-universe" if locale=="en" else "/phuket-universe"
            for js in (False,True):
                for width in (390,1440):
                    ctx=browser.new_context(java_script_enabled=js,offline=True,
                        viewport={"width":width,"height":844 if width==390 else 900},
                        service_workers="block")
                    page=ctx.new_page();unexpected=[];errors=[];events=[]
                    page.on("pageerror",lambda e:errors.append(str(e)))
                    def fulfill(req):
                        u=urlsplit(req.request.url)
                        if u.scheme!="https" or u.netloc!="aiskillab.work" or req.request.method!="GET":
                            unexpected.append(req.request.url)
                            req.abort();return
                        if u.path=="/_vercel/insights/script.js":
                            req.fulfill(status=200,body="/* local analytics stub */",content_type="text/javascript")
                            return
                        k=unquote(u.path).lstrip("/") or "index.html"
                        if k not in files:k+=".html"
                        if k not in files or ".." in Path(k).parts or u.query:
                            unexpected.append(req.request.url);req.abort();return
                        mime={
                            ".html":"text/html; charset=utf-8",
                            ".js":"application/javascript",
                            ".css":"text/css",
                            ".woff2":"font/woff2",
                        }.get(Path(k).suffix,mimetypes.guess_type(k)[0] or "application/octet-stream")
                        req.fulfill(status=200,body=files[k],headers={**headers,"Content-Type":mime})
                    ctx.route("**/*",fulfill)
                    resp=page.goto("https://aiskillab.work"+route,wait_until="load",timeout=18000)
                    need(resp is not None and resp.status==200, "offline status "+route)
                    page.evaluate("document.fonts.ready")
                    info=page.evaluate("""() => ({
                      lang:document.documentElement.lang,
                      width:document.documentElement.scrollWidth,
                      viewport:window.innerWidth,
                      h1:document.querySelectorAll('h1').length,
                      footerLink:document.querySelectorAll('footer a[data-universe-event="universe_click"]').length,
                      footerIcon:document.querySelectorAll('footer a[data-universe-event="universe_click"] svg').length,
                      teaser:document.querySelectorAll('[data-u3-universe-teaser]').length,
                      projects:document.querySelectorAll('a[data-universe-event="project_click"]').length,
                      listings:document.querySelectorAll('[data-u2-card]').length,
                      scripts:[...document.querySelectorAll('script[src]')].filter(x=>x.src.endsWith('/phuket-universe-events.js')).length,
                    })""")
                    need(info["lang"]==locale and info["width"]<=width
                         and info["footerLink"]==1 and info["footerIcon"]==1
                         and info["scripts"]==1, "layout basics "+str(info))
                    need(info["teaser"]==(1 if route.endswith("/phuket") else 0),"teaser "+route)
                    need(info["projects"]==(5 if route.endswith("phuket-universe") else 0),"project markers")
                    need(info["listings"]==0,"inventory must stay empty")
                    locator=page.locator('footer a[data-universe-event="universe_click"]')
                    need(locator.get_attribute("href")==expected,"footer locale mismatch")
                    # Synthetic DOM click; block navigation and assert no POST to the old receiver.
                    if js:
                        page.evaluate("""() => document.addEventListener('click', e => {
                            if(e.target.closest('a[data-universe-event]'))e.preventDefault()
                          },true)""")
                        locator.dispatch_event("click")
                        if route.endswith("phuket-universe"):
                            page.locator('a[data-universe-event="project_click"]').first.dispatch_event("click")
                        page.wait_for_timeout(60)
                    need(not unexpected and not errors and not events,
                         "unexpected network/JS failure: "+repr((unexpected,errors,events)))
                    results.append({"route":route,"locale":locale,"js":js,"width":width,
                                    "height":page.evaluate("document.documentElement.scrollHeight"),
                                    "status":"PASS","event_post_count":0})
                    print("U3_BROWSER_PASS",json.dumps(results[-1],ensure_ascii=False),flush=True)
                    ctx.close()
    finally:
        browser.close()
need(len(results)==24,"browser acceptance count")
print("U3_BROWSER_ACCEPTANCE_PASS cases=24 real_network=0 event_posts=0",flush=True)
