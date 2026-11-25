"""R8 rental move-out and deposit reconciliation, RU/EN draft preview.
Run: python build_move_out.py --repo <checkout> --r7 <preview dir> --output <new external dir>
Only personal arithmetic, no legal determination, submissions, storage or release.
"""
import argparse,base64,hashlib,html,json,subprocess
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
R7="a3ccda9cb448ba2756cb46d16c812c4e8c22cf80"
PINS={
"phuket-universe.html":"a231e27e1687ad4229b2ebf863d6b00a50cfa0e17f7b7e8b7f9657e16798c325",
"en/phuket-universe.html":"abbea4cc42de6bf639a4e1bed51556aee4428a5538f8d7f8f3199a5280ec7b9b",
"preview-tools/ru/rental-journey.html":"a72bd1420ebce4497d439196826e2936161bb1b8623cc4978c813db0458d9232",
"preview-tools/en/rental-journey.html":"c3e7d9576fd4ce921a624dd605d9f97d4f0c24ae3a462ae547148b80ddd95e85",
"preview-tools/ru/rental-budget-calculator.html":"0b3c1d338e221fe774903ec5f2ba54d208df23bad19fd3f368b2b7a8a64d8be7",
"preview-tools/en/rental-budget-calculator.html":"73642f56ec0c7c24f99a1a3999a8f15b466c8fea5291fab36931b2c485efe304",
"preview-tools/ru/rental-shortlist.html":"014841064db6f010780fce536221704700c40c62d049abe8659a05cde0c2418d",
"preview-tools/en/rental-shortlist.html":"91ac7f29e59ecd43a9defc8515dfb3ad07ad8bbd5df90cd79544181bee6b4834",
"preview-tools/ru/rental-move-in.html":"ddee53772565a7fce82b098eaadd309338ec22dc2c39d94a4a1c38c3f8f74ac7",
"preview-tools/en/rental-move-in.html":"f00b8f807bd1cfbe0bb823f09e29cb447b2810def906083a8c8480b07da553f8"}
COPY={
"ru":{"title":"Выезд и сверка депозита","intro":"Сравните введённый вами расчёт возврата с фактически полученной суммой. Это арифметика, а не определение законного долга. Указанные удержания не считаются согласованными или законными.",
"fields":["Внесённый депозит","Удержания по имеющемуся расчёту","Фактически полученный возврат"],"expected":"Расчётный возврат","delta":"Расчётный возврат минус полученный",
"unknown":"Введите все три суммы. Пустое поле — неизвестно, а не ноль.","invalid":"Нужны целые суммы от 0 до 1 000 000 000 THB.","excess":"Удержания больше депозита. Сверьте суммы отдельно; результат не рассчитан.","less":"Получено меньше расчётной суммы. Уточните расхождение по документам.","more":"Получено больше расчётной суммы. Уточните состав платежей.","equal":"Введённые суммы совпадают с расчётом. Это не подтверждение окончательного расчёта.","example":"Вымышленный пример","reset":"Очистить","checkTitle":"Перед возвратом жилья","checks":[["Срок и порядок выезда","Сверьте даты и порядок уведомления в вашем договоре; не полагайтесь на универсальный срок."],["Состояние и опись","Сравните состояние жилья с записями при заселении; зафиксируйте расхождения."],["Счётчики и платежи","Сверьте показания, выставленные счета и уже оплаченные суммы."],["Осмотр и ключи","Уточните порядок осмотра, возврата ключей и подтверждения передачи."],["Возврат депозита","Запросите понятную разбивку удержаний и сверяйте фактические поступления с документами."]],"guide":"К маршруту арендатора","movein":"К списку заселения","other":"English","privacy":"Локальный черновик. Не вводите адреса, имена, контакты или реквизиты. Инструмент не отправляет и не сохраняет значения. Браузер может восстановить поля. Это не юридическая консультация, требование оплаты или подтверждение возврата."},
"en":{"title":"Move-out and deposit reconciliation","intro":"Compare your entered refund calculation with the amount actually received. This is arithmetic, not a legal determination of debt. Entered deductions are not deemed agreed or lawful.",
"fields":["Deposit paid","Deductions in the available calculation","Refund actually received"],"expected":"Calculated refund","delta":"Calculated refund minus amount received",
"unknown":"Enter all three amounts. A blank is unknown, not zero.","invalid":"Enter whole amounts from 0 to 1,000,000,000 THB.","excess":"Deductions exceed the deposit. Reconcile the amounts separately; no result calculated.","less":"Less was received than the calculated amount. Check the difference against the records.","more":"More was received than the calculated amount. Check what the payments include.","equal":"The entered amounts reconcile. This does not confirm final settlement.","example":"Fictional example","reset":"Clear","checkTitle":"Before returning the property","checks":[["Move-out dates and procedure","Check notice dates and procedure in your own agreement; do not rely on a universal notice period."],["Condition and inventory","Compare the property with your move-in notes and record discrepancies."],["Meters and payments","Compare meter readings, bills and amounts already paid."],["Inspection and keys","Clarify inspection, key return and evidence of handover."],["Deposit refund","Ask for an understandable breakdown of deductions and compare actual receipts with the records."]],"guide":"Back to rental journey","movein":"Move-in checklist","other":"Русский","privacy":"Local draft. Do not enter addresses, names, contacts or payment details. The tool does not send or store values. Your browser may restore fields. Not legal advice, a payment demand or refund confirmation."}}
CSS="""*{box-sizing:border-box}body{margin:0;background:#0d1320;color:#eef4fc;font:1rem/1.6 system-ui,sans-serif}main{max-width:860px;margin:auto;padding:24px}h1,h2,h3{line-height:1.25;overflow-wrap:anywhere}a{color:#8ef5df;text-decoration:underline}nav{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:24px}.fields,.results{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px}.field{display:grid;gap:6px;min-width:0}input{width:100%;padding:10px;background:#152338;color:inherit;border:1px solid #8192aa;border-radius:8px;font:inherit}input[aria-invalid=true]{border:2px solid #f8aa96}fieldset{margin:18px 0;border:1px solid #61728a;border-radius:14px;padding:16px;min-width:0}button{padding:10px 14px;margin:12px 8px 0 0;background:#18364a;color:inherit;border:1px solid #8192aa;border-radius:8px;font:inherit;cursor:pointer}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #39e1c6;outline-offset:3px}.results>div{padding:16px;border:1px solid #61728a;border-radius:12px;min-width:0}output{display:block;color:#8ef5df;font-weight:700;font-size:1.4rem;overflow-wrap:anywhere}details{padding:12px;border:1px solid #61728a;border-radius:10px;margin:10px 0}summary{cursor:pointer;font-weight:600}summary:focus-visible{outline:3px solid #39e1c6}small{display:block;color:#b8c8da;margin-top:20px}"""
JS="""(()=>{"use strict";const g=id=>document.getElementById(id),t=JSON.parse(g('copy').textContent),fields=['deposit','deductions','received'].map(g),out=g('expected'),delta=g('delta'),status=g('status'),nf=new Intl.NumberFormat(document.documentElement.lang==='ru'?'ru-RU':'en-US');function amount(el){const s=el.value,n=Number(s),blank=s===''&&!el.validity.badInput,ok=/^[0-9]+$/.test(s)&&Number.isSafeInteger(n)&&n>=0&&n<=1000000000;el.setAttribute('aria-invalid',String(!blank&&!ok));return blank?{kind:'unknown'}:ok?{kind:'known',n}:{kind:'invalid'};}function clear(msg){out.textContent='—';delta.textContent='—';status.textContent=msg;}function render(){const values=fields.map(amount);if(values.some(v=>v.kind==='invalid')){clear(t.invalid);return;}if(values.some(v=>v.kind==='unknown')){clear(t.unknown);return;}const [d,c,r]=values.map(v=>v.n);if(c>d){clear(t.excess);return;}const expected=d-c,diff=expected-r;out.textContent=nf.format(expected)+' THB';delta.textContent=nf.format(diff)+' THB';status.textContent=diff>0?t.less:diff<0?t.more:t.equal;}fields.forEach(x=>x.addEventListener('input',render));g('example').addEventListener('click',()=>{[40000,5000,30000].forEach((n,i)=>{fields[i].value=String(n);});render();});g('reset').addEventListener('click',()=>{fields.forEach(x=>{x.value='';});render();fields[0].focus();});render();})();"""
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(s):return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def route(l,kind):return "/preview-tools/"+l+"/rental-"+kind+".html"
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def render(l):
 c=COPY[l];e=lambda v:html.escape(v,quote=True);other="en" if l=="ru" else "ru"
 fields="".join(f'<label class="field" for="{id}"><span>{e(label)} (THB)</span><input id="{id}" type="number" min="0" max="1000000000" step="1" inputmode="numeric" autocomplete="off"></label>' for id,label in zip(("deposit","deductions","received"),c["fields"]))
 checks="".join(f'<details><summary>{e(a)}</summary><p>{e(b)}</p></details>' for a,b in c["checks"])
 data=json.dumps(c,ensure_ascii=False).replace("<","\\u003c")
 policy=f"default-src 'none'; script-src 'sha256-{pin(JS)}'; style-src 'sha256-{pin(CSS)}'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
 return (f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="{e(policy)}"><title>{e(c["title"])}</title><style>{CSS}</style></head><body><main><nav><a href="{route(l,"journey")}">{e(c["guide"])}</a><a href="{route(l,"move-in")}">{e(c["movein"])}</a><a href="{route(other,"move-out")}" lang="{other}">{e(c["other"])}</a></nav><h1>{e(c["title"])}</h1><p>{e(c["intro"])}</p><fieldset><legend>THB</legend><div class="fields">{fields}</div><button id="example" type="button">{e(c["example"])}</button><button id="reset" type="button">{e(c["reset"])}</button></fieldset><div class="results" aria-live="polite"><div><strong>{e(c["expected"])}</strong><output id="expected">—</output></div><div><strong>{e(c["delta"])}</strong><output id="delta">—</output></div></div><p id="status" role="status">{e(c["unknown"])}</p><h2>{e(c["checkTitle"])}</h2>{checks}<small>{e(c["privacy"])}</small></main><script id="copy" type="application/json">{data}</script><script>{JS}</script></body></html>\n').encode()
def build(manifest,r7):
 need(sha(manifest)==MANIFEST,"parent manifest")
 out={}
 for path,p in PINS.items():
  b=(r7/path).read_bytes();need(sha(b)==p,"R7 pin "+path)
  if path.endswith("/rental-journey.html"):
   l=path.split("/")[1];s=b.decode();anchor="</ul></nav>"
   need(s.count(anchor)==1 and route(l,"move-out") not in s,"guide insertion")
   a=f'<li><a class="pu-s082" href="{route(l,"move-out")}">{html.escape(COPY[l]["title"])}</a></li>'
   new=s.replace(anchor,a+anchor,1);need(new.replace(a,"",1)==s,"guide preservation");out[path]=new.encode()
  else:out[path]=b
 for l in COPY:
  path=route(l,"move-out").lstrip("/");out[path]=render(l);tags=Tags(out[path].decode()).tags
  ids=[a["id"] for t,a in tags if "id" in a]
  need(len(ids)==len(set(ids)),"unique ids")
  need(sum(t=="input" and a.get("type")=="number" for t,a in tags)==3,"three amounts")
  need(sum(t=="details" for t,a in tags)==5,"five prompts")
  need(not any(t in {"form","iframe","textarea"} for t,a in tags),"no submission")
  need([(t,a["href"]) for t,a in tags if "href" in a]==[("a",route(l,"journey")),("a",route(l,"move-in")),("a",route("en" if l=="ru" else "ru","move-out"))],"local links")
  need(any(a.get("name")=="robots" and "noindex" in a.get("content","") for t,a in tags),"noindex")
 need(len(out)==12 and all(len(b)<=38912 for b in out.values()),"historical per-file cap")
 report={n:{"sha256":sha(b),"bytes":len(b),"old_sha256":PINS.get(n),"changed":PINS.get(n)!=sha(b)} for n,b in out.items()}
 need(sum(v["changed"] for v in report.values())==4,"two guides and two new pages")
 return out,{"base":BASE,"r7":R7,"scope":"MOVE_OUT_DRAFT_ONLY","files":report,"release_approval":False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--r7",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 need(out!=repo and repo not in out.parents and not out.exists(),"new external directory")
 files,report=build(git("show",BASE+":deploy/live/_release.json"),a.r7)
 out.mkdir(parents=True,exist_ok=False)
 for n,b in files.items():
  f=out/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
