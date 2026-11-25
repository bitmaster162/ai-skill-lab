"""Daily R2 combined-source and browser verification.
python verify_combined.py --evidence-root <Phuket evidence> --candidate <R2 candidate> --browser <Chromium> --output <new dir>
Direct Node source checks; no Next build or deployment.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
PIN="3dcc7d9c931f519f5c12fb12aa7a30bc7f529924688a76134b79ea012630f4dc"
R1_VERIFY="b0d3a0b3dc0ed19765c1c594e1d681889d05c2c9be543f1ec0fb18b9724ccdc2"
R14="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e"
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def run(root,c,browser,out):
 m=json.loads(checked(c/"COMBINED_DRAFT.json",PIN))
 need(m["scope"]=="DAILY_R2_COMBINED_REVIEW_ONLY" and not m["release_approval"],"draft")
 for n,v in m["patch_files"].items():
  path=c/"static"/n[len("deploy/live/"):] if n.startswith("deploy/live/") else c/"next"/n
  need(sha(path.read_bytes())==v["sha256"] and path.stat().st_size==v["bytes"],"candidate file "+n)
  need(path.read_bytes()==(c/"apply_check"/n).read_bytes(),"patch postimage "+n)
 r14=root/"L12_NEXT_PARITY_R14_20261126"/"candidate"
 prior=json.loads(checked(r14/"NEXT_DRAFT.json",R14))
 for n,v in prior["input_blobs"].items():need(blob((r14/"inputs"/n).read_bytes())==v,"source input "+n)
 # Execute original pure helpers and combined gateway composition. Substitute
 # only the JSON import in memory with the verified identical input.
 js="""import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';import {stripTypeScriptTypes} from 'node:module';import {createHash} from 'node:crypto';
