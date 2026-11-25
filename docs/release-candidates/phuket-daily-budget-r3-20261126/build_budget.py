"""Daily budget R3: exact incremental product preview on the R2 review candidate.
Build: python build_budget.py --evidence-root <Phuket evidence> --repo <Git store> --output <new dir>
The patch targets the isolated R2 candidate, NOT main. No live changes.
"""
import argparse,base64,hashlib,json,os,subprocess
from pathlib import Path
from html import escape
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R2="3dcc7d9c931f519f5c12fb12aa7a30bc7f529924688a76134b79ea012630f4dc"
R2_PAYLOAD="0d4bb8cc44561d7344a5ad493d4136a8fd7b2b91b3550e5ad7f8554d8ed43f86"
PATCHER="6e5a6e24f63bf5ae9012725254ea10ea5c1a177b9584891cd2708122e7a5902b"
CSS_PATH="phuket-daily-assets/budget.css"
JS_PATH="phuket-daily-assets/budget.js"
KEYS=("budget","food","laundry","work","transport","services","leisure")
COPY={
 "ru":{"title":"Бюджет повседневных дел","intro":"Распределите свой лимит на день между шестью категориями. Это ваши плановые суммы, не цены на Пхукете.","units":"Все суммы в THB. Введите от 0 до 10 000 000 бат, до двух знаков после точки или запятой, без разделителей тысяч. Пустое поле — сумма неизвестна; 0 — расходов нет.","skip":"К основному содержимому","back":"К плану повседневных дел","switch":"English","fields":"План расходов","labels":["Лимит на день","Продукты и покупки","Стирка и бытовые дела","Работа и интернет","Транспорт","Местные услуги","Отдых и прогулка"],"known":"Известные расходы","unknown":"Категорий без суммы","invalid":"Некорректные поля","remaining":"Остаток лимита","incomplete":"Остаток не рассчитан: заполните лимит и все шесть категорий.","bad":"Исправьте некорректные суммы.","ok":"План укладывается в лимит.","over":"План превышает лимит.","reset":"Очистить суммы","results":"Расчёт","noscript":"Без JavaScript можно записать суммы; автоматический расчёт недоступен.","privacy":"Суммы не отправляются и не сохраняются приложением. Браузер может восстановить значения при возврате. Не вводите личные данные.","gateway":"Рассчитать бюджет на день"},
 "en":{"title":"Daily essentials budget","intro":"Allocate your own daily limit across six categories. These are your planned amounts, not Phuket market prices.","units":"All amounts in THB. Enter 0 to 10,000,000 baht with up to two decimal places using a dot or comma, without thousands separators. Blank means unknown; 0 means no expense.","skip":"Skip to main content","back":"Back to the daily planner","switch":"Русский","fields":"Expense plan","labels":["Daily limit","Groceries and shopping","Laundry and household errands","Work and internet","Transport","Local services","Leisure and a walk"],"known":"Known expenses","unknown":"Categories without amounts","invalid":"Invalid fields","remaining":"Remaining limit","incomplete":"Balance not calculated: fill the limit and all six categories.","bad":"Correct the invalid amounts.","ok":"The plan is within your limit.","over":"The plan exceeds your limit.","reset":"Clear amounts","results":"Calculation","noscript":"Without JavaScript, you can enter amounts; automatic calculation is unavailable.","privacy":"The app does not send or store amounts. Your browser may restore values when you return. Do not enter personal information.","gateway":"Calculate your daily budget"}}
