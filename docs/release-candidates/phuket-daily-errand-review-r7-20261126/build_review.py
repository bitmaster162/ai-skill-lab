import hashlib,json,os,subprocess
from pathlib import Path
from html import escape
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent/"candidate"
PIN="8813b0158b2e69d33383295b67fb87b92026ee79cb061be66b6f3329d0678fcc"
JS="phuket-daily-assets/budget.js"
def need(x,m):
 if not x:raise RuntimeError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def read(p,h):
 b=p.read_bytes();need(sha(b)==h,"pin "+str(p));return b
def load(p,h):return json.loads(read(p,h))
def once(s,a,b):
 need(s.count(a)==1,"edit "+a[:80]);return s.replace(a,b,1)
def helper(p,h):
 ns={"__name__":"pinned_helper"};exec(compile(read(p,h),str(p),"exec"),ns);return ns
def main():
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*v,cwd=None):return subprocess.check_output(["git","--no-optional-locks",*v],env=env,cwd=cwd,timeout=30)
 repo=ROOT/"L12_RENTAL_JOURNEY_GIT_CAPSULE_R4_20261126/objects.git"
 need(git("-C",str(repo),"rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 specs=[
 ("L12_DAILY_NEXT_R2_20261126","COMBINED_DRAFT.json","3dcc7d9c931f519f5c12fb12aa7a30bc7f529924688a76134b79ea012630f4dc"),
 ("L12_DAILY_BUDGET_R3_20261126","BUDGET_DRAFT.json","98e74e68e4a522df49037e755a80550ffcf3b1bfd14abb535b9067f36839bdd3"),
 ("L12_DAILY_SUMMARY_R4_20261126","SUMMARY_DRAFT.json","d4cfba7e4e579b491384a61bdbef5d9ec60f5bb5b16b0d31b5351aea47c47aa0"),
 ("L12_DAILY_ACTUAL_R5_20261126","ACTUAL_DRAFT.json","92160c843701bb54dee77b56aa659707a2cf8630cd71d7a4ac0942023cd409d1"),
 ("L12_DAILY_VARIANCE_R6_20261126","VARIANCE_DRAFT.json",PIN)]
 manifests=[load(ROOT/d/"candidate"/n,h) for d,n,h in specs];m=manifests[-1]
 prior=ROOT/specs[-1][0]/"candidate"
 ns=helper(ROOT/"L12_DAILY_BUDGET_R3_20261126/build_budget.py","5fdc8272cbf1b38e937bb3fa70a5b72fb7ba2e5205287642d06bd8cffa998f04")
 pa=helper(ROOT/"L12_TOOLKIT_REVIEW_R22_20261126/build_review_patch.py","6e5a6e24f63bf5ae9012725254ea10ea5c1a177b9584891cd2708122e7a5902b")
 need(all(x["base"]==BASE and not x["release_approval"] for x in manifests),"scope")
 old=ns["read"](prior/"static");on=ns["read"](prior/"next")
 need(len(old)==144 and len(on)==32 and ns["digest"](old)==m["static_payload"],"payload")
 pins={}
 for v in manifests:pins.update(v["patch_files"])
 need({n for n in pins if not n.startswith("deploy/live/")}==set(on),"Next inventory")
 for n,v in pins.items():
  b=old[n[12:]] if n.startswith("deploy/live/") else on[n]
  need(sha(b)==v["sha256"] and blob(b)==v["git_blob"],"preimage "+n)
 s=old[JS].decode()
 s=once(s,'const output=(id,value)=>','const review=document.getElementById("errand-review"),reviewGroups=[...review.querySelectorAll("[data-review-state]")];const output=(id,value)=>')
 add='const reviewLines=reviewGroups.map(g=>{const state=g.dataset.reviewState;const names=states.flatMap((e,i)=>e.value===state?[categoryRows[i].querySelector("span").textContent]:[]);const text=names.length?names.join("; "):review.dataset.none;g.querySelector("output").textContent=String(names.length);g.querySelector("[data-review-list]").textContent=text;return g.querySelector("[data-review-label]").textContent+" ("+names.length+"): "+text});review.hidden=false;summary.value+="\\n"+[review.dataset.title,...reviewLines].join("\\n");'
 s=once(s,'reset.disabled=[...fields,...actual]',add+'reset.disabled=[...fields,...actual]')
 js=s.encode();new=dict(old);nn=dict(on);new[JS]=js;nn["public/"+JS]=js
 copy={
 "ru":("Сводка дел на день","Распределение по вашим отметкам. Это не подтверждение выполненных работ или оплаты. Отложенные дела можно вручную перенести в следующий план; данные не переносятся автоматически.","Нет",("Сегодня","Позже","Готово","Не выбрано")),
 "en":("Daily errand review","Grouped by your own choices, not proof of completion or payment. You can manually carry later errands into a new plan; no automatic transfer takes place.","None",("Today","Later","Done","Not selected"))}
 routes=[]
 for l,row in zip(("ru","en"),m["routes"]):
  n=row["html_path"];h=row["handler"];title,help,none,labels=copy[l]
  parts=[]
  for state,label in zip(("1","2","3","0"),labels):
   parts.append(f'<div data-review-state="{state}"><span data-review-label>{escape(label)}</span><output id="review-count-{state}">—</output><p id="review-list-{state}" data-review-list class="muted">—</p></div>')
  section=f'<section id="errand-review" hidden aria-labelledby="review-title" data-title="{escape(title)}" data-none="{escape(none)}"><h2 id="review-title">{escape(title)}</h2><p class="muted">{escape(help)}</p><div aria-live="polite">{"".join(parts)}</div></section>'
  html=once(old[n].decode(),'<div id="summary" class="summary"',section+'<div id="summary" class="summary"')
  oh,nh=ns["sri"](old[JS]),ns["sri"](js);need(html.count(oh)==2,"SRI");html=html.replace(oh,nh);new[n]=html.encode()
  source=on[h].decode();mark="return new Response(";i=source.index(mark)+len(mark);body,z=json.JSONDecoder().raw_decode(source[i:]);need(body.encode()==old[n],"handler preimage")
  nn[h]=(source[:i]+ns["literal"](html)+once(source[i+z:],oh,nh)).encode()
  routes.append({**row,"body_sha256":sha(new[n])})
 sd={n for n in new if new[n]!=old[n]};nd={n for n in nn if nn[n]!=on[n]};need(len(sd)==len(nd)==3,"six replacements")
 files={**{"deploy/live/"+n:new[n] for n in sd},**{n:nn[n] for n in nd}}
 pre={**{"deploy/live/"+n:old[n] for n in sd},**{n:on[n] for n in nd}}
 patch=b"".join(pa["patch_for"](n,pre[n],b) for n,b in sorted(files.items()))
 need(not OUT.exists(),"new output");OUT.mkdir()
 write=pa["write"];write(OUT/"static",new);write(OUT/"next",nn);write(OUT,{"daily-errand-review.patch":patch})
 work=OUT/"apply_check";work.mkdir();write(work,pre)
 args=("apply","--whitespace=nowarn");git(*args,"--check",str(OUT/"daily-errand-review.patch"),cwd=work);git(*args,str(OUT/"daily-errand-review.patch"),cwd=work);need(pa["read"](work)==files,"postimages");git(*args,"--reverse","--check",str(OUT/"daily-errand-review.patch"),cwd=work)
 subprocess.check_call(["node","--check",str(OUT/"static"/JS)])
 report={"scope":"DAILY_ERRAND_REVIEW_R7_REVIEW_ONLY","base":BASE,"r6_report_sha256":PIN,"prior_payload":m["static_payload"],"static_payload":ns["digest"](new),"static_files":len(new),"next_files":len(nn),"routes":routes,"patch_sha256":sha(patch),"patch_files":{n:{"sha256":sha(b),"bytes":len(b),"git_blob":blob(b)} for n,b in sorted(files.items())},"release_approval":False,"limitations":"Incremental against R6, not main. Errand statuses are manual choices, not proof of completion or payment. No automatic carry-over. Actual Next build, independent review and release admission remain open."}
 raw=(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode();write(OUT,{"REVIEW_DRAFT.json":raw})
 print("R7 built",len(files),"replacements","manifest",sha(raw),"patch",sha(patch),"payload",report["static_payload"],flush=True)
if __name__=="__main__":main()
