"""R11 repeatable owner QA, not independent approval.
Run: python verify_review.py --runner <R10 review_bundle.py> --bundle <R10 bundle>
 --browser <installed Chromium> --output <new external directory>
Requires installed Python 3.10+ and Playwright. No fetch, install, or live traffic.
"""
import argparse,hashlib,html,http.client,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R10="4b40b89c0c9c533bcd34ee45e8b564ecdcb6743f"
RUNNER_SHA="600aaea9463fa3412230d46634cce1a3426981a594f266e1940840a6d1dd1ca8"
MANIFEST_SHA="13a0549668dea88764eecdb20862fb78ea2d5487fed8be2f89857cfadb221bbb"
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def write(root,name,b):
 p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("xb") as f:f.write(b)
def verify_inputs(runner,bundle):
 raw=runner.read_bytes();need(sha(raw)==RUNNER_SHA,"runner identity")
 mraw=(bundle/"REVIEW.json").read_bytes();need(sha(mraw)==MANIFEST_SHA,"manifest identity")
 m=json.loads(mraw);need(m["base"]==BASE and m["exact_match"]=="12/12","bundle identity")
 need(len(m["html"])==12 and len(m["assets"])==5 and len(m["source_blobs"])==len(m["earlier_sources"])==7,"inventory")
 pins={**{n:v["sha256"] for n,v in m["html"].items()},**m["assets"],"index.html":m["index_sha256"]}
 for name,pin in pins.items():need(sha((bundle/"preview"/name).read_bytes())==pin,"file identity "+name)
 ns={"__name__":"r10_pinned_review"};exec(compile(raw,"review_bundle.py","exec"),ns)
 need(len(ns["verified"](bundle))==21,"exact allowlist")
 return pins,ns
def rejected(fn):
 try:fn()
 except (ValueError,KeyError,FileNotFoundError):return True
 return False
def number(text):return int("".join(c for c in text if c.isdecimal() or c=="-"))
def local_http(port,path,method="GET",host=None):
 conn=http.client.HTTPConnection("127.0.0.1",port,timeout=5)
 try:
  conn.request(method,path,headers={"Host":host or f"127.0.0.1:{port}"})
  r=conn.getresponse();return r.status,dict(r.getheaders()),r.read()
 finally:conn.close()
