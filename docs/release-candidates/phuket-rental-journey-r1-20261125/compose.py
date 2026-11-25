"""Rental journey RU/EN: isolated composition of five exact draft candidates.
Inputs are their generated preview directories, never live inventory.
Run: python compose.py --repo <checkout> --plan <dir> --cost <dir> --viewing <dir>
 --areas <dir> --calculator <dir> --output <new dir outside repository>
Use the five pinned PR heads below to reproduce the input previews. No merge,
deploy/live mutation or release authority. Calculator is a separate local page.
"""
import argparse,hashlib,html,json,subprocess
from pathlib import Path
from html.parser import HTMLParser
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
RELEASE="AISL_RESTORED_GUIDES_R1_20261122"
PAYLOAD="f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
CSS="c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"
PARENTS={"ru":("phuket-universe.html","2b7c61e013d25815d27b98bb64db9357a64c36a7ec2e6c53a5dfc0ccf357de3a"),"en":("en/phuket-universe.html","74f02c92d9595673c289b6dc714a32c8fa099f565fa7272194967fd6befdb9ba")}
# Tuple: input role, section ID, source commit, RU/EN generated page SHA256.
SOURCES=[
 ("plan","rental-search-plan","721ffc0800566c5882e68118d4a6f8b78d848fcd","17d3df58ea76c98bdc28d4ba708e884f86a55817ed33722d2479c43e47ee561e","ef61924312feeab1557b60c5c9fa524fee85708533b973728385fba3dd67c530"),
 ("areas","area-compare","89c3ac1acd651d6cfc9596c6b206fb20153825ec","9221c73c855b2942675d93f3b37bbab5956928e35225cbcb242299676b163055","90981986d6ea36453b31e8d7178e744f560b45fe4c79c098e602964186d7b68d"),
 ("cost","rental-cost-compare","62ffc9f7c4143415977b474cc0f5b38415313149","8bb6ba4a4d486e96f262a4b8f2ffa85935de3a0c8be7fc2c7856796303780547","3e4229866d3fee970ba5f7d02e384fcd48726164ff8ac5e96c124503cfbea422"),
 ("viewing","rental-viewing-checklist","203d21b31516e00a9aa8119cbca057ffdc4002fa","c4bc11ce0f9e2d1bc57503e0efe007a8473199fe224e61ee210b1d002ddfd508","1c3195091226852c82871bb838fd1066aa3d1d1474d9fdfc9b593c630bb3eeda")]
CALC={"commit":"fb3744a568390a5c3549a793e3ac22b290aa26ab","ru":"3615d7e9daf0ff1a15b80d320ecb4dc4b66c4f31f0eefc576cd1510f5de9223b","en":"2a37c9bf6010d3fea8c8e8201c1ecc982c14af24f233f45d7f7dfadc352670e6"}
COPY={
"ru":("Маршрут арендатора","Подготовьтесь к поиску жилья на Пхукете","Выберите нужный шаг. Эти инструменты помогают сравнивать условия, но не подтверждают наличие жилья и не создают заявку.","План поиска","Сравнение районов","Пример расчёта расходов","Вопросы перед просмотром","Открыть калькулятор аренды","К фильтрам жилья"),
"en":("Rental journey","Prepare for your Phuket rental search","Choose a step. These tools help compare conditions, but do not confirm availability or create an enquiry.","Search plan","Compare areas","Worked cost comparison","Viewing questions","Open rental calculator","Housing filters")}
ANCHOR='<section class="pu-s039" id="agencies">'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def nav(l):
 label,title,intro,*links=COPY[l];e=html.escape
 targets=["#"+s[1] for s in SOURCES]+["/preview-tools/"+l+"/rental-budget-calculator.html","#homes"]
 items="".join(f'<li><a class="pu-s082" href="{target}">{e(text)}</a></li>' for text,target in zip(links,targets))
 return f'<section class="pu-s039" id="rental-journey" aria-labelledby="rental-journey-title"><div class="pu-s096 pu-pad"><div class="pu-s098"><span class="pu-s014">{e(label)}</span><h2 class="pu-s099" id="rental-journey-title">{e(title)}</h2><p class="pu-s044">{e(intro)}</p><nav aria-labelledby="rental-journey-title"><ul class="pu-s102" role="list">{items}</ul></nav></div></div></section>\n\n'
