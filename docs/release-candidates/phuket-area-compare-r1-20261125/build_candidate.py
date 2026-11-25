"""Phuket Universe: compare two areas, RU/EN, isolated draft.
Run: python build_candidate.py --repo <checkout> [--output <new-directory-outside-checkout>]
Read-only Git baseline. No live payload mutation or release authority.
"""
import argparse, hashlib, html, json, subprocess
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
RELEASE="AISL_RESTORED_GUIDES_R1_20261122"
PAYLOAD="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
CSS_SHA="c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"
PINS={"ru":("phuket-universe.html","2b7c61e013d25815d27b98bb64db9357a64c36a7ec2e6c53a5dfc0ccf357de3a"),"en":("en/phuket-universe.html","74f02c92d9595673c289b6dc714a32c8fa099f565fa7272194967fd6befdb9ba")}
COPY={
 "ru":("Выбор района","Сравните два района",
 "Выберите для себя два района. Отмечайте только те условия, которые проверили лично. Сравнивайте прежде всего важные для вас условия, а не число галочек.",
 ["Район А","Район Б"],
 ["Проверены время и удобство ежедневного маршрута.","Проверены пеший путь и доступ к нужным магазинам и услугам.","Проверены транспорт и варианты возвращения домой в нужные часы.","Проверены шум и освещение утром или вечером, когда это важно.","Проверены доступность подходящего интернета и мобильной связи."],
 "К фильтрам жилья","Секция не отправляет и не сохраняет отметки на сервере; браузер может восстановить их. Отметки не подтверждают наличие или качество жилья."),
 "en":("Choosing an area","Compare two areas",
 "Choose two areas for yourself. Tick only the conditions you have personally checked. Compare the conditions that matter to you, not the number of ticks.",
 ["Area A","Area B"],
 ["Checked the time and convenience of daily journeys.","Checked walking routes and access to needed shops and services.","Checked transport and ways to get home at the times that matter.","Checked noise and lighting at relevant morning or evening times.","Checked access to suitable internet and mobile coverage."],
 "Back to housing filters","This section does not send or store ticks on a server; your browser may restore them. Ticks do not confirm housing availability or quality."),
}
def need(ok,msg):
 if not ok: raise ValueError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
class Tags(HTMLParser):
 def __init__(self,source):
  super().__init__(convert_charrefs=True);self.tags=[];self.feed(source);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def section(l):
 label,title,intro,groups,questions,cta,note=COPY[l];e=html.escape
 blocks=[]
 for group,name in zip(("a","b"),groups):
  gid="area-compare-"+group;rows=[]
  for i,q in enumerate(questions,1):
   key=gid+"-"+str(i)
   rows.append(f'<li class="pu-s103"><input type="checkbox" id="{key}"><label class="pu-s106" for="{key}">{e(q)}</label></li>')
  blocks.append(f'<div class="pu-s098" role="group" aria-labelledby="{gid}"><h3 class="pu-s105" id="{gid}">{e(name)}</h3><ul class="pu-s102" role="list">'+"\n".join(rows)+"</ul></div>")
 return ('<section class="pu-s039" id="area-compare" aria-labelledby="area-compare-title"><div class="pu-s096 pu-pad"><div class="pu-s098"><span class="pu-s014">'+e(label)+'</span><h2 class="pu-s099" id="area-compare-title">'+e(title)+'</h2><p class="pu-s044">'+e(intro)+'</p></div><div class="pu-s097">'+"\n".join(blocks)+'</div><p class="pu-s095">'+e(note)+'</p><a class="pu-s082" href="#homes">'+e(cta)+'</a></div></section>\n\n')
def build(read):
 m=json.loads(read("_release.json"));need(m["release_id"]==RELEASE and m["payload_sha256"]==PAYLOAD,"manifest")
 pins={x["path"]:x for x in m["files"]};need(len(pins)==len(m["files"])==116,"inventory")
 css=read("phuket-universe.css");need(sha(css)==CSS_SHA==pins["phuket-universe.css"]["sha256"],"CSS")
 out={};rows=[]
 for l,(name,pin) in PINS.items():
  raw=read(name);need(sha(raw)==pin==pins[name]["sha256"] and len(raw)==pins[name]["size"],"page pin")
  old=raw.decode("utf-8");anchor='<section class="pu-s039" id="agencies">'
  need(old.count(anchor)==1 and 'id="area-compare"' not in old,"anchor")
  frag=section(l);tags=Tags(frag).tags
  inputs=[a for t,a in tags if t=="input"];labels=[a["for"] for t,a in tags if t=="label"]
  need(len(inputs)==len(labels)==10 and len(set(labels))==10,"ten independent controls")
  need(all(set(a)=={"id","type"} and a["type"]=="checkbox" for a in inputs),"local unchecked inputs only")
  need(sorted(labels)==sorted(a["id"] for a in inputs),"label binding")
  need(sum(a.get("role")=="group" for t,a in tags)==2,"two groups")
  need([(t,a["href"]) for t,a in tags if "href" in a]==[("a","#homes")],"local link")
  need(not any(t in {"script","style","form","button","iframe","img","link","textarea","select"} for t,a in tags),"no active submit or scripts")
  need(not any(any(k.startswith(("on","data-")) or k=="style" for k in a) for t,a in tags),"no data hooks")
  need(all(("."+c).encode() in css for t,a in tags for c in a.get("class","").split()),"existing styles")
  new=old.replace(anchor,frag+anchor,1);need(new.replace(frag,"",1).encode()==raw,"parent preservation")
  before,after=Tags(old).tags,Tags(new).tags
  ids=[a["id"] for t,a in after if "id" in a]
  for t,a in tags:
   if "id" in a:need(ids.count(a["id"])==1,"unique new ID")
  need(ids.count("homes")==1,"CTA target")
  need(sum("data-u2-catalog" in a for t,a in after)==1 and not any("data-u2-card" in a for t,a in after),"empty catalogue")
  need([(t,a) for t,a in before if t in {"script","form","link"}]==[(t,a) for t,a in after if t in {"script","form","link"}],"active assets unchanged")
  out[name]=new.encode();rows.append({"locale":l,"source_sha256":pin,"candidate_sha256":sha(out[name]),"added_bytes":len(out[name])-len(raw),"checkboxes":10,"structure":"PASS"})
 return out,{"base":BASE,"parent_release":RELEASE,"scope":"DRAFT_ONLY","pages":rows}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",type=Path,required=True);p.add_argument("--output",type=Path);args=p.parse_args()
 repo=args.repo.resolve();git=lambda *a:subprocess.check_output(["git","-C",str(repo),*a])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 out,report=build(lambda n:git("show",BASE+":deploy/live/"+n))
 if args.output:
  dest=args.output.resolve();need(dest!=repo and repo not in dest.parents and not dest.exists(),"new directory outside repo")
  dest.mkdir(parents=True,exist_ok=False)
  for n,raw in out.items():
   f=dest/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
  (dest/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