def browser_case(browser,origin,l,width):
 ctx=browser.new_context(viewport={"width":width,"height":844},service_workers="block",locale="ru-RU" if l=="ru" else "en-US",reduced_motion="reduce")
 foreign=[];errors=[];tests={}
 def route(rt):
  if rt.request.url.startswith(origin+"/"):rt.continue_()
  else:foreign.append(rt.request.url);rt.abort()
 ctx.route("**/*",route);page=ctx.new_page();page.on("pageerror",lambda e:errors.append(str(e)))
 root="/preview-tools/"+l+"/rental-";other="en" if l=="ru" else "ru";parent="/phuket-universe" if l=="ru" else "/en/phuket-universe"
 guide=root+"journey.html";calc=root+"budget-calculator.html";short=root+"shortlist.html";movein=root+"move-in.html";moveout=root+"move-out.html"
 g=lambda k:page.locator("#"+k)
 def go(path):page.goto(origin+path,wait_until="load",timeout=12000)
 def follow(selector,path):
  a=page.locator(selector);a.focus();a.press("Enter");page.wait_for_url("**"+path,timeout=5000)
  return urlsplit(page.url).path==urlsplit(path).path
 def geometry():return page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
 try:
  go("/");tests["review_index"]=page.locator("tbody a").count()==12
  tests["index_geometry"]=geometry()
  tests["parent_route"]=follow(f'a[href="{parent}"]',parent)
  tests["empty_inventory"]=page.locator("[data-u2-card]").count()==0
  tests["guide_route"]=follow("#rental-journey-entry a",guide)
  tests["four_stages"]=page.locator("#rental-journey nav [role=group]").count()==4
  tests["all_nine_links"]=page.locator("#rental-journey nav a").count()==9
  tests["guide_geometry"]=geometry()
  tests["calculator_route"]=follow(f'#rental-journey nav a[href="{calc}"]',calc)
  g("example").click();tests["calculator_demo"]=[number(g(k).inner_text()) for k in ("monthly","upfront")]==[31000,86000]
  g("prepay").check();tests["prepay_adjustment"]=number(g("upfront").inner_text())==89000
  g("deposit").fill("-1");tests["calculator_invalid"]=g("monthly").inner_text()=="—" and g("upfront").inner_text()=="—"
  g("reset").click();tests["calculator_reset"]=all(g(k).input_value()=="" for k in ("rent","utilities","deposit","oneoff")) and not g("prepay").is_checked()
  tests["calculator_geometry"]=geometry()
  tests["shortlist_route"]=follow(f'.tool-nav a[href="{short}"]',short)
  tests["no_auto_transfer"]=g("budget").input_value()==""
  g("example").click();t=json.loads(g("copy").text_content());n=json.loads(g("note-copy").text_content())
  tests["shortlist_demo"]=g("summary1").inner_text()==t["matched"] and g("summary2").inner_text()==t["mismatch"]
  g("note-generate").click();tests["empty_selection"]=g("note-output").input_value()=="" and g("note-status").inner_text()==n["empty"]
  g("keep1").check();g("note-generate").click();note=g("note-output").input_value()
  tests["selected_only"]=t["option"]+" 1" in note and t["option"]+" 2" not in note and t["matched"] in note and n["warning"] in note
  g("note-select").click();tests["manual_selection"]=g("note-output").evaluate("(e)=>e.selectionStart===0&&e.selectionEnd===e.value.length")
  g("rent1").fill("");tests["stale_cleared"]=g("note-output").input_value()=="" and g("note-status").inner_text()==n["stale"]
  g("note-generate").click();tests["unknown_not_zero"]=t["rent"]+": "+t["unknown"] in g("note-output").input_value()
  g("rent1").fill("1e3");g("note-generate").click();tests["invalid_blocks_note"]=g("note-output").input_value()=="" and g("note-status").inner_text()==n["invalid"]
  g("reset").click();tests["shortlist_reset"]=g("note-output").input_value()=="" and g("count").inner_text().endswith("0 / 3")
  tests["shortlist_geometry"]=geometry()
  tests["return_guide_1"]=follow(f'.tool-nav a[href="{guide}"]',guide)
  tests["move_in_route"]=follow(f'#rental-journey nav a[href="{movein}"]',movein)
  counts=lambda:[int(x) for x in page.locator("[data-count]").all_text_contents()]
  tests["initial_move_in"]=counts()==[8,0,0,0]
  for i in range(1,9):g("item-"+str(i)).select_option(str((i-1)%4))
  tests["move_in_states"]=counts()==[2,2,2,2]
  g("reset").click();tests["move_in_reset"]=counts()==[8,0,0,0] and page.evaluate("document.activeElement.id")=="item-1"
  tests["move_in_geometry"]=geometry()
  tests["return_guide_2"]=follow(f'nav a[href="{guide}"]',guide)
  tests["move_out_route"]=follow(f'#rental-journey nav a[href="{moveout}"]',moveout)
  g("example").click();t2=json.loads(g("copy").text_content())
  tests["deposit_demo"]=[number(g(k).inner_text()) for k in ("expected","delta")]==[35000,5000] and g("status").inner_text()==t2["less"]
  g("received").fill("40000")
  tests["negative_delta"]=number(g("delta").inner_text())==-5000 and g("status").inner_text()==t2["more"]
  g("deductions").fill("40001")
  tests["excess_deduction"]=g("expected").inner_text()=="—" and g("status").inner_text()==t2["excess"]
  g("reset").click();tests["move_out_reset"]=g("expected").inner_text()=="—" and g("status").inner_text()==t2["unknown"]
  tests["move_out_geometry"]=geometry()
  tests["language_switch"]=follow("nav a[lang]","/preview-tools/"+other+"/rental-move-out.html") and page.locator("html").get_attribute("lang")==other
  tests["language_return"]=follow("nav a[lang]",moveout) and page.locator("html").get_attribute("lang")==l
  tests["no_storage"]=page.evaluate("localStorage.length===0&&sessionStorage.length===0")
  tests["no_forms"]=page.locator("form").count()==0
  tests["no_external_requests"]=not foreign
  tests["no_js_errors"]=not errors
  return {"locale":l,"width":width,"tests":tests,"pass":all(tests.values()),"blocked_external":foreign,"page_errors":errors}
 finally:ctx.close()
def dashboard(report):
 e=lambda s:html.escape(str(s))
 rows=[]
 for name,value in report["checks"].items():rows.append(f"<tr><td>{e(name)}</td><td>{'PASS' if value else 'FAIL'}</td></tr>")
 for c in report["browser_cases"]:
  name=c["locale"].upper()+" "+str(c["width"])+" px"
  rows.append(f"<tr><td>{e(name)}</td><td>{sum(c['tests'].values())}/{len(c['tests'])} {'PASS' if c['pass'] else 'FAIL'}</td></tr>")
  for name,value in c["tests"].items():
   if not value:rows.append(f"<tr><td>{e(name)}</td><td>FAIL</td></tr>")
 title="Owner QA — "+report["status"]
 return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+e(title)+'</title><style>body{margin:24px;background:#0d1320;color:#eef4fc;font:16px/1.6 system-ui,sans-serif}main{max-width:900px;margin:auto}table{border-collapse:collapse;width:100%}td,th{padding:9px;text-align:left;border-bottom:1px solid #61728a;overflow-wrap:anywhere}h1{line-height:1.2}</style></head><body><main><h1>'+e(title)+'</h1><p>'+e(report["passed"])+' / '+e(report["total"])+' actual checks passed. Exact R10 review bundle. Not independent or production approval.</p><p>'+e(report["limitations"])+'</p><table><thead><tr><th scope="col">Check</th><th scope="col">Result</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></main></body></html>\n').encode()
