"""R5 owner QA, replay pinned R4 tests plus actual spending checks."""
import argparse,hashlib,json,sys
from pathlib import Path
PIN="92160c843701bb54dee77b56aa659707a2cf8630cd71d7a4ac0942023cd409d1"
R4="d4cfba7e4e579b491384a61bdbef5d9ec60f5bb5b16b0d31b5351aea47c47aa0"
VERIFIER="f418b4ed573df40f60f4fd23aae31b6f84fd26141924764765092b1cb3b2bcd4"
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("candidate","r4","verifier","browser","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and all(out!=p.resolve() and p.resolve() not in out.parents for p in (a.candidate,a.r4)),"new output")
 raw=a.verifier.read_bytes();need(sha(raw)==VERIFIER,"exact prior tests")
 s=raw.decode()
 def replace(old,new):
  nonlocal s
  need(s.count(old)==1,"adapter boundary "+old[:90]);s=s.replace(old,new,1)
 replace('PIN="'+R4+'"','PIN="'+PIN+'"')
 replace('R2="98e74e68e4a522df49037e755a80550ffcf3b1bfd14abb535b9067f36839bdd3"','R2="'+R4+'"')
 replace('c/"SUMMARY_DRAFT.json"','c/"ACTUAL_DRAFT.json"')
 replace('prior/"BUDGET_DRAFT.json"','prior/"SUMMARY_DRAFT.json"')
 replace('OWNER_DAILY_SUMMARY_R4_QA','OWNER_DAILY_ACTUAL_R5_BROWSER_QA')
 replace('len(note())==11','len(note())==21')
 replace('       checks["status_labels"]=', '''       checks["actual_inputs"]=page.locator("[data-actual]").count()==6 and all(g(k+"-actual").count()==1 for k in KEYS[1:])
       checks["actual_labels"]=page.locator("[data-actual]").evaluate_all("(es)=>es.every(e=>e.labels.length===1)")
       checks["status_labels"]=''')
 # Add a fresh actual-spend scenario after the unchanged R4 reset checks.
 marker='       else:\n        g("food-state").select_option("1")'
 extra='''        dash=chr(8212)
        actual_line=lambda k,v:field_label(k+"-actual")+": "+v
        actual_label=lambda k:g("actual-results").get_attribute("data-"+k)
        checks["initial_actual_unknown"]=value("actual-known")==value("actual-remaining")==value("actual-delta")==dash and value("actual-missing")=="6" and value("actual-invalid")=="0" and all(actual_line(k,unknown) in note() for k in KEYS[1:])
        g("food-state").select_option("3")
        checks["done_not_paid"]=g("food-actual").input_value()=="" and value("actual-known")==dash and value("actual-missing")=="6"
        setv("budget","100");setv("food","10")
        for k in KEYS[2:]:setv(k,"0")
        setv("food-actual","0,10");setv("laundry-actual","0.20")
        checks["partial_actual"]=value("actual-known")==money(.3) and value("actual-missing")=="4" and value("actual-remaining")==value("actual-delta")==dash
        checks["plan_unaffected"]=value("known")==money(10) and value("remaining")==money(90)
        for k in KEYS[3:]:setv(k+"-actual","0")
        checks["actual_exact"]=value("actual-known")==money(.3) and value("actual-remaining")==money(99.7) and value("actual-delta")==money(-9.7)
        checks["actual_summary"]=actual_line("food",money(.1)) in note() and actual_label("remaining")+": "+money(99.7) in note() and actual_label("delta")+": "+money(-9.7) in note()
        setv("transport-actual","9.71")
        checks["positive_variance_satang"]=value("actual-known")==money(10.01) and value("actual-delta")==money(.01)
        setv("transport-actual","99.71")
        checks["actual_over_limit"]=value("actual-known")==money(100.01) and value("actual-remaining")==money(-.01) and value("actual-delta")==money(90.01)
        setv("budget","")
        checks["variance_without_limit"]=value("actual-remaining")==dash and value("actual-delta")==money(90.01)
        setv("budget","100");setv("food","")
        checks["actual_independent_of_plan"]=value("actual-remaining")==money(-.01) and value("actual-delta")==dash
        setv("food","10")
        for key,bad in (("negative","-1"),("exponent","1e3"),("thousands","1 000"),("precision","0.001"),("bound","10000000.01")):
         setv("transport-actual",bad);checks["actual_reject_"+key]=g("transport-actual").get_attribute("aria-invalid")=="true" and value("actual-invalid")=="1" and value("actual-remaining")==value("actual-delta")==dash and value("remaining")==money(90)
        checks["invalid_actual_safe_summary"]=actual_line("transport",invalid) in note() and "10000000.01" not in g("summary-text").input_value()
        setv("transport-actual","0")
        checks["actual_recovery"]=value("actual-invalid")=="0" and value("actual-remaining")==money(99.7) and g("transport-actual").get_attribute("aria-invalid") is None
        for k in KEYS[1:]:setv(k+"-actual","10000000")
        checks["actual_max_exact"]=value("actual-known")==money(60000000) and value("actual-remaining")==money(-59999900)
        g("reset").click()
        checks["actual_reset"]=all(g(k+"-actual").input_value()=="" for k in KEYS[1:]) and value("actual-known")==dash and value("actual-missing")=="6" and g("reset").is_disabled() and all(actual_line(k,unknown) in note() for k in KEYS[1:])
        setv("food-actual","0")
        checks["actual_zero_only"]=value("actual-known")==money(0) and value("actual-missing")=="5" and not g("reset").is_disabled()
        g("reset").click()
'''
 replace(marker,extra+marker)
 replace('        checks["nojs_native"]=', '''        g("food-actual").fill("0")
        checks["nojs_actual"]=g("food-actual").input_value()=="0" and not g("actual-results").is_visible()
        checks["nojs_native"]=''')
 out.mkdir(parents=True,exist_ok=False);adapted=s.encode();compile(adapted,"adapted.py","exec")
 (out/"adapted_verifier.py").write_bytes(adapted)
 ns={"__name__":"pinned_r4_adapter"};exec(compile(adapted,"adapted.py","exec"),ns)
 status=ns["run"](a.candidate,a.r4,a.browser,out/"browser")
 b=(out/"browser/QA.json").read_bytes();q=json.loads(b)
 report={"scope":"OWNER_DAILY_ACTUAL_R5_QA","report_sha256":PIN,"adapted_verifier_sha256":sha(adapted),"browser_qa_sha256":sha(b),"passed":q["passed"],"total":q["total"],"all_pass":status==0 and q["all_pass"],"release_approval":False,"limitations":"Pinned R4 assertions plus actual expense scenarios, isolated Chromium and direct Node response checks. No actual Next build/router, full preflight, independent visual/accessibility or production acceptance."}
 rb=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode();(out/"QA.json").write_bytes(rb)
 print("ACTUAL_QA","PASS" if report["all_pass"] else "REVISE",q["passed"],"/",q["total"],"SHA256",sha(rb),flush=True)
 return 0 if report["all_pass"] else 1
if __name__=="__main__":sys.exit(main())
