"""Daily essentials R1: independent bilingual product preview on exact parent.
Build only outside the checkout; no deployment or admission.
python build_daily.py --repo <pinned Git store> --parent <R16 parent> --output <new directory>
"""
import argparse,base64,hashlib,json,os,re,subprocess
from pathlib import Path
from html import escape
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
PARENT="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
CSS_PATH="phuket-daily-assets/essentials.css"
JS_PATH="phuket-daily-assets/essentials.js"
KINDS=("food","laundry","work","transport","services","leisure")
COPY={
 "ru":{"title":"Повседневные дела на Пхукете","intro":"Соберите свой план на день: выберите, что нужно сегодня, что можно отложить и что уже выполнено.","scope":"Личный список, не каталог заведений и не расчёт маршрута. Перед выходом проверьте адрес, часы работы, доступность и стоимость у выбранного места.","back":"К Phuket Universe","switch":"English","skip":"К основному содержимому","legend":"Ваши дела","states":["Не выбрано","Сегодня","Позже","Выполнено"],"labels":["Сегодня","Позже","Выполнено"],"plan":"Ваш план","empty":"Пока ничего не выбрано.","reset":"Сбросить отметки","note":"Можно выделить и скопировать текст плана вручную. Приложение не сохраняет и не отправляет отметки. Браузер может восстановить их при возврате. Не вводите личные данные.","nojs":"Без JavaScript можно отметить дела вручную; счётчики и текст плана недоступны.","gateway":"План повседневных дел","gateway_body":"Продукты, бытовые услуги, рабочее место, транспорт и отдых — соберите собственный список перед выходом.","items":[
 ["Продукты и покупки","Составьте список необходимых покупок. Проверьте часы работы и способы оплаты."],
 ["Стирка и бытовые дела","Уточните срок готовности, стоимость и условия услуги."],
 ["Работа и интернет","Проверьте время доступа, связь, розетки и возможность спокойно работать."],
 ["Транспорт","Сравните варианты поездки и возвращения; заранее проверьте доступность и стоимость."],
 ["Местные услуги","Уточните, нужна ли запись, какие документы или вещи потребуется взять и какова полная цена."],
 ["Отдых и прогулка","Выберите место и время, проверьте актуальные условия доступа и погоду."]]},
 "en":{"title":"Daily essentials in Phuket","intro":"Build your own plan for the day: choose what to do today, what can wait, and what is already done.","scope":"A personal checklist, not a business directory or route calculation. Check the address, opening hours, availability and cost with your chosen place before leaving.","back":"Back to Phuket Universe","switch":"Русский","skip":"Skip to main content","legend":"Your errands","states":["Not selected","Today","Later","Done"],"labels":["Today","Later","Done"],"plan":"Your plan","empty":"Nothing selected yet.","reset":"Reset choices","note":"Select and copy the plan manually if useful. The app does not store or send your choices. Your browser may restore them when you return. Do not enter personal information.","nojs":"Without JavaScript, mark errands manually; counters and the text plan are unavailable.","gateway":"Daily essentials planner","gateway_body":"Groceries, household services, work, transport and leisure: make your own list before heading out.","items":[
 ["Groceries and shopping","Make a shopping list. Check opening hours and payment options."],
 ["Laundry and household errands","Confirm turnaround time, cost and service conditions."],
 ["Work and internet","Check access hours, connectivity, power outlets and whether the space suits your work."],
 ["Transport","Compare ways to get there and back; confirm availability and cost before leaving."],
 ["Local services","Check whether an appointment is needed, what to bring and the total price."],
 ["Leisure and a walk","Choose a place and time; check current access conditions and weather."]]}}