def run(runner,bundle,browser_path,out):
 pins,ns=verify_inputs(runner,bundle)
 out.mkdir(parents=True,exist_ok=False)
 tests={"pinned_inputs":True};cases=[];fatal=None;server=None
 try:
  bad=out/"negative_fixture";bad.mkdir()
  write(bad,"REVIEW.json",(bundle/"REVIEW.json").read_bytes())
  for name in pins:write(bad/"preview",name,(bundle/"preview"/name).read_bytes())
  target=bad/"preview"/"phuket-universe.html";target.write_bytes(target.read_bytes()+b" ")
  tests["modified_html_rejected"]=rejected(lambda:ns["verified"](bad))
  tests["strict_input_gate_rejects_modified_html"]=rejected(lambda:verify_inputs(runner,bad))
  target.write_bytes((bundle/"preview"/"phuket-universe.html").read_bytes())
  bad_manifest=bad/"REVIEW.json";bad_manifest.write_bytes(bad_manifest.read_bytes()+b" ")
  tests["modified_manifest_rejected"]=rejected(lambda:verify_inputs(runner,bad))
  server=subprocess.Popen([sys.executable,"-u",str(runner),"--serve",str(bundle),"--port","0"],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
  line=server.stdout.readline();match=re.search(r"http://127\.0\.0\.1:(\d+)/",line);need(match,"loopback startup")
  port=int(match.group(1));origin=f"http://127.0.0.1:{port}"
  for name,pin in pins.items():
   status,headers,b=local_http(port,"/"+name)
   tests["served:"+name]=status==200 and sha(b)==pin and headers.get("X-Robots-Tag")=="noindex,nofollow" and headers.get("Cache-Control")=="no-store"
  for path,name in [("/","index.html"),("/phuket-universe","phuket-universe.html"),("/en/phuket-universe","en/phuket-universe.html")]:
   status,headers,b=local_http(port,path)
   tests["alias:"+path]=status==200 and sha(b)==pins[name] and "connect-src 'none'" in headers.get("Content-Security-Policy","")
  for path in ("/REVIEW.json","/sources/runner.py","/../REVIEW.json","/_vercel/insights/script.js","/phuket-housing-u2.js","/phuket-universe?x=1"):
   tests["deny:"+path]=local_http(port,path)[0]==404
  tests["bad_host"]=local_http(port,"/",host="example.invalid")[0]==403
  tests["post_denied"]=local_http(port,"/",method="POST")[0]==501
  print("HTTP_AND_INTEGRITY",sum(tests.values()),"/",len(tests),flush=True)
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=str(browser_path),headless=True,args=["--disable-background-networking","--disable-component-update","--disable-sync","--no-first-run"])
   try:
    for l in ("ru","en"):
     for width in (320,390,1440):
      c=browser_case(browser,origin,l,width);cases.append(c)
      print("CASE",l,width,sum(c["tests"].values()),"/",len(c["tests"]),"FAILED",[k for k,v in c["tests"].items() if not v],flush=True)
   finally:browser.close()
 except Exception as exc:
  fatal=type(exc).__name__+": "+str(exc)
  print("FAIL",fatal,flush=True)
 finally:
  if server is not None:
   server.terminate()
   try:server.wait(timeout=5)
   except subprocess.TimeoutExpired:server.kill();server.wait(timeout=5)
   tests["server_stopped"]=server.poll() is not None
  else:tests["server_stopped"]=False
 total=len(tests)+sum(len(c["tests"]) for c in cases)
 passed=sum(tests.values())+sum(sum(c["tests"].values()) for c in cases)
 all_pass=not fatal and len(cases)==6 and all(tests.values()) and all(c["pass"] for c in cases)
 report={"scope":"OWNER_REPRODUCIBLE_R10_QA","base":BASE,"r10":R10,"created_utc":datetime.now(timezone.utc).isoformat(),"status":"PASS" if all_pass else "REVISE","checks":tests,"browser_cases":cases,"passed":passed,"total":total,"all_pass":all_pass,"fatal":fatal,"release_approval":False,"limitations":"Exact local preview only. Original runtime disabled. No full visual, screen-reader, independent, transfer/payload-budget or production acceptance."}
 write(out,"QA.json",(json.dumps(report,indent=2,ensure_ascii=False)+"\n").encode())
 write(out,"QA.html",dashboard(report))
 print("RESULT",report["status"],passed,"/",total,"SHA256",sha((out/"QA.json").read_bytes()),flush=True)
 return 0 if all_pass else 1
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--runner",required=True,type=Path);p.add_argument("--bundle",required=True,type=Path);p.add_argument("--browser",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 out=a.output.resolve();bundle=a.bundle.resolve();runner=a.runner.resolve()
 need(a.browser.is_file(),"installed Chromium executable required")
 need(not out.exists() and out!=bundle and bundle not in out.parents and runner.parent not in out.parents,"new output outside input directories")
 sys.exit(run(runner,bundle,a.browser.resolve(),out))
if __name__=="__main__":main()
