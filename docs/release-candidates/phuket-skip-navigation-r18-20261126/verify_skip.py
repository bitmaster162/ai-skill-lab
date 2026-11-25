"""R18 exact skip-navigation QA with pinned payload and direct Node handler readback.
Run: python verify_skip.py --candidate <R18 candidate> --browser <installed Chromium> --output <new directory>
Isolated browser and installed Node only. No live traffic or release admission.
"""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
PIN="2c9641546e4d800cb1f024064e41c1480a0ebc62e328ead60c5ceecb0defece2"
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def run(candidate,browser_path,out):
 raw=(candidate/"R18.json").read_bytes();need(sha(raw)==PIN,"report identity")
 m=json.loads(raw);need(m["scope"]=="R18_SKIP_NAVIGATION_DRAFT_ONLY" and not m["release_approval"],"draft scope")
 files={}
 for f in sorted((candidate/"static").rglob("*")):
  need(not f.is_symlink(),"symlink")
  if f.is_file():files[f.relative_to(candidate/"static").as_posix()]=f.read_bytes()
 need(len(files)==135 and sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())==m["candidate_payload"]["payload_sha256"],"static payload")
 for n,v in m["next_delta"].items():
  b=(candidate/"next"/n).read_bytes();need(sha(b)==v["sha256"] and len(b)==v["bytes"],"Next pin")
 for n,v in m["static_delta"].items():need(sha(files[n])==v["sha256"],"static delta")
 cfg=json.loads(files["vercel.json"]);headers={a["key"]:a["value"] for x in cfg["headers"] if x["source"]=="/(.*)" for a in x["headers"]}
 routes={"/"+(n[:-5] if n.endswith(".html") else n):b for n,b in files.items()}
 tests={};cases=[];fatal=None
 try:
  js="""import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=process.argv[1];const m=JSON.parse(fs.readFileSync(path.join(root,'R18.json'),'utf8'));
const checks={};for(const r of m.routes){
 const mod=await import(pathToFileURL(path.join(root,'next',r.handler)).href);
 const res=mod.GET();const b=Buffer.from(await res.arrayBuffer());
 checks[r.route]=res.status===200&&createHash('sha256').update(b).digest('hex')===r.body_sha256&&b.equals(fs.readFileSync(path.join(root,'static',r.html_path)))&&Object.entries(r.headers).every(([k,v])=>res.headers.get(k)===v);
}
console.log(JSON.stringify(checks));"""
  result=subprocess.run(["node","--input-type=module","-e",js,str(candidate)],capture_output=True,check=True,timeout=30)
  tests.update({"node:"+k:v for k,v in json.loads(result.stdout).items()})
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
   try:
    for width,enabled in ((320,False),(1440,True)):
     for row in m["routes"]:
      route=row["route"];kind=route.split("rental-")[-1];l="en" if route.startswith("/en/") else "ru"
      ctx=browser.new_context(viewport={"width":width,"height":844},service_workers="block",java_script_enabled=enabled,locale="ru-RU" if l=="ru" else "en-US")
      origin="https://preview.invalid";blocked=[];errors=[];messages=[];served=[]
      def serve(rt):
       u=urlsplit(rt.request.url);p=u.path
       if u.scheme=="https" and u.netloc=="preview.invalid" and rt.request.method=="GET" and not u.query and p in routes:
        mime="text/css" if p.endswith(".css") else "application/javascript" if p.endswith(".js") else "font/woff2" if p.endswith(".woff2") else "text/html; charset=utf-8"
        served.append(p);rt.fulfill(status=200,body=routes[p],content_type=mime,headers=headers)
       else:blocked.append((u.netloc,p));rt.abort()
      ctx.route("**/*",serve);page=ctx.new_page();page.set_default_timeout(6000)
      page.on("pageerror",lambda e:errors.append(str(e)));page.on("console",lambda msg:messages.append(msg.text))
      c={};g=lambda n:page.locator("#"+n)
      try:
       page.goto(origin+route,wait_until="load",timeout=12000)
       skip=page.locator('a[class*="skip"][href="#main"]')
       c["one_skip_target"]=skip.count()==1 and g("main").count()==1 and g("main").get_attribute("tabindex")=="-1"
       c["local_label"]=skip.inner_text()==("К основному содержимому" if l=="ru" else "Skip to main content")
       c["initially_hidden"]=skip.bounding_box()["x"]+skip.bounding_box()["width"]<0
       page.keyboard.press("Tab")
       c["first_tab"]=skip.evaluate("(e)=>document.activeElement===e")
       box=skip.bounding_box()
       c["visible_on_focus"]=box["x"]>=0 and box["y"]>=0 and box["x"]+box["width"]<=width+1 and box["y"]+box["height"]<=844
       page.keyboard.press("Enter")
       c["fragment"]=urlsplit(page.url).fragment=="main"
       c["main_focus"]=g("main").evaluate("(e)=>document.activeElement===e")
       c["main_geometry"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
       c["main_not_tabstop"]=g("main").get_attribute("tabindex")=="-1"
       page.keyboard.press("Tab")
       c["next_tab_inside_main"]=page.evaluate("document.getElementById('main').contains(document.activeElement)&&document.activeElement.id!=='main'")
       if kind in ("move-in","move-out"):c["leading_nav_skipped"]=page.locator("header.rental-nav-header nav").count()==1 and page.locator("#main nav").count()==0
       if enabled:
        if kind=="budget-calculator":
         g("example").click();c["functional_smoke"]=["".join(x for x in g(k).inner_text() if x.isdecimal()) for k in ("monthly","upfront")]==["31000","86000"]
        elif kind=="shortlist":
         g("example").click();g("keep1").check();g("note-generate").click();c["functional_smoke"]=bool(g("note-output").input_value())
        elif kind=="move-in":
         g("item-1").select_option("2");c["functional_smoke"]=[int(x) for x in page.locator("[data-count]").all_text_contents()]==[7,0,1,0]
        elif kind=="move-out":
         g("example").click();c["functional_smoke"]=["".join(x for x in g(k).inner_text() if x.isdecimal()) for k in ("expected","delta")]==["35000","5000"]
        else:c["functional_smoke"]=page.locator("#rental-journey nav a").count()==9
       c["no_js_errors"]=not errors
       c["no_external_requests"]=all(h=="preview.invalid" for h,p in blocked)
       c["no_csp_or_sri_errors"]=not any("content security policy" in x.lower() or "integrity" in x.lower() for x in messages)
       c["no_unexpected_blocked"]=not blocked
      finally:ctx.close()
      cases.append({"route":route,"width":width,"js":enabled,"checks":c,"pass":all(c.values()),"blocked":blocked,"errors":errors,"console":messages})
      print("CASE",route,width,enabled,sum(c.values()),"/",len(c),"FAIL",[k for k,v in c.items() if not v],flush=True)
   finally:browser.close()
 except Exception as exc:
  fatal=type(exc).__name__+": "+str(exc);print("FAIL",fatal,flush=True)
 passed=sum(tests.values())+sum(sum(c["checks"].values()) for c in cases);total=len(tests)+sum(len(c["checks"]) for c in cases)
 ok=not fatal and len(tests)==10 and len(cases)==20 and passed==total
 report={"scope":"OWNER_R18_NATIVE_SKIP_QA","created_utc":datetime.now(timezone.utc).isoformat(),"r18_report_sha256":PIN,"checks":tests,"cases":cases,"passed":passed,"total":total,"all_pass":ok,"fatal":fatal,"release_approval":False,"limitations":"Chromium keyboard and selected functional checks; Node direct handler responses. No screen reader, full visual, actual Next build/router, full preflight or admission."}
 out.mkdir(parents=True,exist_ok=False);b=(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode()
 with (out/"QA.json").open("xb") as f:f.write(b)
 print("RESULT","PASS" if ok else "REVISE",passed,"/",total,"SHA256",sha(b),flush=True)
 return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for k in ("candidate","browser","output"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve();candidate=a.candidate.resolve()
 need(not out.exists() and out!=candidate and candidate not in out.parents,"new external output")
 sys.exit(run(candidate,a.browser,out))