CSS="""*{box-sizing:border-box;min-width:0}body{margin:0;background:#070a12;color:#eef2f6;font:1rem/1.55 system-ui,sans-serif}header,main{max-width:1000px;margin:auto;padding:20px clamp(16px,4vw,32px)}header{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between}a{color:#8ef5df;text-decoration:underline;overflow-wrap:anywhere}h1,h2,h3{line-height:1.2;overflow-wrap:anywhere}h1{font-size:clamp(1.85rem,5vw,3rem)}p{overflow-wrap:anywhere}.muted{color:#b4bfce}.skip-link{position:fixed;left:-10000px;top:12px;background:#b9ff3f;color:#070a12;padding:12px;z-index:1000;max-width:calc(100% - 24px)}.skip-link:focus{left:12px}:is(a,select,button,textarea,main):focus-visible{outline:3px solid #b9ff3f;outline-offset:3px}fieldset{border:0;padding:0;margin:24px 0;min-width:0}legend{font-size:1.5rem;font-weight:700;margin-bottom:12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px}.item,.plan{padding:18px;border:1px solid #526079;background:#0d1320;border-radius:16px}.item{display:flex;flex-direction:column;gap:10px}.item h3,.item p{margin:0}.item select{margin-top:auto;width:100%;font:inherit;padding:10px;border-radius:8px;border:1px solid #8192aa;background:#152338;color:#eef2f6;min-height:44px}.counts{display:flex;gap:8px;flex-wrap:wrap;list-style:none;padding:0}.counts li{border:1px solid #526079;padding:8px;border-radius:10px}.plan textarea{width:100%;min-height:180px;resize:vertical;background:#152338;border:1px solid #8192aa;border-radius:8px;color:inherit;padding:12px;font:inherit}button{min-height:44px;padding:10px 16px;margin-top:12px;background:#18364a;color:inherit;border:1px solid #8192aa;border-radius:8px;font:inherit;cursor:pointer}button:disabled{opacity:.6}[hidden]{display:none!important}"""
JS="""(()=>{"use strict";const controls=Array.from(document.querySelectorAll("[data-errand]"));const panel=document.getElementById("plan");const note=document.getElementById("plan-text");const reset=document.getElementById("reset");const empty=panel.dataset.empty;const labels=[...panel.querySelectorAll("[data-count-label]")].map(e=>e.textContent);function update(){const groups=[[],[],[],[]];for(const e of controls){const i=Number(e.value);if(Number.isInteger(i)&&i>=0&&i<=3)groups[i].push(document.getElementById(e.getAttribute("aria-labelledby")).textContent)}const chunks=[];for(let i=1;i<=3;i++){panel.querySelector("[data-count='"+i+"']").textContent=String(groups[i].length);if(groups[i].length)chunks.push(labels[i-1]+":\\n"+groups[i].map(s=>"• "+s).join("\\n"))}note.value=chunks.join("\\n\\n")||empty;reset.disabled=groups[0].length===controls.length}for(const e of controls)e.addEventListener("change",update);reset.addEventListener("click",()=>{for(const e of controls)e.value="0";update()});panel.hidden=false;update()})();"""
def need(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def sri(b):return "sha256-"+base64.b64encode(hashlib.sha256(b).digest()).decode()
def prefix(l):return "/en/phuket-universe" if l=="en" else "/phuket-universe"
def page(l,css,js):
 c=COPY[l];other="en" if l=="ru" else "ru"
 policy="default-src 'none'; script-src '"+sri(js)+"'; style-src 'self'; font-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
 items=[]
 for k,(name,desc) in zip(KINDS,c["items"]):
  opts="".join(f'<option value="{i}">{escape(t)}</option>' for i,t in enumerate(c["states"]))
  items.append(f'<div class="item"><h3 id="{k}-title">{escape(name)}</h3><p id="{k}-help" class="muted">{escape(desc)}</p><select id="{k}" data-errand="" aria-labelledby="{k}-title" aria-describedby="{k}-help">{opts}</select></div>')
 counts="".join(f'<li><span data-count-label="">{escape(t)}</span>: <output data-count="{i}">0</output></li>' for i,t in enumerate(c["labels"],1))
 return (f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="{escape(policy,quote=True)}"><title>{escape(c["title"])} | Phuket Universe</title><link rel="stylesheet" href="/{CSS_PATH}" integrity="{sri(css)}"></head><body><a class="skip-link" href="#main">{escape(c["skip"])}</a><header><a href="{prefix(l)}#daily-essentials">{escape(c["back"])}</a><a lang="{other}" href="{prefix(other)}/daily-essentials">{escape(c["switch"])}</a></header><main id="main" tabindex="-1"><h1>{escape(c["title"])}</h1><p>{escape(c["intro"])}</p><p class="muted">{escape(c["scope"])}</p><fieldset><legend>{escape(c["legend"])}</legend><div class="grid">{"".join(items)}</div></fieldset><section class="plan" id="plan" hidden data-empty="{escape(c["empty"],quote=True)}"><h2 id="plan-title">{escape(c["plan"])}</h2><ul class="counts" aria-live="polite">{counts}</ul><textarea id="plan-text" readonly aria-labelledby="plan-title"></textarea><button id="reset" type="button">{escape(c["reset"])}</button></section><noscript><p>{escape(c["nojs"])}</p></noscript><p class="muted">{escape(c["note"])}</p></main><script src="/{JS_PATH}" integrity="{sri(js)}"></script></body></html>\n').encode()
def gateway(b,l):
 c=COPY[l];s=b.decode()
 anchor='<section class="pu-s039" id="agencies">'
 need(s.count(anchor)==1 and 'id="daily-essentials"' not in s,"unique gateway boundary")
 section=f'<section class="pu-s039" id="daily-essentials" aria-labelledby="daily-title"><div class="pu-s096 pu-pad"><div class="pu-s098"><h2 id="daily-title" class="pu-s099">{escape(c["gateway"])}</h2><p class="pu-s044">{escape(c["gateway_body"])}</p><a class="pu-s082" href="{prefix(l)}/daily-essentials">{escape(c["gateway"])}</a></div></div></section>\n\n'
 return s.replace(anchor,section+anchor,1).encode()
def measure(files):return hashlib.sha256("".join(f"{n}\t{len(b)}\t{sha(b)}\n" for n,b in sorted(files.items())).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ("repo","parent","output"):p.add_argument("--"+n,type=Path,required=True)
 a=p.parse_args();repo=a.repo.resolve();parent=a.parent.resolve();out=a.output.resolve()
 need(not out.exists() and all(out!=x and x not in out.parents for x in (repo,parent)),"new external output")
 env={**os.environ,"GIT_NO_LAZY_FETCH":"1","GIT_ALLOW_PROTOCOL":"","GIT_TERMINAL_PROMPT":"0","GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_GLOBAL":os.devnull}
 def git(*v):return subprocess.check_output(["git","--no-optional-locks","-C",str(repo),*v],env=env,timeout=20)
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"verified Git baseline")
 before={f.relative_to(parent).as_posix():f.read_bytes() for f in parent.rglob("*") if f.is_file() and not f.is_symlink()}
 need(len(before)==116 and measure(before)==PARENT,"exact parent payload")
 css=(CSS+"\n").encode();js=(JS+"\n").encode()
 delta={CSS_PATH:css,JS_PATH:js}
 for l in ("ru","en"):
  n=prefix(l)[1:]+".html"
  pre=git("ls-tree",BASE,"deploy/live/"+n).decode().split()
  need(len(pre)>=3 and pre[2]==blob(before[n]),"parent page Git preimage")
  delta[n]=gateway(before[n],l)
  delta[prefix(l)[1:]+"/daily-essentials.html"]=page(l,css,js)
 need(len(delta)==6 and len(set(delta)&set(before))==2,"exact delta")
 candidate={**before,**delta}
 out.mkdir(exist_ok=False,parents=True)
 for n,b in candidate.items():
  f=out/"static"/n;f.parent.mkdir(exist_ok=True,parents=True);f.write_bytes(b)
 for n,b in delta.items():
  f=out/"overlay"/n;f.parent.mkdir(exist_ok=True,parents=True);f.write_bytes(b)
 m={"scope":"DAILY_ESSENTIALS_R1_DRAFT_ONLY","base":BASE,"parent_payload_sha256":PARENT,"candidate_payload_sha256":measure(candidate),"candidate_files":len(candidate),"delta":{n:{"sha256":sha(b),"git_blob":blob(b),"bytes":len(b)} for n,b in sorted(delta.items())},"release_approval":False,"limitations":"Independent of R22 rental candidate; no actual listings, opening-hours claims, service recommendations or routing. Browser-local native controls and generated manual-copy plan; no server, storage or clipboard writes. No Next equivalent, combined rental integration, release admission or live publication."}
 raw=(json.dumps(m,indent=2,sort_keys=True)+"\n").encode();(out/"DAILY_DRAFT.json").write_bytes(raw)
 print("DAILY",len(delta),"files",len(candidate),"payload",m["candidate_payload_sha256"],"REPORT",sha(raw),flush=True)
if __name__=="__main__":main()
