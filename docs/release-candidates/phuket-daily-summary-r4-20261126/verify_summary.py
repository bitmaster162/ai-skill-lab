"""R4 QA: replay pinned R3 tests and add summary regression assertions.
python verify_summary.py --candidate <R4> --r3 <R3> --verifier <R3 revised verifier> --browser <Chromium> --output <new dir>
"""
import argparse,hashlib,json,sys
from pathlib import Path
R3_VERIFIER="fe9d22c861a570d464be602b36bdddf4cd8b3daaf13ac4bc79f614c9130e2c15"
R3_REPORT="98e74e68e4a522df49037e755a80550ffcf3b1bfd14abb535b9067f36839bdd3"
PIN="d4cfba7e4e579b491384a61bdbef5d9ec60f5bb5b16b0d31b5351aea47c47aa0"
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("candidate","r3","verifier","browser","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=p.resolve() and p.resolve() not in out.parents for p in (a.candidate,a.r3)),"new output")
 src=a.verifier.read_bytes();need(sha(src)==R3_VERIFIER,"pinned prior tests")
 s=src.decode()
 def replace(old,new):
  nonlocal s
  need(s.count(old)==1,"unique adapter boundary "+old[:100])
  s=s.replace(old,new,1)
 replace(R3_REPORT,PIN)
 replace('R2="3dcc7d9c931f519f5c12fb12aa7a30bc7f529924688a76134b79ea012630f4dc"', 'R2="'+R3_REPORT+'"')
 replace('c/"BUDGET_DRAFT.json"','c/"SUMMARY_DRAFT.json"')
 replace('prior/"COMBINED_DRAFT.json"','prior/"BUDGET_DRAFT.json"')
 replace('len(old)==140','len(old)==144')
 replace('len(old_next)==28','len(old_next)==32')
 replace('OWNER_DAILY_BUDGET_R3_QA','OWNER_DAILY_SUMMARY_R4_QA')
 replace('checks["seven_inputs"]=page.locator("[data-amount]").count()==7 and all(g(k).count()==1 for k in KEYS)', '''checks["seven_inputs"]=page.locator("[data-amount]").count()==7 and all(g(k).count()==1 for k in KEYS)
       checks["six_status_controls"]=page.locator("[data-errand-state]").count()==6 and all(g(k+"-state").count()==1 for k in KEYS[1:])
       checks["status_labels"]=page.locator("[data-errand-state]").evaluate_all("(es)=>es.every(e=>e.labels.length===1&&e.options.length===4)")''')
 replace('setv("budget","100");setv("food","0,10");setv("laundry","0.20")','''note=lambda:g("summary-text").input_value().splitlines()
        field_label=lambda k:page.locator('label[for="'+k+'"]').inner_text()
        choice=lambda k:g(k+"-state").locator("option:checked").inner_text()
        row=lambda k,v:field_label(k)+": "+choice(k)+" | "+v
        unknown=g("summary").get_attribute("data-unknown")
        invalid=g("summary").get_attribute("data-invalid")
        checks["summary_initial_unknown"]=len(note())==11 and g("summary-text").get_attribute("readonly") is not None and all(row(k,unknown) in note() for k in KEYS[1:])
        g("food-state").select_option("1");g("work-state").select_option("2");g("transport-state").select_option("3")
        checks["status_only_summary"]=row("food",unknown) in note() and row("work",unknown) in note() and row("transport",unknown) in note() and not g("reset").is_disabled() and value("remaining")==chr(8212)
        setv("budget","100");setv("food","0,10");setv("laundry","0.20")''')
 replace('for k in KEYS[3:]:setv(k,"0")','''checks["partial_summary"]=row("food",money(.1)) in note() and row("laundry",money(.2)) in note() and row("work",unknown) in note() and g("summary").get_attribute("data-remaining")+": "+unknown in note()
        for k in KEYS[3:]:setv(k,"0")''')
 replace('setv("transport","99.71")','''checks["complete_summary"]=g("summary").get_attribute("data-remaining")+": "+money(99.7) in note() and row("transport",money(0)) in note()
        g("food-state").select_option("3");checks["status_does_not_change_amounts"]=row("food",money(.1)) in note() and value("remaining")==money(99.7)
        setv("transport","99.71")''')
 replace('setv("transport","0")','''checks["invalid_summary_safe"]=row("transport",invalid) in note() and "10000000.01" not in g("summary-text").input_value() and g("summary").get_attribute("data-remaining")+": "+unknown in note()
        setv("transport","0")''')
 replace('else:\n        g("budget").fill("100");g("food").fill("0")',''' checks["reset_status_and_summary"]=all(g(k+"-state").input_value()=="0" for k in KEYS[1:]) and all(row(k,unknown) in note() for k in KEYS[1:])
       else:
        g("food-state").select_option("1");checks["nojs_status"]=g("food-state").input_value()=="1" and not g("summary").is_visible()
        g("budget").fill("100");g("food").fill("0")''')
 # The adapted tests are inspectable and the original verifier remains untouched.
 out.mkdir(parents=True,exist_ok=False);raw=s.encode()
 with (out/"adapted_verifier.py").open("xb") as f:f.write(raw)
 ns={"__name__":"pinned_r3_adapter"};exec(compile(raw,"adapted_verifier.py","exec"),ns)
 result=ns["run"](a.candidate,a.r3,a.browser,out/"browser")
 q=(out/"browser"/"QA.json").read_bytes();m=json.loads(q)
 report={"scope":"OWNER_DAILY_SUMMARY_R4_QA","report_sha256":PIN,"adapted_verifier_sha256":sha(raw),"browser_qa_sha256":sha(q),"passed":m["passed"],"total":m["total"],"all_pass":result==0 and m["all_pass"],"release_approval":False,"limitations":"R3 arithmetic tests replayed with pinned inventory adapter and added summary/status tests; direct Node handler checks and isolated Chromium. No actual Next build/router, full preflight, independent or release acceptance."}
 b=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode()
 with (out/"QA.json").open("xb") as f:f.write(b)
 print("SUMMARY_QA","PASS" if report["all_pass"] else "REVISE",m["passed"],"/",m["total"],"SHA256",sha(b),flush=True)
 return 0 if report["all_pass"] else 1
if __name__=="__main__":sys.exit(main())
