"""R6 personal note export for the exact R5 shortlist; draft only.
Run: python build_note.py --repo <checkout> --r5 <R5 preview dir> --output <new external dir>
Explicit local text generation; no automatic clipboard, download, storage or network.
"""
import argparse,base64,hashlib,html,json,re,subprocess
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
R5="8dc243e1f0764ac3c833ece07b690fa57d0e9b6d"
PINS={
"phuket-universe.html":"a231e27e1687ad4229b2ebf863d6b00a50cfa0e17f7b7e8b7f9657e16798c325",
"en/phuket-universe.html":"abbea4cc42de6bf639a4e1bed51556aee4428a5538f8d7f8f3199a5280ec7b9b",
"preview-tools/ru/rental-journey.html":"0d18e96bd3ea52d5bf71097c84c27d13f3b18c31ccc292ce9f52443aea73fea7",
"preview-tools/en/rental-journey.html":"0912f4886e2abca74ec467fb4f1d224af891506725ade1c53a1abd67cccb1c60",
"preview-tools/ru/rental-budget-calculator.html":"0b3c1d338e221fe774903ec5f2ba54d208df23bad19fd3f368b2b7a8a64d8be7",
"preview-tools/en/rental-budget-calculator.html":"73642f56ec0c7c24f99a1a3999a8f15b466c8fea5291fab36931b2c485efe304",
"preview-tools/ru/rental-shortlist.html":"f40e5ade1104cacf533874288bc81f93b3a22fbe94812da3c6919785b6512648",
"preview-tools/en/rental-shortlist.html":"95d88a676c488c1dc45198c6d51de731015014f8a6923776dc7ae6fbd05b101b"}
COPY={
"ru":{"title":"Заметка для себя","intro":"Отметьте нужные варианты в личном списке, затем сформируйте текст. Его можно выделить и вручную скопировать. Инструмент ничего не отправляет и не записывает в буфер автоматически. Не включайте персональные данные.","generate":"Сформировать заметку","select":"Выделить текст","output":"Текст личной заметки","initial":"Заметка ещё не сформирована.","empty":"Отметьте хотя бы один заполненный вариант.","invalid":"Исправьте некорректные суммы в бюджете или отмеченных вариантах.","ready":"Заметка готова. Выделите и скопируйте её вручную.","stale":"Данные изменились. Сформируйте заметку заново.","selected":"Текст выделен. Скопируйте его вручную.","heading":"Phuket Universe — личная заметка","warning":"Личные записи, не объявление, не заявка и не подтверждение наличия."},
"en":{"title":"Personal note","intro":"Mark the options you want to keep, then generate a text note. Select it and copy it manually. The tool neither sends it nor writes to your clipboard automatically. Do not include personal data.","generate":"Generate note","select":"Select text","output":"Personal note text","initial":"No note generated yet.","empty":"Mark at least one filled-in option.","invalid":"Correct invalid amounts in the budget or marked options.","ready":"Note ready. Select and copy it manually.","stale":"Values changed. Generate the note again.","selected":"Text selected. Copy it manually.","heading":"Phuket Universe — personal note","warning":"Personal notes, not a listing, enquiry or availability confirmation."}}
CSS=".personal-note{margin:24px 0}.personal-note textarea{display:block;width:100%;min-height:240px;resize:vertical;padding:12px;border:1px solid #8192aa;border-radius:8px;color:inherit;background:#152338;font:inherit;white-space:pre-wrap}.personal-note textarea:focus-visible{outline:3px solid #39e1c6;outline-offset:3px}.personal-note button:disabled{opacity:.55;cursor:default}"
JS=r"""(()=>{"use strict";const g=id=>document.getElementById(id),t=JSON.parse(g('copy').textContent),n=JSON.parse(g('note-copy').textContent),out=g('note-output'),status=g('note-status'),select=g('note-select');const fields=[...document.querySelectorAll('input,select')];const nf=new Intl.NumberFormat(document.documentElement.lang==='ru'?'ru-RU':'en-US');const clean=s=>s.replace(/[\u0000-\u001f\u007f-\u009f\u2028\u2029\u202a-\u202e\u2066-\u2069]/g,' ').trim().replace(/\s+/g,' ');const value=s=>clean(s)||t.unknown;function amount(el){const s=el.value,k=Number(s);if(s===''&&!el.validity.badInput)return{valid:true,text:t.unknown};return /^[0-9]+$/.test(s)&&Number.isSafeInteger(k)&&k>=0&&k<=1000000000?{valid:true,text:nf.format(k)+' THB'}:{valid:false};}function term(el){return el.options[el.selectedIndex].textContent;}function clear(msg){out.value='';select.disabled=true;status.textContent=msg;}function invalidate(){if(out.value)clear(n.stale);}function generate(){const ids=[1,2,3].filter(i=>g('keep'+i).checked&&!g('keep'+i).disabled);if(!ids.length){clear(n.empty);return;}const budget=amount(g('budget'));const rents=ids.map(i=>amount(g('rent'+i)));if(!budget.valid||rents.some(x=>!x.valid)){clear(n.invalid);return;}const lines=[n.heading,n.warning,'',t.budget+': '+budget.text,t.wanted+': '+term(g('wanted'))];ids.forEach((i,j)=>{lines.push('',t.option+' '+i,t.alias+': '+value(g('alias'+i).value),t.area+': '+value(g('area'+i).value),t.rent+': '+rents[j].text,t.term+': '+term(g('term'+i)),g('summary'+i).textContent,g('budgetResult'+i).textContent,g('termResult'+i).textContent,g('sourceResult'+i).textContent);});out.value=lines.join('\n');select.disabled=false;status.textContent=n.ready;}fields.forEach(x=>{x.addEventListener('input',invalidate);x.addEventListener('change',invalidate);});g('example').addEventListener('click',()=>clear(n.initial));g('reset').addEventListener('click',()=>clear(n.initial));g('note-generate').addEventListener('click',generate);select.addEventListener('click',()=>{if(!out.value)return;out.focus();out.select();status.textContent=n.selected;});clear(n.initial);})();"""
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def csp(s):return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()
def once(s,a,b):
 need(s.count(a)==1,"unique boundary "+a[:60]);return s.replace(a,b,1)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def modify(raw,l):
 old=raw.decode();c=COPY[l];e=html.escape
 section=f'<section class="personal-note" id="personal-note" aria-labelledby="note-title"><h2 id="note-title">{e(c["title"])}</h2><p>{e(c["intro"])}</p><button type="button" id="note-generate">{e(c["generate"])}</button><button type="button" id="note-select" disabled>{e(c["select"])}</button><label for="note-output">{e(c["output"])}</label><textarea id="note-output" readonly autocomplete="off" aria-describedby="note-status"></textarea><p id="note-status" role="status">{e(c["initial"])}</p></section>'
 data=json.dumps(c,ensure_ascii=False).replace("<","\\u003c")
 appended=f'<script id="note-copy" type="application/json">{data}</script><script>{JS}</script>'
 styles=re.findall(r'<style>(.*?)</style>',old,re.S);need(len(styles)==1,"old style")
 style=styles[0];newstyle=style+CSS
 script_hashes=re.findall(r"sha256-[A-Za-z0-9+/=]+",old.split("style-src",1)[0]);need(len(script_hashes)==1,"original script CSP")
 oldscript=script_hashes[0];addhash="sha256-"+csp(JS)
 s=once(old,"<style>"+style+"</style>","<style>"+newstyle+"</style>")
 s=once(s,"sha256-"+csp(style),"sha256-"+csp(newstyle))
 s=once(s,oldscript,oldscript+"&#x27; &#x27;"+addhash)
 s=once(s,'<nav class="tool-nav"',section+'<nav class="tool-nav"')
 s=once(s,"</body>",appended+"</body>")
 # Check all old bytes apart from the explicit insertion and hash/style edits.
 restored=once(s,appended,"");restored=once(restored,section,"")
 restored=once(restored,oldscript+"&#x27; &#x27;"+addhash,oldscript)
 restored=once(restored,"sha256-"+csp(newstyle),"sha256-"+csp(style))
 restored=once(restored,"<style>"+newstyle+"</style>","<style>"+style+"</style>")
 need(restored==old,"old page preservation")
 tags=Tags(s).tags;ids=[a["id"] for t,a in tags if "id" in a]
 need(len(ids)==len(set(ids)),"unique ids")
 need(not any(t=="form" for t,a in tags),"no submission")
 need(sum(t=="textarea" and a.get("id")=="note-output" and "readonly" in a for t,a in tags)==1,"readonly note")
 need(any(a.get("name")=="robots" and "noindex" in a.get("content","") for t,a in tags),"noindex")
 need(len(s.encode())<=38912,"historical per-file cap")
 return s.encode()
def build(manifest,r5):
 need(sha(manifest)==MANIFEST,"parent manifest")
 out={};report={}
 for path,pin in PINS.items():
  b=(r5/path).read_bytes();need(sha(b)==pin,"R5 pin "+path)
  changed=path.endswith("/rental-shortlist.html")
  out[path]=modify(b,path.split("/")[1]) if changed else b
  report[path]={"old_sha256":pin,"sha256":sha(out[path]),"bytes":len(out[path]),"changed":changed}
 need(sum(v["changed"] for v in report.values())==2,"two shortlist variants only")
 return out,{"base":BASE,"r5":R5,"scope":"PERSONAL_NOTE_DRAFT_ONLY","files":report,"release_approval":False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--r5",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 need(out!=repo and repo not in out.parents and not out.exists(),"new external directory")
 files,report=build(git("show",BASE+":deploy/live/_release.json"),a.r5)
 out.mkdir(parents=True,exist_ok=False)
 for name,b in files.items():
  f=out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