CSS="""*{box-sizing:border-box;min-width:0}body{margin:0;background:#070a12;color:#eef2f6;font:1rem/1.55 system-ui,sans-serif}header,main{max-width:920px;margin:auto;padding:20px clamp(16px,4vw,32px)}header{display:flex;flex-wrap:wrap;gap:12px;justify-content:space-between}a{color:#8ef5df;text-decoration:underline;overflow-wrap:anywhere}h1,h2{line-height:1.2;overflow-wrap:anywhere}h1{font-size:clamp(1.8rem,5vw,3rem)}.muted{color:#b4bfce}.skip-link{position:fixed;left:-10000px;top:12px;z-index:1000;background:#b9ff3f;color:#070a12;padding:12px;max-width:calc(100% - 24px)}.skip-link:focus{left:12px}:is(a,input,button,main):focus-visible{outline:3px solid #b9ff3f;outline-offset:3px}fieldset{padding:16px;border:1px solid #61728a;border-radius:16px;margin:24px 0}legend{font-weight:700}.grid,.result{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:14px}.field{display:grid;gap:8px}.field:first-child{grid-column:1/-1}input{width:100%;font:inherit;color:inherit;background:#152338;border:1px solid #8192aa;border-radius:8px;min-height:44px;padding:10px}input[aria-invalid=true]{border:2px solid #f8aa96}output{display:block;font-size:1.4rem;font-weight:700;color:#8ef5df;overflow-wrap:anywhere}.result>div{padding:16px;border:1px solid #61728a;border-radius:12px;background:#0d1320}button{min-height:44px;padding:10px 16px;background:#18364a;color:inherit;border:1px solid #8192aa;border-radius:8px;font:inherit;cursor:pointer}button:disabled{opacity:.6}[hidden]{display:none!important}"""
# Integer satang, no floating-point arithmetic on monetary values.
JS="""(()=>{"use strict";const fields=[...document.querySelectorAll("[data-amount]")],box=document.getElementById("results"),reset=document.getElementById("reset"),status=document.getElementById("status"),fmt=new Intl.NumberFormat(document.documentElement.lang,{minimumFractionDigits:2,maximumFractionDigits:2});const output=(id,value)=>{document.getElementById(id).textContent=value};const money=n=>fmt.format(n/100)+" THB";function parse(e){const s=e.value.trim();if(s===""){e.removeAttribute("aria-invalid");return {kind:"unknown"}}if(!/^\\d{1,8}(?:[.,]\\d{1,2})?$/.test(s)){e.setAttribute("aria-invalid","true");return {kind:"invalid"}}const [a,b=""]=s.replace(",",".").split(".");const n=Number(a)*100+Number((b+"00").slice(0,2));if(!Number.isSafeInteger(n)||n>1000000000){e.setAttribute("aria-invalid","true");return {kind:"invalid"}}e.removeAttribute("aria-invalid");return {kind:"valid",value:n}}function update(){const parsed=fields.map(parse),items=parsed.slice(1),valid=items.filter(x=>x.kind==="valid"),missing=items.filter(x=>x.kind==="unknown").length,bad=parsed.filter(x=>x.kind==="invalid").length,total=valid.reduce((a,b)=>a+b.value,0);output("known",valid.length?money(total):"—");output("unknown",String(missing));output("invalid",String(bad));const complete=parsed.every(x=>x.kind==="valid");const rem=complete?parsed[0].value-total:null;output("remaining",complete?money(rem):"—");status.textContent=bad?box.dataset.bad:!complete?box.dataset.incomplete:rem<0?box.dataset.over:box.dataset.ok;reset.disabled=fields.every(e=>e.value==="")}for(const e of fields)e.addEventListener("input",update);reset.addEventListener("click",()=>{for(const e of fields)e.value="";update();fields[0].focus()});box.hidden=false;update()})();"""
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def sri(b):return "sha256-"+base64.b64encode(hashlib.sha256(b).digest()).decode()
def checked(p,pin):
 b=p.read_bytes();need(sha(b)==pin,"pin "+str(p));return b
def read(p):
 out={}
 for f in sorted(p.rglob("*")):
  need(not f.is_symlink(),"symlink")
  if f.is_file():out[f.relative_to(p).as_posix()]=f.read_bytes()
 return out
