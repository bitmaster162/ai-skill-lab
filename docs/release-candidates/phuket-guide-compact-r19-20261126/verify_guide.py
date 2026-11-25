"""R19 read-only transfer and keyboard QA. Installed Chromium, Playwright, Node.
python verify_guide.py --candidate <R19> --r18 <R18> --measurement <R17 measure_pinned.mjs> --browser <Chromium> --output <new dir>
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from urllib.parse import urlsplit
PIN="57bb2559e5f7128f99ab30ae42a194bcec6d9a3e1b94d2cf1c4cbcfbe54c718c"
OLD="2c9641546e4d800cb1f024064e41c1480a0ebc62e328ead60c5ceecb0defece2"
MEASURE="16520f212967e1aece6646be4f4aa4ad4b60a17d0012254b0c1505e653acdd82"
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):
 files={}
 for f in sorted(p.rglob("*")):
  need(not f.is_symlink(),"symlink")
  if f.is_file():files[f.relative_to(p).as_posix()]=f.read_bytes()
 return files
def payload(files):return sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())
def run(c,old,measurement,browser_path,out):
 raw=(c/"R19.json").read_bytes();need(sha(raw)==PIN,"R19 report")
 m=json.loads(raw);r=(old/"R18.json").read_bytes();need(sha(r)==OLD,"R18 report")
 om=json.loads(r);need(not m["release_approval"] and not om["release_approval"],"draft")
 a=read(old/"static");b=read(c/"static")
 need(payload(a)==om["candidate_payload"]["payload_sha256"] and payload(b)==m["candidate_payload"]["payload_sha256"],"payload identities")
 need(sha(measurement.read_bytes())==MEASURE,"pinned historical measurement")
 tests={};cases=[];fatal=None;metrics={}
 for n,v in m["next_delta"].items():need(sha((c/"next"/n).read_bytes())==v["sha256"],"Next delta pin")
 for n,v in m["static_delta"].items():need(sha(b[n])==v["sha256"],"static delta pin")
 try:
  for label,root in (("before",old/"static"),("after",c/"static")):
   z=subprocess.run(["node",str(measurement),str(root)],check=True,capture_output=True,timeout=120)
   data=json.loads(z.stdout);need(len(data["rows"])==71 and not data["failures"],"measurement coverage")
   metrics[label]=data
  pages=[r["html_path"] for r in m["routes"]]
  for n in pages:
   p=metrics["before"]["rows"][n];q=metrics["after"]["rows"][n]
   tests[n+":css_cap"]=q["cssBr"]<=8192 and q["cssBr"]<p["cssBr"]
   tests[n+":first_view_reduced"]=q["firstBr"]<p["firstBr"] and q["firstGz"]<p["firstGz"]
   tests[n+":font_identity"]=q["fonts"]==p["fonts"] and q["fontBytes"]==p["fontBytes"]
   tests[n+":first_with_fonts_cap"]=q["firstWithFonts"]<=102400
   print("TRANSFER",n,p["cssBr"],"->",q["cssBr"],"first",p["firstBr"],"->",q["firstBr"],"fonts inclusive",p["firstWithFonts"],"->",q["firstWithFonts"],flush=True)
  tests["other_transfer_rows_unchanged"]=all(v==metrics["after"]["rows"][n] for n,v in metrics["before"]["rows"].items() if n not in pages)
  js="""import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=process.argv[1];const m=JSON.parse(fs.readFileSync(path.join(root,'R19.json'),'utf8'));const tests={};
