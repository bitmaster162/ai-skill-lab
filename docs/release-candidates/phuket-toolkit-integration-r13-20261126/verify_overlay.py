"""Verify R13 overlay under the exact parent's CSP header, using an isolated browser.
No real deployment or live traffic. Requires installed Chromium and Playwright.
"""
import argparse,hashlib,json,re,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
INVENTORY="cdeb4a954aa77751b6b776419b93f4f9432d70d28d6a66f86fd4d101e21ccc69"
CONFIG="691fa69c52d689ece2ded370065690a72d37ceea648a2952b0fd13db4865773f"
R10="13a0549668dea88764eecdb20862fb78ea2d5487fed8be2f89857cfadb221bbb"
R12="ef2ccf408a17f806546e6d358319915686900ad2f896bdab2b5395605d4fe001"
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def root(l):return ("/en/" if l=="en" else "/")+"phuket-universe"
def number(s):return int("".join(c for c in s if c.isdecimal() or c=="-"))
def run(candidate,config,r10,r12,parent_assets,browser_path,out):
 m=json.loads(checked(candidate/"DRAFT_INVENTORY.json",INVENTORY))
 cfg=json.loads(checked(config,CONFIG))
 old=json.loads(checked(r10/"REVIEW.json",R10));source=json.loads(checked(r12/"report.json",R12))
 need(m["base"]==BASE and m["status"]=="DRAFT_ONLY_NOT_ADMITTED","draft scope")
 files={n:checked(candidate/"overlay"/n,v["sha256"]) for n,v in m["overlay"].items()}
 need(len(files)==21,"overlay inventory")
 for n,pin in old["assets"].items():files[n]=checked(r10/"preview"/n,pin)
 for n,pin in {"workshop.css":"a666815eb37b12ab643de504fd17e0a12255d25989c63b364ea5c58693a3da06","favicon.svg":"3530c65a4a778bb4ad243457cffd36d6d3c063b33231e1838413a97f0b4ce927","fonts/Onest-ru-en.woff2":"1527f4a5e3a2c65b9d789bf86a49cceefea2472bda0b1b3edc08b3adae4a9997"}.items():
  files[n]=checked(parent_assets/n,pin)
 routes={("/"+n[:-5] if n.endswith(".html") else "/"+n):b for n,b in files.items()}
 # The exact parent's global header; route matching and deployment are not claimed.
 headers={x["key"]:x["value"] for x in next(x for x in cfg["headers"] if x["source"]=="/(.*)")["headers"]}
 expected={}
 for l in ("ru","en"):
  for kind in ("shortlist","move-out"):
   name="preview-tools/"+l+"/rental-"+kind+".html"
   s=checked(r12/name,source["files"][name]["sha256"]).decode()
   expected[l,kind]=dict(re.findall(r'<script id="(copy|note-copy)" type="application/json">(.*?)</script>',s,re.S))
 tests={"exact_inputs":True,"six_original_data_blocks":sum(map(len,expected.values()))==6};cases=[]
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
  version=browser.version
  try:
   for l in ("ru","en"):
    for width in (320,390,1440):
     ctx=browser.new_context(viewport={"width":width,"height":844},service_workers="block",locale="ru-RU" if l=="ru" else "en-US")
     origin="https://preview.invalid";blocked=[];errors=[];messages=[];served=[]
     def route(rt):
      u=urlsplit(rt.request.url);path=u.path
      if u.scheme=="https" and u.netloc=="preview.invalid" and rt.request.method=="GET" and not u.query and path in routes:
       mime="text/css" if path.endswith(".css") else "application/javascript" if path.endswith(".js") else "font/woff2" if path.endswith(".woff2") else "image/svg+xml" if path.endswith(".svg") else "text/html; charset=utf-8"
       served.append(path);rt.fulfill(status=200,body=routes[path],content_type=mime,headers=headers)
      else:
       blocked.append((u.scheme,u.netloc,path,rt.request.method));rt.abort()
     ctx.route("**/*",route)
     page=ctx.new_page();page.set_default_timeout(6500);page.on("pageerror",lambda e:errors.append(str(e)));page.on("console",lambda msg:messages.append(msg.text))
     p=root(l);other="en" if l=="ru" else "ru";guide=p+"/rental-journey";calc=p+"/rental-budget-calculator";short=p+"/rental-shortlist";movein=p+"/rental-move-in";moveout=p+"/rental-move-out"
     g=lambda k:page.locator("#"+k);c={}
     def follow(selector,path):
      a=page.locator(selector);a.focus();a.press("Enter");page.wait_for_url("**"+path)
      return urlsplit(page.url).path==urlsplit(path).path and urlsplit(page.url).fragment==urlsplit(path).fragment
     def geometry():return page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
     def noindex():return page.locator('meta[name="robots"]').get_attribute("content")=="noindex,nofollow"
     def data(kind):
      return all(g(k).evaluate("(e)=>e.tagName==='DIV'&&e.hidden") and g(k).text_content()==v for k,v in expected[l,kind].items())
     try:
      page.goto(origin+p,wait_until="load",timeout=12000)
      c["parent_gateway"]=follow("#rental-journey-entry a",guide)
      c["grouped_nav"]=page.locator("#rental-journey nav [role=group]").count()==4 and page.locator("#rental-journey nav a").count()==9
      c["guide_noindex_geometry"]=noindex() and geometry()
      # Tool pages must satisfy the parent's header AND their more restrictive meta CSP.
      messages.clear();errors.clear()
      c["calculator_clean_route"]=follow(f'#rental-journey nav a[href="{calc}"]',calc)
      g("example").click();c["calculator_example"]=[number(g(k).inner_text()) for k in ("monthly","upfront")]==[31000,86000]
      g("prepay").check();c["prepay"]=number(g("upfront").inner_text())==89000
      g("deposit").fill("-1");c["calculator_invalid"]=g("monthly").inner_text()=="—" and g("upfront").inner_text()=="—"
      g("reset").click();c["calculator_reset"]=g("rent").input_value()==""
      c["calculator_noindex_geometry"]=noindex() and geometry()
      c["shortlist_clean_route"]=follow(f'.tool-nav a[href="{short}"]',short)
      c["shortlist_data_bytes"]=data("shortlist")
      c["no_transfer"]=g("budget").input_value()==""
      g("example").click();t=json.loads(g("copy").text_content());n=json.loads(g("note-copy").text_content())
      c["shortlist_example"]=g("summary1").inner_text()==t["matched"] and g("summary2").inner_text()==t["mismatch"]
      g("keep1").check();g("note-generate").click();note=g("note-output").input_value()
      c["note"]=t["matched"] in note and t["option"]+" 1" in note and t["option"]+" 2" not in note
      g("rent1").fill("");c["stale_note"]=g("note-output").input_value()=="" and g("note-status").inner_text()==n["stale"]
      g("note-generate").click();c["unknown_amount"]=t["rent"]+": "+t["unknown"] in g("note-output").input_value()
      c["shortlist_noindex_geometry"]=noindex() and geometry()
      c["guide_return_1"]=follow(f'.tool-nav a[href="{guide}"]',guide)
      c["move_in_clean_route"]=follow(f'#rental-journey nav a[href="{movein}"]',movein)
      counts=lambda:[int(x) for x in page.locator("[data-count]").all_text_contents()]
      for i in range(1,9):g("item-"+str(i)).select_option(str((i-1)%4))
      c["move_in_counts"]=counts()==[2,2,2,2]
      g("reset").click();c["move_in_reset"]=counts()==[8,0,0,0]
      c["move_in_noindex_geometry"]=noindex() and geometry()
      c["guide_return_2"]=follow(f'nav a[href="{guide}"]',guide)
      c["move_out_clean_route"]=follow(f'#rental-journey nav a[href="{moveout}"]',moveout)
      c["move_out_data_bytes"]=data("move-out")
      g("example").click();t2=json.loads(g("copy").text_content())
      c["deposit_example"]=[number(g(k).inner_text()) for k in ("expected","delta")]==[35000,5000] and g("status").inner_text()==t2["less"]
      g("received").fill("40000");c["deposit_negative_delta"]=number(g("delta").inner_text())==-5000
      g("deductions").fill("40001");c["deposit_excess"]=g("expected").inner_text()=="—" and g("status").inner_text()==t2["excess"]
      c["move_out_noindex_geometry"]=noindex() and geometry()
      c["language_switch"]=follow("nav a[lang]",root(other)+"/rental-move-out") and page.locator("html").get_attribute("lang")==other
      c["language_return"]=follow("nav a[lang]",moveout) and page.locator("html").get_attribute("lang")==l
      c["no_storage"]=page.evaluate("localStorage.length===0&&sessionStorage.length===0")
      c["no_tool_forms"]=page.locator("form").count()==0
      c["parent_csp_tool_compatible"]=not errors and not any("content security policy" in v.lower() or "integrity" in v.lower() for v in messages)
      c["no_external_requests"]=all(u=="https" and h=="preview.invalid" and method=="GET" for u,h,_,method in blocked)
      c["only_parent_runtime_blocked"]=all(path in ("/phuket-housing-u2.js","/phuket-universe-events.js","/_vercel/insights/script.js","/lab-command.js","/favicon.ico") for _,_,path,_ in blocked)
      c["no_preview_paths"]=all("/preview-tools/" not in path for path in served)
     finally:ctx.close()
     cases.append({"locale":l,"width":width,"tests":c,"pass":all(c.values()),"blocked_paths":sorted(set(x[2] for x in blocked)),"page_errors":errors,"console":messages})
     print("CASE",l,width,sum(c.values()),"/",len(c),"FAIL",[k for k,v in c.items() if not v],flush=True)
  finally:browser.close()
 passed=sum(tests.values())+sum(sum(c["tests"].values()) for c in cases);total=len(tests)+sum(len(c["tests"]) for c in cases)
 ok=len(cases)==6 and all(tests.values()) and all(c["pass"] for c in cases)
 report={"scope":"OWNER_R13_ISOLATED_BROWSER_QA","created_utc":datetime.now(timezone.utc).isoformat(),"base":BASE,"inventory_sha256":INVENTORY,"parent_config_sha256":CONFIG,"chromium":version,"checks":tests,"browser_cases":cases,"passed":passed,"total":total,"all_pass":ok,"release_approval":False,"limitations":"Simulated clean routes and exact global parent CSP; original live runtime blocked. No deployment, Vercel route proof, independent review, Next parity, full preflight, accessibility or release admission."}
 out.mkdir(parents=True,exist_ok=False);b=(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode()
 (out/"QA.json").write_bytes(b)
 print("RESULT","PASS" if ok else "REVISE",passed,"/",total,"SHA256",sha(b),flush=True)
 return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for k in ("candidate","config","r10","r12","parent-assets","browser","output"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve();need(not out.exists() and all(out!=x.resolve() and x.resolve() not in out.parents for x in (a.candidate,a.r10,a.r12)),"external new output")
 sys.exit(run(a.candidate,a.config,a.r10,a.r12,a.parent_assets,a.browser,out))