def digest(files):return sha("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode())
def literal(s):return json.dumps(s,ensure_ascii=False).replace("\u2028","\\u2028").replace("\u2029","\\u2029")
def once(s,a,b):
 need(s.count(a)==1,"unique edit "+a[:80]);return s.replace(a,b,1)
def prefix(l):return "/en/phuket-universe" if l=="en" else "/phuket-universe"
def page(l,css,js):
 c=COPY[l];other="en" if l=="ru" else "ru"
 fields="".join(f'<div class="field"><label for="{k}">{escape(t)}</label><input id="{k}" data-amount="" type="text" inputmode="decimal" autocomplete="off" maxlength="11" aria-describedby="units"></div>' for k,t in zip(KEYS,c["labels"]))
 policy="default-src 'none'; script-src '"+sri(js)+"'; style-src 'self'; font-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
 outputs="".join(f'<div><span>{escape(c[k])}</span><output id="{k}">—</output></div>' for k in ("known","unknown","invalid","remaining"))
 attrs=" ".join(f'data-{k}="{escape(c[k],quote=True)}"' for k in ("incomplete","bad","ok","over"))
 html=f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="{escape(policy,quote=True)}"><title>{escape(c["title"])} | Phuket Universe</title><link rel="stylesheet" href="/{CSS_PATH}" integrity="{sri(css)}"></head><body><a class="skip-link" href="#main">{escape(c["skip"])}</a><header><a href="{prefix(l)}/daily-essentials">{escape(c["back"])}</a><a lang="{other}" href="{prefix(other)}/daily-budget">{escape(c["switch"])}</a></header><main id="main" tabindex="-1"><h1>{escape(c["title"])}</h1><p>{escape(c["intro"])}</p><p id="units" class="muted">{escape(c["units"])}</p><fieldset><legend>{escape(c["fields"])}</legend><div class="grid">{fields}</div></fieldset><section id="results" hidden {attrs} aria-labelledby="results-title"><h2 id="results-title">{escape(c["results"])}</h2><div class="result" aria-live="polite">{outputs}</div><p id="status" role="status"></p><button id="reset" type="button">{escape(c["reset"])}</button></section><noscript><p>{escape(c["noscript"])}</p></noscript><p class="muted">{escape(c["privacy"])}</p></main><script src="/{JS_PATH}" integrity="{sri(js)}"></script></body></html>\n'
 return html.encode(),policy
def handler(raw,policy):
 headers={"Content-Type":"text/html; charset=utf-8","Content-Security-Policy":policy+"; frame-ancestors 'none'; worker-src 'none'","X-Robots-Tag":"noindex, nofollow","Cache-Control":"no-store","X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"no-referrer","Permissions-Policy":"camera=(), microphone=(), geolocation=()"}
 return ("export const dynamic = \"force-static\";\nexport function GET(): Response {\n  return new Response("+literal(raw.decode())+", { status: 200, headers: "+literal(headers)+" });\n}\n").encode()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("evidence-root","repo","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();root=a.evidence_root.resolve();repo=a.repo.resolve();out=a.output.resolve()
 need(not out.exists() and out!=root and out!=repo and repo not in out.parents,"new output")
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*v,cwd=None):return subprocess.check_output(["git","--no-optional-locks",*v],cwd=cwd,env=env,timeout=30,stderr=subprocess.STDOUT)
 need(git("-C",str(repo),"rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 prior=root/"L12_DAILY_NEXT_R2_20261126"/"candidate";m=json.loads(checked(prior/"COMBINED_DRAFT.json",R2))
 need(m["base"]==BASE and m["scope"]=="DAILY_R2_COMBINED_REVIEW_ONLY" and not m["release_approval"],"R2 scope")
 static=read(prior/"static");nxt=read(prior/"next")
 need(len(static)==140 and digest(static)==R2_PAYLOAD and len(nxt)==28,"R2 inventory")
 for n,v in m["patch_files"].items():
  b=static[n[len("deploy/live/"):]] if n.startswith("deploy/live/") else nxt[n]
  need(sha(b)==v["sha256"] and blob(b)==v["git_blob"],"R2 source pin "+n)
 new=dict(static);new_next=dict(nxt);css=(CSS+"\n").encode();js=(JS+"\n").encode()
 for n,b in ((CSS_PATH,css),(JS_PATH,js)):
  need(n not in new and "public/"+n not in new_next,"new asset")
  new[n]=b;new_next["public/"+n]=b
 rows=[]
 for l in ("ru","en"):
  c=COPY[l];pfx=prefix(l);daily=pfx[1:]+"/daily-essentials.html";budget=pfx[1:]+"/daily-budget.html"
  group=("app/(en)/en/" if l=="en" else "app/(ru)/")+"phuket-universe/"
  daily_handler=group+"daily-essentials/route.ts";budget_handler=group+"daily-budget/route.ts"
  link=f'<p><a href="{pfx}/daily-budget">{escape(c["gateway"])}</a></p>'
  old=static[daily].decode();changed=once(old,"<fieldset>",link+"<fieldset>")
  need(once(changed,link,"")==old,"preserve Daily content")
  new[daily]=changed.encode()
  s=nxt[daily_handler].decode();mark="return new Response(";i=s.index(mark)+len(mark);body,z=json.JSONDecoder().raw_decode(s[i:])
  need(body.encode()==static[daily],"Daily handler preimage")
  new_next[daily_handler]=(s[:i]+literal(changed)+s[i+z:]).encode()
  need(budget not in new and budget_handler not in new_next,"new route")
  raw,policy=page(l,css,js);new[budget]=raw;new_next[budget_handler]=handler(raw,policy)
  rows.extend([{"route":pfx+"/daily-essentials","html_path":daily,"handler":daily_handler,"body_sha256":sha(new[daily])},{"route":pfx+"/daily-budget","html_path":budget,"handler":budget_handler,"body_sha256":sha(raw)}])
 sd={n for n,b in new.items() if static.get(n)!=b};nd={n for n,b in new_next.items() if nxt.get(n)!=b}
 need(len(sd)==len(nd)==6 and len(new)==144 and len(new_next)==32,"exact incremental inventory")
 need(all(new[n]==b for n,b in static.items() if n not in sd),"prior static unchanged")
 need(all(new_next[n]==b for n,b in nxt.items() if n not in nd),"prior Next unchanged")
 files={**{"deploy/live/"+n:new[n] for n in sd},**{n:new_next[n] for n in nd}}
 old={**{"deploy/live/"+n:static[n] for n in sd if n in static},**{n:nxt[n] for n in nd if n in nxt}}
 need(len(files)==12 and len(old)==4,"incremental patch scope")
 patchsrc=checked(root/"L12_TOOLKIT_REVIEW_R22_20261126"/"build_review_patch.py",PATCHER);ns={"__name__":"pinned_patch"};exec(compile(patchsrc,"patcher.py","exec"),ns)
 patch=b"".join(ns["patch_for"](n,old.get(n),b) for n,b in sorted(files.items()))
 out.mkdir(parents=True,exist_ok=False)
 ns["write"](out/"static",new);ns["write"](out/"next",new_next)
 ns["write"](out,{"daily-budget.patch":patch,"patch.b64":base64.encodebytes(patch)})
 work=out/"apply_check";work.mkdir();ns["write"](work,old)
 args=("apply","--whitespace=nowarn");git(*args,"--check",str(out/"daily-budget.patch"),cwd=work);git(*args,str(out/"daily-budget.patch"),cwd=work)
 need(read(work)==files,"exact postimages");git(*args,"--reverse","--check",str(out/"daily-budget.patch"),cwd=work)
 report={"scope":"DAILY_BUDGET_R3_REVIEW_ONLY","base":BASE,"r2_report_sha256":R2,"prior_payload":R2_PAYLOAD,"static_payload":digest(new),"static_files":len(new),"next_files":len(new_next),"routes":rows,"patch_sha256":sha(patch),"patch_git_blob":blob(patch),"patch_bytes":len(patch),"patch_files":{n:{"sha256":sha(b),"bytes":len(b),"git_blob":blob(b)} for n,b in sorted(files.items())},"release_approval":False,"limitations":"Incremental patch against exact R2 review candidate, not main. User-entered planned amounts only, no market-price claims. No app storage or network. Actual Next build, full preflight, independent review, successor admission and deployment remain open."}
 raw=(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode();ns["write"](out,{"BUDGET_DRAFT.json":raw})
 print("BUDGET",len(new),"static",len(new_next),"Next",len(files),"patch files","payload",report["static_payload"],"report",sha(raw),"patch",sha(patch),"blob",blob(patch),"base64 lines",len(base64.encodebytes(patch).splitlines()),"base64 chars",len(base64.b64encode(patch)),flush=True)
if __name__=="__main__":main()
