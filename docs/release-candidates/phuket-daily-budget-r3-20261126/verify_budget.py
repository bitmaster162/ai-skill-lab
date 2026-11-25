"""R3 budget owner QA; isolated browser and direct Node handlers."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from urllib.parse import urlsplit
PIN="98e74e68e4a522df49037e755a80550ffcf3b1bfd14abb535b9067f36839bdd3"
R2="3dcc7d9c931f519f5c12fb12aa7a30bc7f529924688a76134b79ea012630f4dc"
KEYS=("budget","food","laundry","work","transport","services","leisure")
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def read(root):
 out={}
 for p in sorted(root.rglob("*")):
  need(not p.is_symlink(),"symlink")
  if p.is_file():out[p.relative_to(root).as_posix()]=p.read_bytes()
 return out
def digest(f):return sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(f.items())).encode())
def run(c,prior,browser_path,out):
 m=json.loads(checked(c/"BUDGET_DRAFT.json",PIN));p=json.loads(checked(prior/"COMBINED_DRAFT.json",R2))
 need(not m["release_approval"] and not p["release_approval"],"draft")
 static=read(c/"static");nxt=read(c/"next");old=read(prior/"static");old_next=read(prior/"next")
 need(len(static)==144 and digest(static)==m["static_payload"],"R3 payload")
 need(len(old)==140 and digest(old)==p["static_payload"],"R2 payload")
 need(len(nxt)==32 and len(old_next)==28,"Next inventory")
 for n,v in p["patch_files"].items():
  b=old[n[12:]] if n.startswith("deploy/live/") else old_next[n]
  need(sha(b)==v["sha256"],"R2 source")
 for n,v in m["patch_files"].items():
  b=static[n[12:]] if n.startswith("deploy/live/") else nxt[n]
  need(sha(b)==v["sha256"] and b==(c/"apply_check"/n).read_bytes(),"R3 patch "+n)
 ds={n for n,b in static.items() if old.get(n)!=b};dn={n for n,b in nxt.items() if old_next.get(n)!=b}
 need({"deploy/live/"+n for n in ds}|dn==set(m["patch_files"]),"exact delta")
 need(set(old)<=set(static) and set(old_next)<=set(nxt),"no removals")
 tests={"exact_prior_unchanged_outside_delta":True};cases=[];fatal=None
 try:
  js="""import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';
