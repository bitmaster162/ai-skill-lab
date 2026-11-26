"""R4: one-page daily status + budget summary on exact R3. Review only.
python build_summary.py --evidence-root <Phuket evidence> --repo <Git store> --output <new dir>
"""
import argparse,hashlib,json,os,subprocess,base64
from pathlib import Path
from html import escape
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R3="98e74e68e4a522df49037e755a80550ffcf3b1bfd14abb535b9067f36839bdd3"
R2="3dcc7d9c931f519f5c12fb12aa7a30bc7f529924688a76134b79ea012630f4dc"
PAYLOAD="749eb1782bd477e984a652cf7fb166db8b2f1c10a9173525a5b3798f0e49a186"
BUILDER="5fdc8272cbf1b38e937bb3fa70a5b72fb7ba2e5205287642d06bd8cffa998f04"
PATCHER="6e5a6e24f63bf5ae9012725254ea10ea5c1a177b9584891cd2708122e7a5902b"
CSS="phuket-daily-assets/budget.css"
JS="phuket-daily-assets/budget.js"
COPY={
 "ru":{"intro":"Отметьте состояние каждого дела прямо здесь. Отметки из другого планировщика автоматически не переносятся. Суммы остаются плановыми, даже если дело выполнено.","status":"Статус дела","states":["Не выбрано","Сегодня","Позже","Выполнено"],"title":"Личная сводка дня","help":"Выделите текст и скопируйте вручную, если хотите его сохранить. Сводка не отправляется и не сохраняется приложением.","unknown":"Неизвестно","invalid":"Некорректная сумма","reset":"Очистить суммы и отметки","noscript":"Без JavaScript можно указать суммы и статусы; автоматическая сводка недоступна."},
 "en":{"intro":"Mark each errand here. Choices from the separate planner are not transferred automatically. Amounts remain planned amounts even for completed errands.","status":"Errand status","states":["Not selected","Today","Later","Done"],"title":"Personal daily summary","help":"Select and copy the text manually if you want to keep it. The app does not send or store the summary.","unknown":"Unknown","invalid":"Invalid amount","reset":"Clear amounts and choices","noscript":"Without JavaScript, enter amounts and statuses manually; automatic summary is unavailable."}}
