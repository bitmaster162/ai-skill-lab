"""Daily essentials R1: isolated Chromium QA, no external traffic or release writes."""
import argparse,hashlib,json,sys
from pathlib import Path
from urllib.parse import urlsplit
PIN="c13717ecafb21cb37ce53e282383c67c2df0b27a24617182d92057364781a36a"
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def run(c,browser_path,out):
 raw=(c/"DAILY_DRAFT.json").read_bytes();need(sha(raw)==PIN,"report")
 m=json.loads(raw);need(not m["release_approval"],"draft")
 files={f.relative_to(c/"static").as_posix():f.read_bytes() for f in (c/"static").rglob("*") if f.is_file()}
 need(len(files)==120 and sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())==m["candidate_payload_sha256"],"payload")
 for n,v in m["delta"].items():need(sha(files[n])==v["sha256"] and (c/"overlay"/n).read_bytes()==files[n],"delta")
 headers={v["key"]:v["value"] for h in json.loads(files["vercel.json"])["headers"] if h["source"]=="/(.*)" for v in h["headers"]}
 # Add proposed exact per-page script hash to inherited global header for
 # simulation only; no change to actual parent config or historical gates.
 import base64
 digest="'sha256-"+base64.b64encode(hashlib.sha256(files["phuket-daily-assets/essentials.js"]).digest()).decode()+"'"
 # Same-origin external scripts are permitted by the actual global CSP.
 # Verify the exact original global header instead of installing exceptions.
 routes={"/"+(n[:-5] if n.endswith(".html") else n):b for n,b in files.items()}
 cases=[];fatal=None
 try:
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
   try:
    for l in ("ru","en"):
     base="/en/phuket-universe" if l=="en" else "/phuket-universe"
     dest=base+"/daily-essentials"
     for width,enabled in ((320,False),(390,True),(1440,True)):
      ctx=browser.new_context(viewport={"width":width,"height":844},service_workers="block",java_script_enabled=enabled)
      blocked=[];served=[];errors=[];messages=[]
      def serve(rt):
       u=urlsplit(rt.request.url);p=u.path
       if u.scheme=="https" and u.netloc=="preview.invalid" and rt.request.method=="GET" and not u.query and p in routes:
        mime="text/css" if p.endswith(".css") else "application/javascript" if p.endswith(".js") else "font/woff2" if p.endswith(".woff2") else "text/html; charset=utf-8"
        served.append(p);rt.fulfill(status=200,body=routes[p],content_type=mime,headers=headers)
       else:blocked.append((u.netloc,p));rt.abort()
      ctx.route("**/*",serve)
      page=ctx.new_page();page.set_default_timeout(6000)
      page.on("pageerror",lambda e:errors.append(str(e)));page.on("console",lambda msg:messages.append(msg.text))
      checks={}
      try:
       page.goto("https://preview.invalid"+base,wait_until="load",timeout=15000)
       checks["gateway_one"]=page.locator("#daily-essentials a").count()==1
       page.locator("#daily-essentials a").click()
       page.wait_for_url("**"+dest)
       served.clear();blocked.clear();errors.clear();messages.clear()
       page.reload(wait_until="load")
       checks["language"]=page.locator("html").get_attribute("lang")==l
       checks["noindex"]=page.locator("meta[name=robots]").get_attribute("content")=="noindex,nofollow"
       checks["six_native_controls"]=page.locator("[data-errand]").count()==6 and all(x==4 for x in page.locator("select").evaluate_all("(es)=>es.map(e=>e.options.length)"))
       checks["geometry"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
       page.keyboard.press("Tab");skip=page.locator("a.skip-link");box=skip.bounding_box()
       checks["skip_first_focus"]=skip.evaluate("(e)=>e===document.activeElement") and box["x"]>=0 and box["x"]+box["width"]<=width+1
       page.keyboard.press("Enter");checks["skip_main"]=page.evaluate("document.activeElement.id==='main'") and urlsplit(page.url).fragment=="main"
       page.keyboard.press("Tab");checks["tab_inside_main"]=page.evaluate("document.querySelector('main').contains(document.activeElement)")
       g=lambda k:page.locator("#"+k)
       for k,v in [("food","1"),("work","2"),("transport","3"),("leisure","1")]:g(k).select_option(v)
       checks["independent_selections"]=g("food").input_value()=="1" and g("work").input_value()=="2" and g("transport").input_value()=="3" and g("laundry").input_value()=="0"
       if enabled:
        checks["counts"]=[x.inner_text() for x in page.locator("[data-count]").all()]==["2","1","1"]
        note=g("plan-text").input_value()
        checks["summary_selected_only"]=all(g(k+"-title").inner_text() in note for k in ("food","work","transport","leisure")) and g("laundry-title").inner_text() not in note
        g("food").select_option("3")
        checks["state_recalculated"]=[x.inner_text() for x in page.locator("[data-count]").all()]==["1","1","2"]
        g("reset").click()
        checks["reset"]=all(x=="0" for x in page.locator("select").evaluate_all("(es)=>es.map(e=>e.value)")) and g("reset").is_disabled()
        checks["empty_summary"]=g("plan-text").input_value()==g("plan").get_attribute("data-empty")
        checks["plan_visible"]=g("plan").is_visible()
       else:checks["nojs_manual"]=not g("plan").is_visible() and g("work").input_value()=="2"
       checks["reciprocal_language"]=page.locator("header a[lang]").get_attribute("href")==("/phuket-universe/daily-essentials" if l=="en" else "/en/phuket-universe/daily-essentials")
       checks["return_link"]=page.locator("header a").first.get_attribute("href")==base+"#daily-essentials"
       checks["no_font_requests"]=not any(n.endswith(".woff2") for n in served)
       checks["no_errors_or_external"]=not errors and not blocked and not any("content security policy" in s.lower() or "integrity" in s.lower() for s in messages)
       checks["no_storage"]=page.evaluate("localStorage.length===0&&sessionStorage.length===0")
      finally:ctx.close()
      cases.append({"locale":l,"width":width,"js":enabled,"checks":checks,"pass":all(checks.values()),"blocked":blocked,"errors":errors,"console":messages})
      print("CASE",l,width,enabled,sum(checks.values()),"/",len(checks),"FAIL",[k for k,v in checks.items() if not v],flush=True)
   finally:browser.close()
 except Exception as e:fatal=type(e).__name__+": "+str(e);print("FAIL",fatal,flush=True)
 total=sum(len(x["checks"]) for x in cases);passed=sum(sum(x["checks"].values()) for x in cases)
 ok=not fatal and len(cases)==6 and passed==total
 report={"scope":"OWNER_DAILY_R1_ISOLATED_BROWSER_QA","report_sha256":PIN,"cases":cases,"passed":passed,"total":total,"all_pass":ok,"fatal":fatal,"release_approval":False,"limitations":"Native and JS functions in Chromium; exact parent global CSP simulated. No real deployment, actual Next equivalent, full preflight, independent review or release admission."}
 out.mkdir(parents=True,exist_ok=False);b=(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode();(out/"QA.json").write_bytes(b)
 print("RESULT","PASS" if ok else "REVISE",passed,"/",total,"SHA256",sha(b),flush=True);return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for k in ("candidate","browser","output"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and a.candidate.resolve() not in out.parents,"new output")
 sys.exit(run(a.candidate,a.browser,out))
