"""R12 exact compact preview QA. No fetch, production access, or release approval.
Run: python verify_compact.py --candidate <R12 candidate> --r10 <R10 bundle>
 --r11 <R11 verify_review.py> --browser <installed Chromium> --output <new dir>
"""
import argparse,hashlib,http.server,json,threading,sys
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
REPORT="ef2ccf408a17f806546e6d358319915686900ad2f896bdab2b5395605d4fe001"
R10="13a0549668dea88764eecdb20862fb78ea2d5487fed8be2f89857cfadb221bbb"
R11="a69a1f5a3b1ca36fdcbe062935c03fd6be88af21ead0e25362d410ad91c1f366"
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(path,pin):
 b=path.read_bytes();need(sha(b)==pin,"pin "+str(path));return b
def run(candidate,r10,r11,browser_path,out):
 m=json.loads(checked(candidate/"report.json",REPORT))
 old=json.loads(checked(r10/"REVIEW.json",R10))
 need(m["base"]==BASE and m["shared_assets"]==9 and m["saved_bytes"]==11764,"scope")
 files={n:checked(candidate/n,v["sha256"]) for n,v in m["files"].items()}
 need(len(files)==21,"candidate inventory")
 for n,pin in old["assets"].items():files[n]=checked(r10/"preview"/n,pin)
 files["index.html"]=checked(r10/"preview"/"index.html",old["index_sha256"])
 allowed={"/"+n:b for n,b in files.items()}
 allowed["/"]=files["index.html"]
 allowed["/phuket-universe"]=files["phuket-universe.html"]
 allowed["/en/phuket-universe"]=files["en/phuket-universe.html"]
 raw=checked(r11,R11);ns={"__name__":"r11_pinned_cases"};exec(compile(raw,"verify_review.py","exec"),ns)
 class Handler(http.server.BaseHTTPRequestHandler):
  def log_message(self,*a):pass
  def do_GET(self):
   u=urlsplit(self.path);p=u.path
   if self.headers.get("Host")!=f"127.0.0.1:{self.server.server_port}":self.send_error(403);return
   if u.query or p not in allowed:self.send_error(404);return
   b=allowed[p]
   mime="text/css" if p.endswith(".css") else "application/javascript" if p.endswith(".js") else "font/woff2" if p.endswith(".woff2") else "text/html; charset=utf-8"
   self.send_response(200);self.send_header("Content-Type",mime);self.send_header("Content-Length",str(len(b)));self.send_header("Cache-Control","no-store");self.send_header("X-Robots-Tag","noindex,nofollow");self.send_header("X-Content-Type-Options","nosniff")
   if mime.startswith("text/html"):
    policy="frame-ancestors 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
    if p in ("/","/index.html"):policy+="; default-src 'none'; style-src 'unsafe-inline'"
    elif "rental-journey.html" in p or "phuket-universe" in p:policy+="; default-src 'none'; script-src 'none'; style-src 'self'; font-src 'self'; img-src 'self' data:"
    self.send_header("Content-Security-Policy",policy)
   self.end_headers();self.wfile.write(b)
 out.mkdir(parents=True,exist_ok=False)
 server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler);server.daemon_threads=True
 thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 origin=f"http://127.0.0.1:{server.server_port}"
 tests={};cases=[];fatal=None
 try:
  for n,b in files.items():
   status,headers,actual=ns["local_http"](server.server_port,"/"+n)
   tests["served:"+n]=status==200 and actual==b and headers.get("Cache-Control")=="no-store"
  tests["unknown_route_denied"]=ns["local_http"](server.server_port,"/sources/runner.py")[0]==404
  tests["post_denied"]=ns["local_http"](server.server_port,"/",method="POST")[0]==501
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
   try:
    for l in ("ru","en"):
     for width in (320,390,1440):
      c=ns["browser_case"](browser,origin,l,width);cases.append(c)
      print("CASE",l,width,sum(c["tests"].values()),"/",len(c["tests"]),"FAILED",[k for k,v in c["tests"].items() if not v],flush=True)
    kinds=("budget-calculator","shortlist","move-in","move-out")
    for l in ("ru","en"):
     for kind in kinds:
      ctx=browser.new_context(service_workers="block",viewport={"width":390,"height":844})
      external=[];messages=[]
      def route(rt):
       if rt.request.url.startswith(origin+"/"):rt.continue_()
       else:external.append(rt.request.url);rt.abort()
      ctx.route("**/*",route);page=ctx.new_page();page.on("console",lambda msg:messages.append(msg.text))
      page.goto(origin+"/preview-tools/"+l+"/rental-"+kind+".html",wait_until="load",timeout=12000)
      tests["css_applied:"+l+":"+kind]=page.evaluate("getComputedStyle(document.body).backgroundColor")== "rgb(13, 19, 32)" and page.evaluate("document.styleSheets.length") == 1
      tests["no_integrity_error:"+l+":"+kind]=not external and not any("integrity" in x.lower() or "violates the following content security policy" in x.lower() for x in messages)
      ctx.close()
    # Substitute corrupt response bytes in a separate isolated browser context.
    for ext in ("js","css"):
     key="/preview-tools/assets/rental-budget-calculator"+("-1.js" if ext=="js" else ".css")
     ctx=browser.new_context(service_workers="block",viewport={"width":390,"height":844});messages=[];tampered=[]
     def route_bad(rt):
      url=rt.request.url
      if url==origin+key:
       tampered.append(url)
       body=allowed[key]+(b";document.documentElement.dataset.tampered='yes';" if ext=="js" else b"body{background:rgb(1,2,3)!important}")
       rt.fulfill(status=200,body=body,content_type="application/javascript" if ext=="js" else "text/css")
      elif url.startswith(origin+"/"):rt.continue_()
      else:rt.abort()
     ctx.route("**/*",route_bad);page=ctx.new_page();page.on("console",lambda msg:messages.append(msg.text))
     page.goto(origin+"/preview-tools/en/rental-budget-calculator.html",wait_until="load",timeout=12000)
     if ext=="js":
      page.locator("#example").click()
      blocked=page.locator("#monthly").inner_text()=="—" and page.evaluate("document.documentElement.dataset.tampered===undefined")
     else:blocked=page.evaluate("getComputedStyle(document.body).backgroundColor")!="rgb(1, 2, 3)"
     tests["tampered_"+ext+"_rejected"]=bool(tampered) and blocked and any("integrity" in x.lower() for x in messages)
     ctx.close()
   finally:browser.close()
 except Exception as e:
  fatal=type(e).__name__+": "+str(e);print("FAIL",fatal,flush=True)
 finally:
  server.shutdown();server.server_close();thread.join(timeout=5)
  tests["server_stopped"]=not thread.is_alive()
 passed=sum(tests.values())+sum(sum(c["tests"].values()) for c in cases);total=len(tests)+sum(len(c["tests"]) for c in cases)
 ok=not fatal and len(cases)==6 and all(tests.values()) and all(c["pass"] for c in cases)
 report={"scope":"OWNER_R12_COMPACT_QA","created_utc":datetime.now(timezone.utc).isoformat(),"base":BASE,"candidate_report_sha256":REPORT,"tests":tests,"browser_cases":cases,"passed":passed,"total":total,"all_pass":ok,"fatal":fatal,"release_approval":False,"limitations":"Exact local review only. Chromium. Original runtime blocked. No independent, visual, accessibility, production-transfer or release acceptance."}
 b=(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode()
 with (out/"QA.json").open("xb") as f:f.write(b)
 print("RESULT","PASS" if ok else "REVISE",passed,"/",total,"FAILED",[k for k,v in tests.items() if not v],"SHA256",sha(b),flush=True)
 return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("candidate","r10","r11","browser","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=x.resolve() and x.resolve() not in out.parents for x in (a.candidate,a.r10)),"external new output")
 sys.exit(run(a.candidate.resolve(),a.r10.resolve(),a.r11.resolve(),a.browser.resolve(),out))