def compose(read,dirs):
 m=json.loads(read("_release.json"));need(m["release_id"]==RELEASE and m["payload_sha256"]==PAYLOAD,"parent manifest")
 css=read("phuket-universe.css");need(sha(css)==CSS,"CSS pin")
 output={};report=[]
 for l,(name,parentpin) in PARENTS.items():
  raw=read(name);need(sha(raw)==parentpin,"parent HTML")
  old=raw.decode();need(old.count(ANCHOR)==1 and 'id="rental-journey"' not in old,"anchor")
  before,after=old.split(ANCHOR);fragments=[]
  for role,section,commit,ru,en in SOURCES:
   b=(dirs[role]/name).read_bytes();need(sha(b)==(ru if l=="ru" else en),"input pin "+role)
   v=b.decode();need(v.startswith(before) and v.endswith(ANCHOR+after),"parent boundary "+role)
   f=v[len(before):-len(ANCHOR+after)]
   need([a.get("id") for t,a in Tags(f).tags if t=="section"]==[section],"section identity "+role);fragments.append(f)
  n=nav(l)
  joined=n+"".join(fragments);new=before+joined+ANCHOR+after
  need(new.replace(joined,"",1).encode()==raw,"parent preservation")
  tags=Tags(new).tags;ids=[a["id"] for t,a in tags if "id" in a]
  added=Tags(joined).tags
  need(all(ids.count(a["id"])==1 for t,a in added if "id" in a),"unique inserted IDs")
  expected=["top","orbit","homes","rental-journey"]+[s[1] for s in SOURCES]+["agencies"]
  need([a.get("id") for t,a in tags if t=="section"]==expected,"ordered sections")
  need(sum(t=="details" for t,a in added)==5 and sum(t=="input" and a.get("type")=="checkbox" for t,a in added)==10,"native tools")
  need(sum("data-u2-catalog" in a for t,a in tags)==1 and not any("data-u2-card" in a for t,a in tags),"empty inventory")
  need(not any(t in {"script","style","form","iframe"} for t,a in added),"no new active assets on aggregator")
  for t,a in Tags(n).tags:
   if a.get("href","").startswith("#"):need(ids.count(a["href"][1:])==1,"nav anchor")
   for cls in a.get("class","").split():need(("."+cls).encode() in css,"existing style")
  calcpath=l+"/rental-budget-calculator.html";calc=(dirs["calculator"]/calcpath).read_bytes();need(sha(calc)==CALC[l],"calculator pin")
  output["preview-tools/"+calcpath]=calc;output[name]=new.encode()
  report.append({"locale":l,"combined_sha256":sha(output[name]),"calculator_sha256":sha(calc),"sections":expected,"added_bytes":len(output[name])-len(raw),"structure":"PASS"})
 return output,{"base":BASE,"scope":"COMBINED_DRAFT_ONLY","source_heads":[x[2] for x in SOURCES]+[CALC["commit"]],"pages":report}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--output",required=True,type=Path)
 for role in ("plan","cost","viewing","areas","calculator"):p.add_argument("--"+role,required=True,type=Path)
 a=p.parse_args();repo=a.repo.resolve();dest=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"Git baseline")
 need(dest!=repo and repo not in dest.parents and not dest.exists(),"new output outside repository")
 out,report=compose(lambda n:git("show",BASE+":deploy/live/"+n),vars(a))
 dest.mkdir(parents=True,exist_ok=False)
 for name,b in out.items():
  f=dest/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (dest/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
