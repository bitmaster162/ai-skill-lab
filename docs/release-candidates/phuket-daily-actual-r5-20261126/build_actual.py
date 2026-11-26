"""R5 actual-versus-planned daily spending, exact R4 review candidate.
python build_actual.py --evidence-root <Phuket evidence> --repo <Git store> --output <new directory>
Incremental review patch, not a release or main checkout edit.
"""
import argparse,base64,hashlib,json,os,subprocess
from pathlib import Path
from html import escape
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R4="d4cfba7e4e579b491384a61bdbef5d9ec60f5bb5b16b0d31b5351aea47c47aa0"
R3="98e74e68e4a522df49037e755a80550ffcf3b1bfd14abb535b9067f36839bdd3"
R2="3dcc7d9c931f519f5c12fb12aa7a30bc7f529924688a76134b79ea012630f4dc"
PAYLOAD="553631d4ed5d1112fdb876d932cc5249afe4b3aa1d59ee88e9e04e43eff0a9e0"
BUILDER="5fdc8272cbf1b38e937bb3fa70a5b72fb7ba2e5205287642d06bd8cffa998f04"
PATCHER="6e5a6e24f63bf5ae9012725254ea10ea5c1a177b9584891cd2708122e7a5902b"
JS="phuket-daily-assets/budget.js"
COPY={
"ru":{"plan":"План","actual":"Фактически потрачено","intro":"Укажите фактические расходы отдельно от плана. Выполненное дело не подтверждает оплату. Заполняйте только расходы за выбранный день; неизвестное оставьте пустым, а отсутствие расходов обозначьте 0.","title":"Фактические расходы за день","known":"Известные фактические расходы","missing":"Фактических сумм неизвестно","invalid":"Некорректные фактические суммы","remaining":"Остаток после фактических расходов","delta":"Факт минус план","help":"Отклонение рассчитывается только при заполнении всех шести плановых и фактических сумм. Положительное значение — потрачено больше плана, отрицательное — меньше.","reset":"Очистить все суммы и отметки","plan_known":"Известные плановые расходы","plan_remaining":"Плановый остаток лимита"},
"en":{"plan":"Planned","actual":"Actually spent","intro":"Enter actual expenses separately from the plan. A completed errand does not prove payment. Include only expenses for the selected day; leave unknown amounts blank and enter 0 for no expense.","title":"Actual daily spending","known":"Known actual expenses","missing":"Unknown actual amounts","invalid":"Invalid actual amounts","remaining":"Remaining after actual spending","delta":"Actual minus planned","help":"Variance is calculated only when all six planned and actual amounts are valid. A positive value means spending exceeded the plan; a negative value means spending was below it.","reset":"Clear all amounts and choices","plan_known":"Known planned expenses","plan_remaining":"Remaining planned limit"}}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def once(s,a,b):
 need(s.count(a)==1,"unique edit "+a[:100]);return s.replace(a,b,1)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("evidence-root","repo","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();root=a.evidence_root.resolve();repo=a.repo.resolve();out=a.output.resolve()
 need(not out.exists() and out!=root and out!=repo and repo not in out.parents,"new output")
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*v,cwd=None):return subprocess.check_output(["git","--no-optional-locks",*v],env=env,cwd=cwd,timeout=30,stderr=subprocess.STDOUT)
 need(git("-C",str(repo),"rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 prior=root/"L12_DAILY_SUMMARY_R4_20261126"/"candidate";p3=root/"L12_DAILY_BUDGET_R3_20261126"
 m=json.loads(checked(prior/"SUMMARY_DRAFT.json",R4))
 m3=json.loads(checked(p3/"candidate/BUDGET_DRAFT.json",R3))
 m2=json.loads(checked(root/"L12_DAILY_NEXT_R2_20261126/candidate/COMBINED_DRAFT.json",R2))
 need(all(x["base"]==BASE and not x["release_approval"] for x in (m,m3,m2)),"draft scope")
 ns={"__name__":"pinned_builder"};exec(compile(checked(p3/"build_budget.py",BUILDER),"budget.py","exec"),ns)
 static=ns["read"](prior/"static");nxt=ns["read"](prior/"next")
 need(len(static)==144 and ns["digest"](static)==PAYLOAD and len(nxt)==32,"R4 payload")
 pins={**m2["patch_files"],**m3["patch_files"],**m["patch_files"]}
 need({n for n in pins if not n.startswith("deploy/live/")}==set(nxt),"Next inventory")
 for n,v in pins.items():
  b=static[n[12:]] if n.startswith("deploy/live/") else nxt[n]
  need(sha(b)==v["sha256"] and blob(b)==v["git_blob"],"R4 source "+n)
 s=static[JS].decode()
 s=once(s,'const output=(id,value)=>','const actual=[...document.querySelectorAll("[data-actual]")],actualBox=document.getElementById("actual-results");const output=(id,value)=>')
 # Use the original strict integer-satang parser for the independent actual values.
 add='''const ap=actual.map(parse),av=ap.filter(x=>x.kind==="valid"),at=av.reduce((a,b)=>a+b.value,0),ac=ap.every(x=>x.kind==="valid"),pc=items.every(x=>x.kind==="valid"),ar=ac&&parsed[0].kind==="valid"?parsed[0].value-at:null,variance=ac&&pc?at-total:null;output("actual-known",av.length?money(at):"—");output("actual-missing",String(ap.filter(x=>x.kind==="unknown").length));output("actual-invalid",String(ap.filter(x=>x.kind==="invalid").length));output("actual-remaining",ar===null?"—":money(ar));output("actual-delta",variance===null?"—":money(variance));const arows=ap.map((p,i)=>label(actual[i])+": "+display(p));summary.value+="\\n"+[actualBox.dataset.title,...arows,actualBox.dataset.known+": "+(av.length?money(at):meta.dataset.unknown),actualBox.dataset.remaining+": "+(ar===null?meta.dataset.unknown:money(ar)),actualBox.dataset.delta+": "+(variance===null?meta.dataset.unknown:money(variance))].join("\\n");'''
 add=add.replace('"\n"','"\\n"')
 s=once(s,'reset.disabled=fields.every(e=>e.value==="")&&states.every(e=>e.value==="0")}',add+'reset.disabled=[...fields,...actual].every(e=>e.value==="")&&states.every(e=>e.value==="0")}')
 s=once(s,'for(const e of fields)e.addEventListener("input",update);','for(const e of [...fields,...actual])e.addEventListener("input",update);')
 s=once(s,'for(const e of fields)e.value="";','for(const e of [...fields,...actual])e.value="";')
 js=s.encode();new=dict(static);nn=dict(nxt);new[JS]=js;nn["public/"+JS]=js
 rows=[]
 for l in ("ru","en"):
  c=COPY[l];b=ns["COPY"][l];prefix=ns["prefix"](l);n=prefix[1:]+"/daily-budget.html";html=static[n].decode()
  html=once(html,"<fieldset>",'<p class="muted">'+escape(c["intro"])+'</p><fieldset>')
  for k,label in zip(ns["KEYS"][1:],b["labels"][1:]):
   marker=f'<label for="{k}">{escape(label)}</label>'
   html=once(html,marker,f'<label for="{k}">{escape(label)} — {escape(c["plan"])}</label>')
   marker=f'<input id="{k}" data-amount="" type="text" inputmode="decimal" autocomplete="off" maxlength="11" aria-describedby="units">'
   actual=f'<label for="{k}-actual">{escape(label)} — {escape(c["actual"])}</label><input id="{k}-actual" data-actual="" type="text" inputmode="decimal" autocomplete="off" maxlength="11" aria-describedby="units">'
   html=once(html,marker,marker+actual)
  # The old labels occur both in visible outputs and in summary data attributes.
  for key,repl in (("known","plan_known"),("remaining","plan_remaining")):
   original=escape(b[key]);replacement=escape(c[repl]);need(html.count(original)==2,"plan labels")
   html=html.replace(original,replacement)
  attrs=" ".join(f'data-{k}="{escape(c[k],quote=True)}"' for k in ("title","known","remaining","delta"))
  outputs="".join(f'<div><span>{escape(c[k])}</span><output id="actual-{k}">—</output></div>' for k in ("known","missing","invalid","remaining","delta"))
  section=f'<section id="actual-results" aria-labelledby="actual-title" {attrs}><h2 id="actual-title">{escape(c["title"])}</h2><div class="result" aria-live="polite">{outputs}</div><p class="muted">{escape(c["help"])}</p></section>'
  html=once(html,'<div id="summary" class="summary"',section+'<div id="summary" class="summary"')
  reset="Очистить суммы и отметки" if l=="ru" else "Clear amounts and choices"
  html=once(html,'>'+escape(reset)+'</button>','>'+escape(c["reset"])+'</button>')
  oldhash=ns["sri"](static[JS]);newhash=ns["sri"](js);need(html.count(oldhash)==2,"CSP/SRI pins")
  html=html.replace(oldhash,newhash);raw=html.encode();new[n]=raw
  h=next(x["handler"] for x in m["routes"] if x["html_path"]==n)
  source=nxt[h].decode();mark="return new Response(";i=source.index(mark)+len(mark);body,z=json.JSONDecoder().raw_decode(source[i:])
  need(body.encode()==static[n],"handler preimage")
  tail=once(source[i+z:],oldhash,newhash);nn[h]=(source[:i]+ns["literal"](html)+tail).encode()
  rows.append({"html_path":n,"handler":h,"route":prefix+"/daily-budget","body_sha256":sha(raw)})
 sd={n for n in new if new[n]!=static[n]};nd={n for n in nn if nn[n]!=nxt[n]}
 need(len(sd)==len(nd)==3 and set(new)==set(static) and set(nn)==set(nxt),"six replacements")
 files={**{"deploy/live/"+n:new[n] for n in sd},**{n:nn[n] for n in nd}}
 old={**{"deploy/live/"+n:static[n] for n in sd},**{n:nxt[n] for n in nd}}
 patcher={"__name__":"pinned_patch"};exec(compile(checked(root/"L12_TOOLKIT_REVIEW_R22_20261126/build_review_patch.py",PATCHER),"patcher.py","exec"),patcher)
 patch=b"".join(patcher["patch_for"](n,old[n],b) for n,b in sorted(files.items()))
 out.mkdir(parents=True,exist_ok=False);write=patcher["write"]
 write(out/"static",new);write(out/"next",nn);write(out,{"daily-actual.patch":patch,"patch.b64":base64.encodebytes(patch)})
 work=out/"apply_check";work.mkdir();write(work,old)
 args=("apply","--whitespace=nowarn");git(*args,"--check",str(out/"daily-actual.patch"),cwd=work);git(*args,str(out/"daily-actual.patch"),cwd=work)
 need(patcher["read"](work)==files,"exact postimages");git(*args,"--reverse","--check",str(out/"daily-actual.patch"),cwd=work)
 report={"scope":"DAILY_ACTUAL_R5_REVIEW_ONLY","base":BASE,"r4_report_sha256":R4,"prior_payload":PAYLOAD,"static_payload":ns["digest"](new),"static_files":len(new),"next_files":len(nn),"routes":rows,"patch_sha256":sha(patch),"patch_git_blob":blob(patch),"patch_files":{n:{"sha256":sha(b),"bytes":len(b),"git_blob":blob(b)} for n,b in sorted(files.items())},"release_approval":False,"limitations":"Incremental patch against R4, not main. Actual amounts are user entries, not independently verified payments. No app storage or external submission. Actual Next build, full preflight, visual/independent acceptance and release admission remain open."}
 raw=(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode();write(out,{"ACTUAL_DRAFT.json":raw})
 print("ACTUAL",len(files),"patch files",report["static_payload"],"report",sha(raw),"patch",sha(patch),"blob",blob(patch),"base64 lines",len(base64.encodebytes(patch).splitlines()),"base64 chars",len(base64.b64encode(patch)),flush=True)
if __name__=="__main__":main()