for(const r of m.routes){const mod=await import(pathToFileURL(path.join(root,'next',r.handler)).href);const res=mod.GET();const b=Buffer.from(await res.arrayBuffer());tests[r.route]=res.status===200&&b.equals(fs.readFileSync(path.join(root,'static',r.html_path)))&&createHash('sha256').update(b).digest('hex')===r.body_sha256&&Object.entries(r.headers).every(([k,v])=>res.headers.get(k)===v)}
console.log(JSON.stringify(tests));"""
  z=subprocess.run(["node","--input-type=module","-e",js,str(c)],check=True,capture_output=True,timeout=30)
  tests.update({"node:"+k:v for k,v in json.loads(z.stdout).items()})
  cfg=json.loads(b["vercel.json"]);headers={h["key"]:h["value"] for x in cfg["headers"] if x["source"]=="/(.*)" for h in x["headers"]}
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
   try:
    for width in (320,390,1440):
     for row in m["routes"]:
      route=row["route"];l="en" if route.startswith("/en/") else "ru"
      origin="https://preview.invalid";served=[];blocked=[];errors=[];messages=[]
      ctx=browser.new_context(viewport={"width":width,"height":844},service_workers="block",java_script_enabled=False,locale="ru-RU" if l=="ru" else "en-US")
      routes={"/"+(n[:-5] if n.endswith(".html") else n):v for n,v in b.items()}
      def serve(rt):
       u=urlsplit(rt.request.url);p=u.path
       if u.scheme=="https" and u.netloc=="preview.invalid" and rt.request.method=="GET" and not u.query and p in routes:
        mime="text/css" if p.endswith(".css") else "font/woff2" if p.endswith(".woff2") else "text/html; charset=utf-8"
        served.append(p);rt.fulfill(status=200,body=routes[p],content_type=mime,headers=headers)
       else:blocked.append((u.netloc,p));rt.abort()
      ctx.route("**/*",serve);page=ctx.new_page();page.set_default_timeout(5000)
      page.on("pageerror",lambda e:errors.append(str(e)));page.on("console",lambda msg:messages.append(msg.text))
      check={}
      try:
       page.goto(origin+route,wait_until="load",timeout=12000)
       page.evaluate("document.fonts.ready")
       check["guide_only_css"]=page.evaluate("Array.from(document.styleSheets).map(x=>new URL(x.href).pathname)")==["/phuket-rental-assets/rental-journey.css"]
       check["no_workshop_requests"]="/workshop.css" not in served and "/phuket-universe.css" not in served
       allowed={"/"+x for x in ("fonts/Manrope-latin.woff2","fonts/Manrope-cyrillic.woff2","fonts/Unbounded-ru-en.woff2")}
       requested={x for x in served if x.endswith(".woff2")}
       check["fonts_loaded"]=bool(requested) and requested<=allowed and page.evaluate("document.fonts.check('16px Manrope')&&document.fonts.check('16px Unbounded')")
       check["geometry"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
       check["four_stage_groups"]=page.locator("#rental-journey nav [role=group]").count()==4 and page.locator("#rental-journey nav a").count()==9
       check["skip_first_tab"]=False;page.keyboard.press("Tab");skip=page.locator("a.pu-skip-link");check["skip_first_tab"]=skip.evaluate("(e)=>e===document.activeElement")
       box=skip.bounding_box();check["skip_visible"]=box["x"]>=0 and box["x"]+box["width"]<=width+1
       page.keyboard.press("Enter");check["skip_focus"]=page.evaluate("document.activeElement.id==='main'") and urlsplit(page.url).fragment=="main"
       page.keyboard.press("Tab");check["next_tab"]=page.evaluate("document.querySelector('main').contains(document.activeElement)")
       boxes=page.locator('input[type=checkbox]')
       check["ten_checkboxes"]=boxes.count()==10
       boxes.first.check();boxes.last.check();check["independent_checkboxes"]=boxes.first.is_checked() and boxes.last.is_checked() and not boxes.nth(1).is_checked()
       summary=page.locator("details summary");check["five_disclosures"]=summary.count()==5
       summary.first.focus();summary.first.press("Enter");check["disclosure_keyboard"]=page.locator("details").first.get_attribute("open") is not None
       summary.first.press("Space");check["disclosure_close"]=page.locator("details").first.get_attribute("open") is None
       check["opened_geometry"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
       check["readable_palette"]=page.evaluate("getComputedStyle(document.querySelector('.pu-page')).backgroundColor==='rgb(7, 10, 18)' && getComputedStyle(document.querySelector('.pu-page')).color==='rgb(238, 242, 246)'")
       check["no_errors"]=not errors and not blocked and not any("integrity" in x.lower() or "content security policy" in x.lower() for x in messages)
      finally:ctx.close()
      cases.append({"route":route,"width":width,"checks":check,"pass":all(check.values()),"served":sorted(set(served)),"blocked":blocked,"errors":errors,"console":messages})
      print("CASE",route,width,sum(check.values()),"/",len(check),"FAIL",[k for k,v in check.items() if not v],flush=True)
   finally:browser.close()
 except Exception as e:fatal=type(e).__name__+": "+str(e);print("FAIL",fatal,flush=True)
 passed=sum(tests.values())+sum(sum(x["checks"].values()) for x in cases);total=len(tests)+sum(len(x["checks"]) for x in cases)
 ok=not fatal and len(cases)==6 and passed==total
 report={"scope":"OWNER_R19_GUIDE_QA","report_sha256":PIN,"tests":tests,"cases":cases,"metrics":{k:{n:v for n,v in r["rows"].items() if n in [x["html_path"] for x in m["routes"]]} for k,r in metrics.items()},"passed":passed,"total":total,"all_pass":ok,"fatal":fatal,"release_approval":False,"limitations":"Exact pinned algorithm measurements, not real network timings. Chromium no-JS checks and direct Node handlers; no full visual/screen-reader, actual Next build, preflight, independent approval or release admission."}
 out.mkdir(parents=True,exist_ok=False);raw=(json.dumps(report,indent=2)+"\n").encode();(out/"QA.json").write_bytes(raw)
 print("RESULT","PASS" if ok else "REVISE",passed,"/",total,"SHA256",sha(raw),flush=True)
 return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for k in ("candidate","r18","measurement","browser","output"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=x.resolve() and x.resolve() not in out.parents for x in (a.candidate,a.r18)),"new output")
 sys.exit(run(a.candidate,a.r18,a.measurement,a.browser,out))
