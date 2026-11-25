"""Isolated RU/EN viewing checklist. Draft only; no release authority.
Run: python build_candidate.py --repo <checkout> [--output <new directory outside checkout>]
Uses exact Git parent files. Never modifies deploy/live or inventory.
"""
import argparse, hashlib, html, json, subprocess
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
RELEASE="AISL_RESTORED_GUIDES_R1_20261122"
PAYLOAD="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
CSS_SHA="c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"
PINS={
 "ru":("phuket-universe.html","2b7c61e013d25815d27b98bb64db9357a64c36a7ec2e6c53a5dfc0ccf357de3a"),
 "en":("en/phuket-universe.html","74f02c92d9595673c289b6dc714a32c8fa099f565fa7272194967fd6befdb9ba"),
}
COPY={
 "ru":("Перед просмотром","Пять вопросов о жилье",
 "Раскройте вопросы и выпишите ответы для себя. Если ответ неизвестен, оставьте его открытым. Секция не отправляет сообщения и не сохраняет ваши данные.",
 [("Этот объект ещё свободен?","Сверьте ссылку, адрес или номер объекта, дату доступности и время последнего подтверждения. Старая карточка не гарантирует наличие."),
 ("Сколько стоит мой срок аренды?","Запишите цену за месяц именно на ваш срок, что включено, что оплачивается отдельно, и когда действует эта цена."),
 ("Какая сумма нужна до заселения?","Разделите первый платёж, депозит, разовые расходы и сроки их оплаты. Уточните условия возврата депозита."),
 ("Что проверить на месте?","Сверьте состояние объекта, воду, электричество, интернет, шум, доступ и перечень имущества. Уточните, кто отвечает за ремонт."),
 ("Кто подписывает договор и получает оплату?","До оплаты проверьте полномочия получателя, письменные условия и соответствие реквизитов договору. Не переводите деньги только на основании объявления.")],
 "К фильтрам жилья","Это личный список вопросов, а не проверка объекта, бронь или гарантия сделки."),
 "en":("Before a viewing","Five questions about a rental",
 "Expand the questions and note the answers for yourself. Leave unknown answers open. This section neither sends messages nor stores your information.",
 [("Is this property still available?","Check the link, address or listing reference, available date and last confirmation. An old listing does not guarantee availability."),
 ("What is the price for my rental term?","Note the monthly price for your exact term, what is included, what is billed separately and when that price applies."),
 ("How much cash is due before moving in?","Separate the first payment, deposit, one-off charges and payment dates. Check the deposit refund conditions."),
 ("What should I inspect in person?","Check the condition, water, electricity, internet, noise, access and inventory. Ask who is responsible for repairs."),
 ("Who signs the agreement and receives payment?","Before paying, verify the recipient's authority, written terms and whether payment details match the agreement. Do not transfer money solely on the basis of a listing.")],
 "Back to housing filters","This is a personal question list, not property verification, a reservation or a transaction guarantee."),
}
def need(ok,msg):
 if not ok: raise ValueError(msg)
def sha(raw): return hashlib.sha256(raw).hexdigest()
class Tags(HTMLParser):
 def __init__(self,source):
  super().__init__(convert_charrefs=True);self.tags=[];self.feed(source);self.close()
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
def section(locale):
 label,title,intro,questions,cta,note=COPY[locale];e=html.escape
 rows="\n".join('<li class="pu-s103"><span class="pu-s104" aria-hidden="true">'+str(i)+'</span><div class="pu-s072"><details><summary class="pu-s105">'+e(q)+'</summary><p class="pu-s106">'+e(a)+'</p></details></div></li>' for i,(q,a) in enumerate(questions,1))
 return ('<section class="pu-s039" id="rental-viewing-checklist" aria-labelledby="rental-viewing-checklist-title"><div class="pu-s096 pu-pad"><div class="pu-s097"><div class="pu-s098"><span class="pu-s014">'+e(label)+'</span><h2 class="pu-s099" id="rental-viewing-checklist-title">'+e(title)+'</h2><p class="pu-s044">'+e(intro)+'</p><p class="pu-s095">'+e(note)+'</p><a class="pu-s082" href="#homes">'+e(cta)+'</a></div><ol class="pu-s102" role="list">'+rows+'</ol></div></div></section>\n\n')
def build(read):
 m=json.loads(read("_release.json"));need(m["release_id"]==RELEASE and m["payload_sha256"]==PAYLOAD,"parent manifest")
 pins={x["path"]:x for x in m["files"]};need(len(pins)==len(m["files"])==116,"inventory")
 css=read("phuket-universe.css");need(sha(css)==CSS_SHA==pins["phuket-universe.css"]["sha256"],"CSS pin")
 out={};report=[]
 for locale,(name,pin) in PINS.items():
  raw=read(name);need(sha(raw)==pin==pins[name]["sha256"] and len(raw)==pins[name]["size"],"page pin")
  old=raw.decode("utf-8");anchor='<section class="pu-s039" id="agencies">'
  need(old.count(anchor)==1 and "rental-viewing-checklist" not in old,"anchor")
  frag=section(locale);tags=Tags(frag).tags
  need(sum(t=="details" for t,a in tags)==sum(t=="summary" for t,a in tags)==sum(t=="li" for t,a in tags)==5,"5 disclosures")
  need(all("open" not in a for t,a in tags if t=="details"),"collapsed by default")
  need([(t,a["href"]) for t,a in tags if "href" in a]==[("a","#homes")],"local link")
  need(not any(t in {"script","style","form","input","button","iframe","img","link"} for t,a in tags),"no active content")
  need(not any(any(k.startswith(("on","data-")) or k=="style" for k in a) for t,a in tags),"no events/data hooks")
  need(all(("."+c).encode() in css for t,a in tags for c in a.get("class","").split()),"existing styles")
  new=old.replace(anchor,frag+anchor,1);need(new.replace(frag,"",1).encode()==raw,"preserve parent")
  before,after=Tags(old).tags,Tags(new).tags
  need([a.get("id") for t,a in after if t=="section"]==["top","orbit","homes","rental-viewing-checklist","agencies"],"section order")
  ids=[a["id"] for t,a in after if "id" in a]
  need(ids.count("rental-viewing-checklist")==ids.count("rental-viewing-checklist-title")==ids.count("homes")==1,"unique new and CTA ids")
  need(sum("data-u2-catalog" in a for t,a in after)==1 and not any("data-u2-card" in a for t,a in after),"empty catalogue")
  need([(t,a) for t,a in before if t in {"script","form","link"}]==[(t,a) for t,a in after if t in {"script","form","link"}],"preserve active assets")
  out[name]=new.encode();report.append({"locale":locale,"source_sha256":pin,"candidate_sha256":sha(out[name]),"added_bytes":len(out[name])-len(raw),"disclosures":5,"structure":"PASS"})
 return out,{"base":BASE,"parent_release":RELEASE,"scope":"DRAFT_ONLY","pages":report}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",type=Path,required=True);p.add_argument("--output",type=Path);args=p.parse_args()
 repo=args.repo.resolve()
 git=lambda *a:subprocess.check_output(["git","-C",str(repo),*a])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 out,report=build(lambda name:git("show",BASE+":deploy/live/"+name))
 if args.output:
  dest=args.output.resolve();need(dest!=repo and repo not in dest.parents and not dest.exists(),"new directory outside repository")
  dest.mkdir(parents=True,exist_ok=False)
  for name,raw in out.items():
   target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  (dest/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