const root=process.argv[1],r14=process.argv[2],m=JSON.parse(fs.readFileSync(path.join(root,'COMBINED_DRAFT.json'),'utf8'));
const read=(n)=>fs.readFileSync(path.join(r14,'inputs',n),'utf8');
const load=async(s)=>import('data:text/javascript;base64,'+Buffer.from(stripTypeScriptTypes(s,{mode:'strip'})).toString('base64'));
const {phuketUniverseMarkup}=await load(read('components/phuketUniverseMarkup.ts'));
const {withAgencyPilotTerms}=await load(read('components/phuketUniverseAgencyTerms.ts'));
const {withUniverseU3}=await load(read('components/phuketUniverseU3.ts'));
const importLine='import sections from "../data/phuket_housing_r6_sections.json";';
const hs=read('components/phuketHousingCatalog.ts');
if(hs.split(importLine).length!==2)throw Error('JSON import boundary');
const {withHousingCatalog}=await load(hs.replace(importLine,'const sections = '+read('data/phuket_housing_r6_sections.json').trim()+';'));
const next=n=>import(pathToFileURL(path.join(root,'next',n)).href);
const {withRentalJourney}=await next('components/phuketRentalJourney.ts');
const {withDailyEssentials}=await next('components/phuketDailyEssentials.ts');
const checks={};
const rejects=fn=>{try{fn();return false}catch{return true}};
const section=(s,id)=>{const i=s.indexOf('id="'+id+'"'),a=s.lastIndexOf('<section ',i),b=s.indexOf('</section>',i)+10;if(i<0||a<0||b<i)throw Error('section boundary');return s.slice(a,b)};
const sha=b=>createHash('sha256').update(b).digest('hex');
for(const l of ['ru','en']){
 const pre=withRentalJourney(withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[l],l),l),l),l);
 const after=withDailyEssentials(pre,l),g=m.gateways[l];
 const html=fs.readFileSync(path.join(root,'static',l==='en'?'en/phuket-universe.html':'phuket-universe.html'),'utf8');
 checks[l+'_daily_exact']=section(after,'daily-essentials')===section(html,'daily-essentials')&&after.split(g).length===2;
 checks[l+'_housing_exact']=section(after,'homes')===section(html,'homes');
 checks[l+'_only_daily_inserted']=after.replace(g,'')===pre;
 checks[l+'_duplicate_rejected']=rejects(()=>withDailyEssentials(after,l));
 checks[l+'_missing_marker_rejected']=rejects(()=>withDailyEssentials(pre.replace('id="agencies"','id="missing"'),l));
 checks[l+'_locale_rejected']=rejects(()=>withDailyEssentials(pre,'xx'));
}
const walk=dir=>fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);
const handlers=walk(path.join(root,'next','app')).filter(n=>n.endsWith(path.sep+'route.ts'));
if(handlers.length!==12)throw Error('handler inventory');
for(const n of handlers){
 const rel=path.relative(path.join(root,'next'),n).replaceAll('\\\\','/');
 const route='/'+rel.replace(/^app\\/\\((ru|en)\\)\\//,'').replace(/\\/route\\.ts$/,'');
 const mod=await import(pathToFileURL(n).href),res=mod.GET(),bytes=Buffer.from(await res.arrayBuffer());
 const expected=fs.readFileSync(path.join(root,'static',route.slice(1)+'.html'));
 const row=m.daily_routes.find(x=>x.route===route);
 const csp=res.headers.get('Content-Security-Policy')||'';
 checks['handler:'+route]=bytes.equals(expected)&&res.status===200&&res.headers.get('X-Robots-Tag')==='noindex, nofollow'&&res.headers.get('Cache-Control')==='no-store'&&csp.includes("default-src 'none'")&&csp.includes("connect-src 'none'")&&csp.includes("frame-ancestors 'none'")&&(!row||(sha(bytes)===row.body_sha256&&Object.entries(row.headers).every(([k,v])=>res.headers.get(k)===v)));
}
const comp=fs.readFileSync(path.join(root,'next','components','PhuketUniverse.tsx'),'utf8');
checks.component_wrapper=comp.includes('import { withDailyEssentials } from "@/components/phuketDailyEssentials";')&&comp.includes('const markup = withDailyEssentials(withRentalJourney(withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale), locale), locale), locale);');
console.log(JSON.stringify(checks));"""
 z=subprocess.run(["node","--input-type=module","-e",js,str(c),str(r14)],capture_output=True,timeout=40)
 if z.returncode:raise ValueError(z.stderr.decode(errors="replace")[-2000:])
 tests=json.loads(z.stdout);need(len(tests)==25 and all(tests.values()),"source QA "+str(tests))
 print("NODE",sum(tests.values()),"/",len(tests),flush=True)
 # Reuse the exact R1 browser checks with only the package inventory adapter.
 # The old test code and prior artifacts remain unchanged.
 v=checked(root/"L12_DAILY_ESSENTIALS_R1_20261126"/"verify_daily.py",R1_VERIFY).decode()
 def replace(old,new):
  nonlocal v
  need(v.count(old)==1,"test adapter boundary "+old[:80]);v=v.replace(old,new,1)
 replace("c13717ecafb21cb37ce53e282383c67c2df0b27a24617182d92057364781a36a",PIN)
 replace('c/"DAILY_DRAFT.json"','c/"COMBINED_DRAFT.json"')
 replace('len(files)==120','len(files)==140')
 replace('m["candidate_payload_sha256"]','m["static_payload"]')
 replace('for n,v in m["delta"].items():need(sha(files[n])==v["sha256"] and (c/"overlay"/n).read_bytes()==files[n],"delta")','for n in m["incremental_static"]:need(sha(files[n])==m["patch_files"]["deploy/live/"+n]["sha256"],"incremental static")')
 replace("OWNER_DAILY_R1_ISOLATED_BROWSER_QA","OWNER_DAILY_R2_COMBINED_BROWSER_QA")
 replace("No real deployment, actual Next equivalent, full preflight, independent review or release admission.","No actual Next build/router, full preflight, independent review or release admission.")
 out.mkdir(parents=True,exist_ok=False)
 ns={"__name__":"pinned_r1_browser_adapter"};exec(compile(v,"daily_browser_adapter.py","exec"),ns)
 status=ns["run"](c,browser,out/"browser")
 b=json.loads((out/"browser"/"QA.json").read_bytes())
 total=len(tests)+b["total"];passed=sum(tests.values())+b["passed"];ok=status==0 and b["all_pass"] and passed==total
 report={"scope":"OWNER_DAILY_R2_COMBINED_QA","report_sha256":PIN,"source_checks":tests,"browser_qa_sha256":sha((out/"browser"/"QA.json").read_bytes()),"passed":passed,"total":total,"all_pass":ok,"release_approval":False,"limitations":"R14 pure source composition and direct Node handlers; R1 browser verifier reused with exact combined inventory adapter. No actual Next build/router, deployment, full preflight, independent review or release admission."}
 raw=(json.dumps(report,indent=2,sort_keys=True)+"\n").encode();(out/"QA.json").write_bytes(raw)
 print("COMBINED_QA","PASS" if ok else "REVISE",passed,"/",total,"SHA256",sha(raw),flush=True)
 return 0 if ok else 1
if __name__=="__main__":
 p=argparse.ArgumentParser(description=__doc__)
 for k in ("evidence-root","candidate","browser","output"):p.add_argument("--"+k,type=Path,required=True)
 a=p.parse_args();out=a.output.resolve()
 need(not out.exists() and a.candidate.resolve() not in out.parents,"new output")
 sys.exit(run(a.evidence_root,a.candidate,a.browser,out))
