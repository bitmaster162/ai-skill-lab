import json,hashlib,threading,functools,sys
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
P=Path(__file__).parent;C=P/"candidate";S=C/"static"
PIN="8813b0158b2e69d33383295b67fb87b92026ee79cb061be66b6f3329d0678fcc"
def sha(b):return hashlib.sha256(b).hexdigest()
raw=(C/"VARIANCE_DRAFT.json").read_bytes();assert sha(raw)==PIN
m=json.loads(raw)
for n,v in m["patch_files"].items():
 p=S/n[12:] if n.startswith("deploy/live/") else C/"next"/n
 assert sha(p.read_bytes())==v["sha256"],n
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_POST(self):self.send_error(405)
def main():
 out=P/"QA.json";assert not out.exists()
 server=ThreadingHTTPServer(("127.0.0.1",0),functools.partial(Handler,directory=str(S)))
 threading.Thread(target=server.serve_forever,daemon=True).start()
 host="http://127.0.0.1:"+str(server.server_port)
 rows=[]
 try:
  with sync_playwright() as pw:
   b=pw.chromium.launch(executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",headless=True)
   for lang in ("ru","en"):
    path="/phuket-universe/daily-budget.html" if lang=="ru" else "/en/phuket-universe/daily-budget.html"
    for width in (320,390,1440):
     for js in (True,False):
      checks={}
      ctx=b.new_context(viewport={"width":width,"height":900},java_script_enabled=js)
      external=[];errors=[]
      def route(r):
       if r.request.url.startswith(host+"/"):r.continue_()
       else:external.append(r.request.url);r.abort()
      ctx.route("**/*",route);pg=ctx.new_page();pg.on("pageerror",lambda e:errors.append(str(e)))
      try:
       pg.goto(host+path,wait_until="load",timeout=15000)
       g=lambda x:pg.locator("#"+x)
       cat=g("category-variance")
       v=lambda k:g("variance-"+k).inner_text()
       fill=lambda k,s:g(k).fill(s)
       keys=cat.locator("[data-category]").evaluate_all("(els)=>els.map(e=>e.dataset.category)")
       checks["six_unique_outputs"]=len(keys)==len(set(keys))==6 and all(g("variance-"+k).count()==1 for k in keys)
       checks["geometry"]=pg.evaluate("document.documentElement.scrollWidth <= innerWidth")
       if js:
        money=lambda n:pg.evaluate("(n)=>new Intl.NumberFormat(document.documentElement.lang,{minimumFractionDigits:2,maximumFractionDigits:2}).format(n/100)+' THB'",n)
        unknown=g("summary").get_attribute("data-unknown");invalid=g("summary").get_attribute("data-invalid")
        label=lambda k:cat.locator('[data-category="'+k+'"] span').inner_text()
        state=lambda k:cat.get_attribute("data-"+k)
        note=lambda:g("summary-text").input_value()
        checks["initial_unknown"]=cat.is_visible() and all(v(k)==unknown for k in keys)
        fill(keys[0],"10");checks["one_value_unknown"]=v(keys[0])==unknown
        fill(keys[0]+"-actual","10.01");checks["over_one_satang"]=v(keys[0])==state("over")+" · "+money(1)
        fill(keys[1],"0");fill(keys[1]+"-actual","0");checks["zero_equal"]=v(keys[1])==state("equal")+" · "+money(0)
        fill(keys[2],"12,50");fill(keys[2]+"-actual","2.25");checks["under"]=v(keys[2])==state("under")+" · "+money(-1025)
        checks["partial_not_total"]=g("actual-delta").inner_text()=="—"
        checks["independent_rows"]=all(v(k)==unknown for k in keys[3:])
        checks["summary_live"]=label(keys[0])+": "+v(keys[0]) in note() and label(keys[2])+": "+v(keys[2]) in note()
        fill(keys[3],"1e3");checks["invalid_not_unknown"]=v(keys[3])==invalid
        fill(keys[3]+"-actual","0");checks["invalid_not_zero"]=v(keys[3])==invalid
        fill(keys[3],"0");checks["invalid_recovery"]=v(keys[3])==state("equal")+" · "+money(0)
        fill(keys[0]+"-actual","");checks["cleared_unknown"]=v(keys[0])==unknown and label(keys[0])+": "+unknown in note()
        fill(keys[0]+"-actual","10.01")
        for k in keys[4:]:fill(k,"0");fill(k+"-actual","0")
        checks["aggregate_exact"]=g("actual-delta").inner_text()==money(-1024)
        fill("budget","100");checks["actual_remaining"]=g("actual-remaining").inner_text()==money(8774)
        g("reset").click();checks["reset_all"]=all(v(k)==unknown for k in keys) and g("reset").is_disabled() and g("actual-delta").inner_text()=="—"
        checks["no_storage"]=pg.evaluate("localStorage.length===0 && sessionStorage.length===0")
       else:
        checks["nojs_hidden"]=not cat.is_visible()
        fill(keys[0],"1");fill(keys[0]+"-actual","0")
        checks["nojs_native"]=g(keys[0]).input_value()=="1" and g(keys[0]+"-actual").input_value()=="0" and not cat.is_visible()
       checks["no_external_requests"]=not external;checks["no_page_errors"]=not errors
      except Exception as e:checks["exception"]=False;errors.append(str(e))
      finally:ctx.close()
      rows.append({"language":lang,"width":width,"js":js,"checks":checks,"errors":errors,"external":external})
   b.close()
 finally:server.shutdown();server.server_close()
 total=sum(len(r["checks"]) for r in rows);passed=sum(sum(r["checks"].values()) for r in rows)
 result={"scope":"OWNER_CATEGORY_VARIANCE_R6_BROWSER_QA","manifest":PIN,"passed":passed,"total":total,"all_pass":passed==total,"cases":rows,"limitations":"Isolated static Chromium; not full inherited suite, Next router/build, independent accessibility or release acceptance."}
 out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print("R6 QA",passed,"/",total,"sha",sha(out.read_bytes()),flush=True)
 for row in rows:
  failed=[k for k,v in row["checks"].items() if not v]
  if failed: print(row["language"],row["width"],row["js"],failed,row["errors"],flush=True)
 return 0 if passed==total else 1
if __name__=="__main__":sys.exit(main())
