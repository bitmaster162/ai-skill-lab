"""R7 move-in checklist integrated with the exact R6 rental toolkit.
Draft only. No submissions, server storage, inventory, or deploy/live writes.
Run: python build_move_in.py --repo <checkout> --r6 <preview dir> --output <new external directory>
"""
import argparse,base64,hashlib,html,json,subprocess
from html.parser import HTMLParser
from pathlib import Path

BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
R6="149c0f175a944acf2504fbb03d1b7a3a482a823c"
PINS={
"phuket-universe.html":"a231e27e1687ad4229b2ebf863d6b00a50cfa0e17f7b7e8b7f9657e16798c325",
"en/phuket-universe.html":"abbea4cc42de6bf639a4e1bed51556aee4428a5538f8d7f8f3199a5280ec7b9b",
"preview-tools/ru/rental-journey.html":"0d18e96bd3ea52d5bf71097c84c27d13f3b18c31ccc292ce9f52443aea73fea7",
"preview-tools/en/rental-journey.html":"0912f4886e2abca74ec467fb4f1d224af891506725ade1c53a1abd67cccb1c60",
"preview-tools/ru/rental-budget-calculator.html":"0b3c1d338e221fe774903ec5f2ba54d208df23bad19fd3f368b2b7a8a64d8be7",
"preview-tools/en/rental-budget-calculator.html":"73642f56ec0c7c24f99a1a3999a8f15b466c8fea5291fab36931b2c485efe304",
"preview-tools/ru/rental-shortlist.html":"014841064db6f010780fce536221704700c40c62d049abe8659a05cde0c2418d",
"preview-tools/en/rental-shortlist.html":"91ac7f29e59ecd43a9defc8515dfb3ad07ad8bbd5df90cd79544181bee6b4834"}
COPY={
"ru":{
"title":"Чек-лист заселения","intro":"Отмечайте состояние каждого пункта при передаче жилья. «Зафиксировано» означает только, что вы записали результат проверки, а не что всё исправно или согласовано.",
"labels":["Не проверено","Зафиксировано","Нужно уточнить","Не применимо"],
"items":[
["Ключи и доступ","Сверьте количество переданных ключей, карт доступа и пультов. Проверьте обычный вход и выход без вмешательства в замки."],
["Состояние помещений","Запишите уже существующие повреждения, пятна и следы протечек. При необходимости отдельно сделайте разрешённые фотографии."],
["Опись имущества","Сверьте переданные предметы и их состояние с согласованным списком."],
["Счётчики и услуги","Запишите доступные показания воды и электричества, дату и порядок оплаты. Не вскрывайте оборудование и электрощит."],
["Связь и бытовые приборы","Уточните подключение интернета и обычную работу доступных приборов. Не выполняйте опасных проверок."],
["Переданные документы","Сверьте экземпляры согласованных документов и подтверждения уже совершённых платежей. Не отмечайте неполученное как полученное."],
["Порядок сообщения о дефектах","Уточните, кому и каким способом сообщать о неисправностях, и как фиксировать ответ."],
["Условия возврата жилья","Запишите согласованный порядок возврата ключей, осмотра и расчётов при выезде. Не подменяйте договор этим списком."]],
"summary":"Состояния пунктов","reset":"Сбросить все отметки","nav":"К маршруту арендатора","other":"English",
"warning":"Личные отметки не являются актом приёма-передачи, подтверждением безопасности или юридическим заключением. Не вводите здесь адреса, имена, контакты или данные документов.",
"privacy":"Черновик для локального просмотра: инструмент не сохраняет и не отправляет отметки. Браузер может восстановить значения. Перед уходом запишите важные результаты отдельно."},
"en":{
"title":"Move-in checklist","intro":"Record each item's status at handover. “Recorded” means you noted the outcome, not that the item is safe, satisfactory or agreed.",
"labels":["Not checked","Recorded","Needs clarification","Not applicable"],
"items":[
["Keys and access","Check the number of keys, access cards and remotes handed over. Check normal entry and exit without tampering with locks."],
["Property condition","Note existing damage, stains and signs of leaks. Take permitted photographs separately if needed."],
["Inventory","Compare the handed-over items and their condition with the agreed inventory."],
["Meters and services","Note accessible water and electricity readings, date and billing arrangements. Do not open equipment or electrical panels."],
["Connectivity and appliances","Clarify internet activation and normal operation of accessible appliances. Do not perform hazardous tests."],
["Documents received","Compare copies of agreed documents and receipts for payments already made. Do not mark missing documents as received."],
["Reporting defects","Clarify whom to notify about defects, how to report them and how to record the response."],
["Returning the property","Note the agreed key-return, inspection and settlement arrangements for move-out. This checklist does not replace the agreement."]],
"summary":"Item statuses","reset":"Reset all marks","nav":"Back to rental journey","other":"Русский",
"warning":"Personal marks are not a handover certificate, safety assurance or legal conclusion. Do not enter addresses, names, contact details or document data here.",
"privacy":"Local review draft: the tool does not store or send your marks. Your browser may restore values. Record important outcomes separately before leaving."}}
CSS="""*{box-sizing:border-box}body{margin:0;background:#0d1320;color:#eef4fc;font:1rem/1.6 system-ui,sans-serif}main{max-width:880px;margin:auto;padding:24px}h1,h2,h3{line-height:1.3;overflow-wrap:anywhere}a{color:#8ef5df;text-decoration:underline}nav{display:flex;flex-wrap:wrap;gap:16px;margin:12px 0 24px}.items{display:grid;gap:12px;list-style:none;margin:0;padding:0}.items li{border:1px solid #61728a;border-radius:14px;padding:16px;min-width:0}.items p{margin:6px 0 12px}.items h3{margin:0}select,button{max-width:100%;font:inherit;background:#152338;color:inherit;border:1px solid #8192aa;border-radius:8px;padding:10px}select{width:100%}a:focus-visible,select:focus-visible,button:focus-visible{outline:3px solid #39e1c6;outline-offset:3px}.counts{display:flex;flex-wrap:wrap;gap:10px;padding:0;list-style:none}.counts li{border:1px solid #61728a;border-radius:8px;padding:8px}button{cursor:pointer}small{display:block;color:#b8c8da;margin-top:16px}"""
JS="""(()=>{"use strict";const selects=[...document.querySelectorAll('.items select')];const counters=[...document.querySelectorAll('[data-count]')];function render(){const totals=[0,0,0,0];for(const s of selects){totals[Number(s.value)]++;}for(const c of counters)c.textContent=String(totals[Number(c.dataset.count)]);}for(const s of selects)s.addEventListener('change',render);document.getElementById('reset').addEventListener('click',()=>{for(const s of selects)s.value='0';render();selects[0].focus();});render();})();"""
def sha(b):return hashlib.sha256(b).hexdigest()
def csp(s):return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def route(l):return "/preview-tools/"+l+"/rental-move-in.html"
def guide(l):return "/preview-tools/"+l+"/rental-journey.html"
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def render(l):
 c=COPY[l];e=html.escape;other="en" if l=="ru" else "ru"
 opts="".join(f'<option value="{i}">{e(label)}</option>' for i,label in enumerate(c["labels"]))
 rows="".join(f'<li><h3 id="item-{i}-label">{e(title)}</h3><p id="item-{i}-hint">{e(desc)}</p><select id="item-{i}" aria-labelledby="item-{i}-label" aria-describedby="item-{i}-hint" autocomplete="off">{opts}</select></li>' for i,(title,desc) in enumerate(c["items"],1))
 counts="".join(f'<li>{e(label)}: <strong data-count="{i}">{8 if i==0 else 0}</strong></li>' for i,label in enumerate(c["labels"]))
 policy=f"default-src 'none'; script-src 'sha256-{csp(JS)}'; style-src 'sha256-{csp(CSS)}'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
 return (f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta http-equiv="Content-Security-Policy" content="{e(policy,quote=True)}"><title>{e(c["title"])}</title><style>{CSS}</style></head><body><main><nav><a href="{guide(l)}">{e(c["nav"])}</a><a href="{route(other)}" lang="{other}">{e(c["other"])}</a></nav><h1>{e(c["title"])}</h1><p>{e(c["intro"])}</p><p>{e(c["warning"])}</p><h2>{e(c["summary"])}</h2><ul class="counts" role="status" aria-live="polite">{counts}</ul><ol class="items" role="list">{rows}</ol><p><button type="button" id="reset">{e(c["reset"])}</button></p><small>{e(c["privacy"])}</small></main><script>{JS}</script></body></html>\n').encode()
def build(manifest,r6):
 need(sha(manifest)==MANIFEST,"parent manifest")
 out={}
 for path,pin in PINS.items():
  raw=(r6/path).read_bytes();need(sha(raw)==pin,"R6 pin "+path)
  if path.endswith("/rental-journey.html"):
   l=path.split("/")[1];s=raw.decode();anchor="</ul></nav>"
   need(s.count(anchor)==1 and route(l) not in s,"guide nav boundary")
   link=f'<li><a class="pu-s082" href="{route(l)}">{html.escape(COPY[l]["title"])}</a></li>'
   new=s.replace(anchor,link+anchor,1);need(new.replace(link,"",1)==s,"guide preservation")
   out[path]=new.encode()
  else:out[path]=raw
 for l in COPY:out[route(l).lstrip("/")]=render(l)
 for l in COPY:
  page=out[route(l).lstrip("/")].decode();tags=Tags(page).tags
  ids=[a["id"] for t,a in tags if "id" in a]
  need(len(ids)==len(set(ids)) and sum(t=="select" for t,a in tags)==8,"unique IDs and eight items")
  need(sum(t=="option" for t,a in tags)==32,"four states each")
  need(not any(t in {"form","input","textarea","iframe"} for t,a in tags),"no personal fields or submission")
  need([(t,a["href"]) for t,a in tags if "href" in a]==[("a",guide(l)),("a",route("en" if l=="ru" else "ru"))],"local links")
  need(any(a.get("name")=="robots" and "noindex" in a.get("content","") for t,a in tags),"noindex")
  g=out[guide(l).lstrip("/")].decode();need(sum(a.get("href")==route(l) for t,a in Tags(g).tags)==1,"guide entry")
 need(len(out)==10 and all(len(b)<=38912 for b in out.values()),"historical per-file cap")
 report={n:{"sha256":sha(b),"bytes":len(b),"old_sha256":PINS.get(n),"changed":PINS.get(n)!=sha(b)} for n,b in out.items()}
 need(sum(v["changed"] for v in report.values())==4,"two guides plus two new pages")
 return out,{"base":BASE,"r6":R6,"scope":"MOVE_IN_DRAFT_ONLY","files":report,"release_approval":False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--r6",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 need(out!=repo and repo not in out.parents and not out.exists(),"new external directory")
 files,report=build(git("show",BASE+":deploy/live/_release.json"),a.r6)
 out.mkdir(parents=True,exist_ok=False)
 for name,b in files.items():
  f=out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