const root=process.argv[1];const walk=d=>fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):[path.join(d,e.name)]);
const checks={};for(const f of walk(path.join(root,'next','app')).filter(n=>n.endsWith(path.sep+'route.ts'))){
 const rel=path.relative(path.join(root,'next'),f).split(path.sep).join('/');
 const route='/'+rel.replace(/^app\\/\\((ru|en)\\)\\//,'').replace(/\\/route\\.ts$/,'');
 const mod=await import(pathToFileURL(f).href);const res=mod.GET(),b=Buffer.from(await res.arrayBuffer()),csp=res.headers.get('Content-Security-Policy')||'';
 checks[route]=res.status===200&&b.equals(fs.readFileSync(path.join(root,'static',route.slice(1)+'.html')))&&res.headers.get('X-Robots-Tag')==='noindex, nofollow'&&res.headers.get('Cache-Control')==='no-store'&&csp.includes("default-src 'none'")&&csp.includes("connect-src 'none'")&&csp.includes("frame-ancestors 'none'");
}console.log(JSON.stringify(checks));"""
  z=subprocess.run(["node","--input-type=module","-e",js,str(c)],capture_output=True,timeout=45)
  need(z.returncode==0,z.stderr.decode(errors="replace")[-2000:])
  node=json.loads(z.stdout);need(len(node)==14,"14 handlers")
  tests.update({"node:"+k:v for k,v in node.items()});print("NODE",sum(node.values()),"/",len(node),flush=True)
  headers={v["key"]:v["value"] for h in json.loads(static["vercel.json"])["headers"] if h["source"]=="/(.*)" for v in h["headers"]}
  routes={"/"+(n[:-5] if n.endswith(".html") else n):v for n,v in static.items()}
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
   try:
    for l in ("ru","en"):
     prefix="/en/phuket-universe" if l=="en" else "/phuket-universe"
     dest=prefix+"/daily-budget";daily=prefix+"/daily-essentials"
     for width,enabled in ((320,False),(390,True),(1440,True)):
      ctx=browser.new_context(viewport={"width":width,"height":844},service_workers="block",java_script_enabled=enabled,locale="ru-RU" if l=="ru" else "en-US")
      served=[];blocked=[];errors=[];messages=[]
      def serve(rt):
       u=urlsplit(rt.request.url);q=u.path
       if u.scheme=="https" and u.netloc=="preview.invalid" and rt.request.method=="GET" and not u.query and q in routes:
        mime="text/css" if q.endswith(".css") else "application/javascript" if q.endswith(".js") else "text/html; charset=utf-8"
        served.append(q);rt.fulfill(status=200,body=routes[q],content_type=mime,headers=headers)
       else:blocked.append((u.netloc,q));rt.abort()
      ctx.route("**/*",serve);page=ctx.new_page();page.set_default_timeout(6000)
      page.on("pageerror",lambda e:errors.append(str(e)));page.on("console",lambda x:messages.append(x.text))
      checks={};g=lambda k:page.locator("#"+k)
      try:
       page.goto("https://preview.invalid"+daily,wait_until="load",timeout=12000)
       checks["prior_planner_controls"]=page.locator("[data-errand]").count()==6
       link=page.locator(f'a[href="{dest}"]');checks["one_budget_link"]=link.count()==1
       link.click();page.wait_for_url("**"+dest)
       checks["lang"]=page.locator("html").get_attribute("lang")==l
       checks["noindex"]=page.locator("meta[name=robots]").get_attribute("content")=="noindex,nofollow"
       checks["seven_inputs"]=page.locator("[data-amount]").count()==7 and all(g(k).count()==1 for k in KEYS)
       checks["labels"]=page.evaluate("Array.from(document.querySelectorAll('[data-amount]')).every(e=>e.labels.length===1)")
       checks["links"]=page.locator("header a").first.get_attribute("href")==daily and page.locator("header a[lang]").get_attribute("href")==("/phuket-universe/daily-budget" if l=="en" else "/en/phuket-universe/daily-budget")
       page.keyboard.press("Tab");skip=page.locator("a.skip-link");box=skip.bounding_box()
       checks["visible_skip_first"]=skip.evaluate("(e)=>e===document.activeElement") and box["x"]>=0 and box["x"]+box["width"]<=width+1
       page.keyboard.press("Enter");checks["main_focus"]=page.evaluate("document.activeElement.id==='main'") and urlsplit(page.url).fragment=="main"
       page.keyboard.press("Tab");checks["tab_main"]=page.evaluate("document.querySelector('main').contains(document.activeElement)")
       checks["geometry"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
       if enabled:
        value=lambda k:g(k).inner_text()
        money=lambda v:page.evaluate("(v)=>new Intl.NumberFormat(document.documentElement.lang,{minimumFractionDigits:2,maximumFractionDigits:2}).format(v)+' THB'",v)
        setv=lambda k,v:g(k).fill(v)
        state=lambda k:g("results").get_attribute("data-"+k)
        checks["empty_unknown"]=value("known")==value("remaining")==chr(8212) and value("unknown")=="6" and value("invalid")=="0" and g("reset").is_disabled()
        setv("budget","100");setv("food","0,10");setv("laundry","0.20")
        checks["partial_known"]=value("known")==money(.3) and value("unknown")=="4" and value("remaining")==chr(8212) and value("status")==state("incomplete")
        for k in KEYS[3:]:setv(k,"0")
        checks["exact_decimal_sum"]=value("known")==money(.3) and value("remaining")==money(99.7) and value("unknown")=="0" and value("status")==state("ok")
        setv("transport","99.71")
        checks["overspend_one_satang"]=value("known")==money(100.01) and value("remaining")==money(-.01) and value("status")==state("over")
        for k,bad in (("negative","-1"),("exponent","1e3"),("thousands","1 000"),("precision","0.001"),("bound","10000000.01")):
         setv("transport",bad);checks["reject_"+k]=g("transport").get_attribute("aria-invalid")=="true" and value("invalid")=="1" and value("remaining")==chr(8212) and value("status")==state("bad")
        setv("transport","0")
        checks["invalid_recovery"]=g("transport").get_attribute("aria-invalid") is None and value("invalid")=="0" and value("remaining")==money(99.7)
        setv("budget","");checks["unknown_limit"]=value("remaining")==chr(8212) and value("known")==money(.3) and value("status")==state("incomplete")
        for k in KEYS:setv(k,"0")
        checks["explicit_zero"]=value("known")==money(0) and value("remaining")==money(0) and value("unknown")=="0" and value("status")==state("ok")
        for k in KEYS:setv(k,"10000000")
        checks["max_exact_sum"]=value("known")==money(60000000) and value("remaining")==money(-50000000) and value("invalid")=="0"
        g("reset").click();checks["reset_all"]=all(g(k).input_value()=="" for k in KEYS) and g("reset").is_disabled() and value("remaining")==chr(8212) and page.evaluate("document.activeElement.id==='budget'")
       else:
        g("budget").fill("100");g("food").fill("0")
        checks["nojs_native"]=not g("results").is_visible() and g("budget").input_value()=="100" and g("food").input_value()=="0"
       checks["no_fonts_or_external"]=not any(x.endswith(".woff2") for x in served) and not blocked
       checks["no_errors"]=not errors and not any("content security policy" in x.lower() or "integrity" in x.lower() for x in messages)
       checks["no_storage"]=page.evaluate("localStorage.length===0&&sessionStorage.length===0")
      finally:ctx.close()
      cases.append({"locale":l,"width":width,"js":enabled,"checks":checks,"pass":all(checks.values()),"blocked":blocked,"errors":errors,"console":messages})
      print("CASE",l,width,enabled,sum(checks.values()),"/",len(checks),"FAIL",[k for k,v in checks.items() if not v],flush=True)
   finally:browser.close()
 except Exception as e:fatal=type(e).__name__+": "+str(e);print("FAIL",fatal,flush=True)
 passed=sum(tests.values())+sum(sum(x["checks"].values()) for x in cases);total=len(tests)+sum(len(x["checks"]) for x in cases)
 ok=not fatal and len(cases)==6 and passed==total
 report={"scope":"OWNER_DAILY_BUDGET_R3_QA","report_sha256":PIN,"tests":tests,"cases":cases,"passed":passed,"total":total,"all_pass":ok,"fatal":fatal,"release_approval":False,"limitations":"Isolated Chromium calculations and direct Node handlers. No actual Next build/router, full preflight, screen reader, independent acceptance or release admission."}
 out.mkdir(parents=True,exist_ok=False);raw=(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode();(out/"QA.json").write_bytes(raw)
 print("RESULT","PASS" if ok else "REVISE",passed,"/",total,"SHA256",sha(raw),flush=True)
 return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for k in ("candidate","r2","browser","output"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=p.resolve() and p.resolve() not in out.parents for p in (a.candidate,a.r2)),"new output")
 sys.exit(run(a.candidate,a.r2,a.browser,out))
