"""R20 font dependency and regression verification. Installed Chromium/Playwright/Node.
Run: python verify_fonts.py --candidate <R20> --r19 <R19> --r18 <R18>
 --builder <system_fonts.py> --measurement <R17 runner> --browser <Chromium> --output <new dir>
No network to public services, no admission or live writes.
"""
import argparse,base64,hashlib,json,subprocess,sys
from pathlib import Path
from urllib.parse import urlsplit
PIN="7f51fe030fa0e0dc5258c646e705d6f92ac8bd8341ca0bff2f76b3ca76ed6f53"
R19="57bb2559e5f7128f99ab30ae42a194bcec6d9a3e1b94d2cf1c4cbcfbe54c718c"
R18="2c9641546e4d800cb1f024064e41c1480a0ebc62e328ead60c5ceecb0defece2"
BUILDER="178c64bff114250e52fe09854417e7eec3f31304a63a499f36814175256e7454"
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
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def rejected(fn):
 try:fn()
 except ValueError:return True
 return False
def run(c,old,r18,builder,measurement,browser_path,out):
 m=json.loads(checked(c/"R20.json",PIN));om=json.loads(checked(old/"R19.json",R19));rm=json.loads(checked(r18/"R18.json",R18))
 need(not any(x["release_approval"] for x in (m,om,rm)),"draft scope")
 ns={"__name__":"r20_pinned_policy"};exec(compile(checked(builder,BUILDER),"system_fonts.py","exec"),ns)
 a=read(old/"static");b=read(c/"static")
 need(ns["measure"](a)==om["candidate_payload"] and ns["measure"](b)==m["candidate_payload"],"exact payload")
 need(sha(measurement.read_bytes())==MEASURE,"pinned measurement")
 for n,v in m["next_delta"].items():need(sha((c/"next"/n).read_bytes())==v["sha256"],"Next pin")
 policy=m["font_policy_proposal"];guard=ns["font_policy"]
 tests={"exact_tool_font_policy":guard(b,policy)};cases=[];fatal=None;metrics={}
 sample="phuket-universe/rental-journey.html"
 # Test semantic rejection even when the changed document has been re-pinned.
 def altered(raw):
  modified=dict(b);modified[sample]=raw
  p={**policy,sample:{**policy[sample],"html_sha256":sha(raw)}}
  return modified,p
 wrong,p=altered(b[sample].replace(b"</head>",b'<link rel="preload" as="font" href="/fonts/Manrope-latin.woff2"></head>',1))
 tests["added_preload_rejected"]=rejected(lambda:guard(wrong,p))
 wrong,p=altered(b[sample].replace(b"font-src &#x27;none&#x27;",b"font-src &#x27;self&#x27;",1))
 p[sample]["csp"]=p[sample]["csp"].replace("font-src 'none'","font-src 'self'")
 tests["font_csp_relaxation_rejected"]=rejected(lambda:guard(wrong,p))
 tests["extra_route_rejected"]=rejected(lambda:guard(b,{**policy,"unexpected.html":policy[sample]}))
 tests["missing_route_rejected"]=rejected(lambda:guard(b,{n:v for n,v in policy.items() if n!=sample}))
 tests["font_budget_increase_rejected"]=rejected(lambda:guard(b,{**policy,sample:{**policy[sample],"font_bytes":1}}))
 try:
  for label,root in (("before",old/"static"),("after",c/"static")):
   z=subprocess.run(["node",str(measurement),str(root)],check=True,capture_output=True,timeout=120)
   data=json.loads(z.stdout);need(len(data["rows"])==71 and not data["failures"],"measurement coverage")
   metrics[label]=data
  for n in policy:
   q=metrics["after"]["rows"][n]
   tests[n+":zero_font_budget"]=q["fontCount"]==q["fontBytes"]==0 and q["firstWithFonts"]==q["firstBr"]
   tests[n+":generic_byte_caps"]=q["htmlBr"]<=10240 and q["cssBr"]<=8192 and q["firstBr"]<=19456 and q["firstGz"]<=23040 and q["firstWithFonts"]<=102400
  guides=[n for n in policy if n.endswith("rental-journey.html")]
  for n in guides:
   p=metrics["before"]["rows"][n];q=metrics["after"]["rows"][n]
   tests[n+":reduced_first_view"]=q["firstWithFonts"]<p["firstWithFonts"] and q["firstBr"]<p["firstBr"]
   print("TRANSFER",n,"fonts",p["fontBytes"],"->",q["fontBytes"],"first_with_fonts",p["firstWithFonts"],"->",q["firstWithFonts"],flush=True)
  tests["other_69_transfer_rows_unchanged"]=all(v==metrics["after"]["rows"][n] for n,v in metrics["before"]["rows"].items() if n not in guides)
  # Check the new guide responses, and the unchanged other eight handlers.
  js="""import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=process.argv[1],prior=process.argv[2];const m=JSON.parse(fs.readFileSync(path.join(root,'R20.json'),'utf8'));const old=JSON.parse(fs.readFileSync(path.join(prior,'R18.json'),'utf8'));const rows=new Map(old.routes.map(r=>[r.route,r]));for(const r of m.routes)rows.set(r.route,r);const checks={};
for(const r of rows.values()){const mod=await import(pathToFileURL(path.join(root,'next',r.handler)).href);const res=mod.GET();const b=Buffer.from(await res.arrayBuffer());checks[r.route]=res.status===200&&b.equals(fs.readFileSync(path.join(root,'static',r.html_path)))&&createHash('sha256').update(b).digest('hex')===r.body_sha256&&Object.entries(r.headers).every(([k,v])=>res.headers.get(k)===v)}
console.log(JSON.stringify(checks));"""
  z=subprocess.run(["node","--input-type=module","-e",js,str(c),str(r18)],check=True,capture_output=True,timeout=30)
  checks=json.loads(z.stdout);need(len(checks)==10,"ten handler results")
  tests.update({"node:"+k:v for k,v in checks.items()})
  cfg=json.loads(b["vercel.json"]);headers={h["key"]:h["value"] for x in cfg["headers"] if x["source"]=="/(.*)" for h in x["headers"]}
  routes={"/"+(n[:-5] if n.endswith(".html") else n):v for n,v in b.items()}
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
   try:
    for width,enabled in ((320,False),(1440,True)):
     for n in sorted(policy):
      route="/"+n[:-5];kind=n.split("rental-")[-1][:-5];l="en" if n.startswith("en/") else "ru";origin="https://preview.invalid"
      served=[];blocked=[];errors=[];messages=[];font_requests=[]
      ctx=browser.new_context(viewport={"width":width,"height":844},service_workers="block",java_script_enabled=enabled,locale="ru-RU" if l=="ru" else "en-US")
      def serve(rt):
       u=urlsplit(rt.request.url);p=u.path
       if rt.request.resource_type=="font" or p.endswith((".woff",".woff2",".ttf",".otf")):font_requests.append(p)
       if u.scheme=="https" and u.netloc=="preview.invalid" and rt.request.method=="GET" and not u.query and p in routes:
        mime="text/css" if p.endswith(".css") else "application/javascript" if p.endswith(".js") else "font/woff2" if p.endswith(".woff2") else "text/html; charset=utf-8"
        served.append(p);rt.fulfill(status=200,body=routes[p],content_type=mime,headers=headers)
       else:blocked.append((u.netloc,p));rt.abort()
      ctx.route("**/*",serve);page=ctx.new_page();page.set_default_timeout(5000)
      page.on("pageerror",lambda e:errors.append(str(e)));page.on("console",lambda msg:messages.append(msg.text))
      check={};g=lambda k:page.locator("#"+k)
      try:
       page.goto(origin+route,wait_until="load",timeout=12000);page.evaluate("document.fonts.ready")
       check["system_heading_font"]=page.locator("h1").evaluate("(e)=>getComputedStyle(e).fontFamily.includes('system-ui')")
       check["no_webfont_faces"]=page.evaluate("document.fonts.size===0")
       check["no_font_preloads"]=page.locator('link[as=font]').count()==0
       check["one_stylesheet"]=page.evaluate("document.styleSheets.length===1")
       page.keyboard.press("Tab");skip=page.locator('a[class*="skip"][href="#main"]')
       box=skip.bounding_box();check["first_tab_and_visible"]=skip.evaluate("(e)=>e===document.activeElement") and box["x"]>=0 and box["x"]+box["width"]<=width+1
       page.keyboard.press("Enter");check["skip_focus"]=page.evaluate("document.activeElement.id==='main'") and urlsplit(page.url).fragment=="main"
       page.keyboard.press("Tab");check["inside_main"]=page.evaluate("document.querySelector('main').contains(document.activeElement)")
       check["geometry"]=page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
       if kind=="journey":
        boxes=page.locator('input[type=checkbox]');boxes.first.check();check["guide_controls"]=boxes.count()==10 and boxes.first.is_checked() and not boxes.last.is_checked()
        summary=page.locator("details summary");summary.first.focus();summary.first.press("Enter");check["guide_details"]=summary.count()==5 and page.locator("details").first.get_attribute("open") is not None
       elif enabled:
        if kind=="budget-calculator":
         g("example").click();check["functional_smoke"]=["".join(x for x in g(k).inner_text() if x.isdecimal()) for k in ("monthly","upfront")]==["31000","86000"]
        elif kind=="shortlist":
         g("example").click();g("keep1").check();g("note-generate").click();check["functional_smoke"]=bool(g("note-output").input_value())
        elif kind=="move-in":
         g("item-1").select_option("2");check["functional_smoke"]=[int(x) for x in page.locator("[data-count]").all_text_contents()]==[7,0,1,0]
        elif kind=="move-out":
         g("example").click();check["functional_smoke"]=["".join(x for x in g(k).inner_text() if x.isdecimal()) for k in ("expected","delta")]==["35000","5000"]
       page.evaluate("document.fonts.ready")
       check["zero_font_requests"]=not font_requests
       check["no_errors_or_external"]=not errors and not blocked and not any("integrity" in x.lower() or "content security policy" in x.lower() for x in messages)
      finally:ctx.close()
      cases.append({"route":route,"width":width,"js":enabled,"checks":check,"pass":all(check.values()),"font_requests":font_requests,"served":sorted(set(served)),"blocked":blocked,"errors":errors,"console":messages})
      print("CASE",route,width,sum(check.values()),"/",len(check),"FAIL",[k for k,v in check.items() if not v],flush=True)
   finally:browser.close()
 except Exception as e:fatal=type(e).__name__+": "+str(e);print("FAIL",fatal,flush=True)
 passed=sum(tests.values())+sum(sum(x["checks"].values()) for x in cases);total=len(tests)+sum(len(x["checks"]) for x in cases)
 ok=not fatal and len(cases)==20 and passed==total
 report={"scope":"OWNER_R20_FONT_QA","report_sha256":PIN,"tests":tests,"cases":cases,"metrics":{k:{n:v for n,v in r["rows"].items() if n in policy} for k,r in metrics.items()},"passed":passed,"total":total,"all_pass":ok,"fatal":fatal,"release_approval":False,"limitations":"Historical generic two-preload rule still conflicts with zero-font tools; proposed exact route policy not installed. Compression measurements, isolated Chromium and direct Node handlers, not real network timing, actual Next build, full visual/screen-reader, full preflight or independent approval."}
 out.mkdir(parents=True,exist_ok=False);raw=(json.dumps(report,indent=2)+"\n").encode();(out/"QA.json").write_bytes(raw)
 print("RESULT","PASS" if ok else "REVISE",passed,"/",total,"FAILED",[k for k,v in tests.items() if not v],"SHA256",sha(raw),flush=True)
 return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for k in ("candidate","r19","r18","builder","measurement","browser","output"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=x.resolve() and x.resolve() not in out.parents for x in (a.candidate,a.r19,a.r18)),"new output")
 sys.exit(run(a.candidate,a.r19,a.r18,a.builder,a.measurement,a.browser,out))