def need(v,m):
 if not v:raise ValueError(m)
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
 prior=root/"L12_DAILY_BUDGET_R3_20261126"/"candidate"
 m=json.loads(checked(prior/"BUDGET_DRAFT.json",R3))
 r2=json.loads(checked(root/"L12_DAILY_NEXT_R2_20261126"/"candidate"/"COMBINED_DRAFT.json",R2))
 need(m["base"]==r2["base"]==BASE and not m["release_approval"] and not r2["release_approval"],"draft scope")
 ns={"__name__":"pinned_builder"};exec(compile(checked(prior.parent/"build_budget.py",BUILDER),"budget.py","exec"),ns)
 static=ns["read"](prior/"static");nxt=ns["read"](prior/"next")
 need(len(static)==144 and ns["digest"](static)==PAYLOAD and len(nxt)==32,"exact R3")
 pins={**r2["patch_files"],**m["patch_files"]}
 need({n for n in pins if not n.startswith("deploy/live/")}==set(nxt),"Next inventory")
 for n,v in pins.items():
  b=static[n[12:]] if n.startswith("deploy/live/") else nxt[n]
  need(sha(b)==v["sha256"] and blob(b)==v["git_blob"],"R3 file "+n)
 css=static[CSS]+b"\n.field select,.summary textarea{width:100%;font:inherit;color:inherit;background:#152338;border:1px solid #8192aa;border-radius:8px;padding:10px}.field select{min-height:44px}.summary textarea{min-height:270px;resize:vertical}.summary{margin:24px 0}.field select:focus-visible,.summary textarea:focus-visible{outline:3px solid #b9ff3f;outline-offset:3px}\n"
 s=static[JS].decode()
 # Keep the original parser and arithmetic unchanged; render a summary using
 # only validated monetary values, never unvalidated strings.
 s=once(s,'const output=(id,value)=>','const states=[...document.querySelectorAll("[data-errand-state]")],summary=document.getElementById("summary-text"),meta=document.getElementById("summary");const output=(id,value)=>')
 summary='''const display=p=>p.kind==="valid"?money(p.value):p.kind==="unknown"?meta.dataset.unknown:meta.dataset.invalid;const label=e=>e.labels[0].textContent;const rows=items.map((p,i)=>label(fields[i+1])+": "+states[i].selectedOptions[0].textContent+" | "+display(p));summary.value=[meta.dataset.title,label(fields[0])+": "+display(parsed[0]),...rows,meta.dataset.known+": "+(valid.length?money(total):meta.dataset.unknown),meta.dataset.remaining+": "+(complete?money(rem):meta.dataset.unknown),status.textContent].join("\\n");'''
 # JSON/JS escape: the inserted source must contain a backslash-n, not an actual newline in the literal.
 summary=summary.replace('join("\n")','join("\\n")')
 s=once(s,'reset.disabled=fields.every(e=>e.value==="")}',summary+'reset.disabled=fields.every(e=>e.value==="")&&states.every(e=>e.value==="0")}')
 s=once(s,'reset.addEventListener("click",()=>{for(const e of fields)e.value="";update();','for(const e of states)e.addEventListener("change",update);reset.addEventListener("click",()=>{for(const e of fields)e.value="";for(const e of states)e.value="0";update();')
 js=s.encode()
 new=dict(static);nn=dict(nxt);new[CSS]=css;new[JS]=js;nn["public/"+CSS]=css;nn["public/"+JS]=js
 rows=[]
 for l in ("ru","en"):
  c=COPY[l];b=ns["COPY"][l];prefix=ns["prefix"](l)
  n=prefix[1:]+"/daily-budget.html";old=static[n].decode();html=old
  html=once(html,'<fieldset>','<p class="muted">'+escape(c["intro"])+'</p><fieldset>')
  for k,label in zip(ns["KEYS"][1:],b["labels"][1:]):
   marker=f'<input id="{k}" data-amount="" type="text" inputmode="decimal" autocomplete="off" maxlength="11" aria-describedby="units">'
   opts="".join(f'<option value="{i}">{escape(t)}</option>' for i,t in enumerate(c["states"]))
   extra=f'<label for="{k}-state">{escape(label)} — {escape(c["status"])}</label><select id="{k}-state" data-errand-state="">{opts}</select>'
   html=once(html,marker,marker+extra)
  attrs=" ".join(f'data-{k}="{escape(v,quote=True)}"' for k,v in {"title":c["title"],"unknown":c["unknown"],"invalid":c["invalid"],"known":b["known"],"remaining":b["remaining"]}.items())
  extra=f'<div id="summary" class="summary" {attrs}><h2 id="summary-title">{escape(c["title"])}</h2><p class="muted">{escape(c["help"])}</p><textarea id="summary-text" aria-labelledby="summary-title" readonly></textarea></div>'
  html=once(html,'<button id="reset" type="button">',extra+'<button id="reset" type="button">')
  html=once(html,'>'+escape(b["reset"])+'</button>','>'+escape(c["reset"])+'</button>')
  html=once(html,'<noscript><p>'+escape(b["noscript"])+'</p></noscript>','<noscript><p>'+escape(c["noscript"])+'</p></noscript>')
  # Script digest appears in both the SRI and CSP. Update both, not any parent policy.
  for oldasset,newasset,count in ((static[CSS],css,1),(static[JS],js,2)):
   oldhash=ns["sri"](oldasset);newhash=ns["sri"](newasset);need(html.count(oldhash)==count,"asset pin count");html=html.replace(oldhash,newhash)
  raw=html.encode();new[n]=raw
  h=next(x["handler"] for x in m["routes"] if x["html_path"]==n)
  source=nxt[h].decode();mark="return new Response(";i=source.index(mark)+len(mark);body,z=json.JSONDecoder().raw_decode(source[i:])
  need(body.encode()==static[n],"handler preimage")
  tail=once(source[i+z:],ns["sri"](static[JS]),ns["sri"](js))
  nn[h]=(source[:i]+ns["literal"](html)+tail).encode()
  rows.append({"html_path":n,"handler":h,"route":prefix+"/daily-budget","body_sha256":sha(raw)})
 sd={n for n in new if new[n]!=static[n]};nd={n for n in nn if nn[n]!=nxt[n]}
 need(len(sd)==len(nd)==4 and set(new)==set(static) and set(nn)==set(nxt),"eight replacements only")
 files={**{"deploy/live/"+n:new[n] for n in sd},**{n:nn[n] for n in nd}}
 old={**{"deploy/live/"+n:static[n] for n in sd},**{n:nxt[n] for n in nd}}
 patcher={"__name__":"pinned_patch"};exec(compile(checked(root/"L12_TOOLKIT_REVIEW_R22_20261126"/"build_review_patch.py",PATCHER),"patcher.py","exec"),patcher)
 patch=b"".join(patcher["patch_for"](n,old[n],b) for n,b in sorted(files.items()))
 out.mkdir(parents=True,exist_ok=False);write=patcher["write"]
 write(out/"static",new);write(out/"next",nn);write(out,{"daily-summary.patch":patch,"patch.b64":base64.encodebytes(patch)})
 work=out/"apply_check";work.mkdir();write(work,old)
 args=("apply","--whitespace=nowarn");git(*args,"--check",str(out/"daily-summary.patch"),cwd=work);git(*args,str(out/"daily-summary.patch"),cwd=work);need(patcher["read"](work)==files,"exact postimages");git(*args,"--reverse","--check",str(out/"daily-summary.patch"),cwd=work)
 report={"scope":"DAILY_SUMMARY_R4_REVIEW_ONLY","base":BASE,"r3_report_sha256":R3,"prior_payload":PAYLOAD,"static_payload":ns["digest"](new),"static_files":len(new),"next_files":len(nn),"routes":rows,"patch_sha256":sha(patch),"patch_git_blob":blob(patch),"patch_files":{n:{"sha256":sha(b),"bytes":len(b),"git_blob":blob(b)} for n,b in sorted(files.items())},"release_approval":False,"limitations":"Incremental R3 patch, not main. One-page manually entered status and planned budget, no cross-page data transfer. Actual Next build, full preflight, visual/accessibility and independent review, admission and owner merge open."}
 raw=(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n").encode();write(out,{"SUMMARY_DRAFT.json":raw})
 print("SUMMARY",len(files),"patch files",report["static_payload"],"report",sha(raw),"patch",sha(patch),"blob",blob(patch),"base64 lines",len(base64.encodebytes(patch).splitlines()),"base64 chars",len(base64.b64encode(patch)),flush=True)
if __name__=="__main__":main()
