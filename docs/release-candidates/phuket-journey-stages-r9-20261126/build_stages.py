"""R9 stage navigation for the exact R8 Phuket rental journey.
Draft preview only. No changes to live releases, inventory or data handling.
Run: python build_stages.py --repo <checkout> --r8 <preview dir> --output <new external dir>
"""
import argparse,hashlib,html,json,re,subprocess
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
R8="10676f62d13b37c8e8603ff41b1ebb3856828f67"
CSS_SHA="c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"
PINS={
"phuket-universe.html":"a231e27e1687ad4229b2ebf863d6b00a50cfa0e17f7b7e8b7f9657e16798c325",
"en/phuket-universe.html":"abbea4cc42de6bf639a4e1bed51556aee4428a5538f8d7f8f3199a5280ec7b9b",
"preview-tools/ru/rental-journey.html":"34fe769f6f4e781c4ea34b278bc7773849f0cefef2cf39bd845de2f0ad522f6b",
"preview-tools/en/rental-journey.html":"cce5e94cdbd44cd8703ad027bd5f2f698bfaf11b3b36c7cd130fa96850a8e147",
"preview-tools/ru/rental-budget-calculator.html":"0b3c1d338e221fe774903ec5f2ba54d208df23bad19fd3f368b2b7a8a64d8be7",
"preview-tools/en/rental-budget-calculator.html":"73642f56ec0c7c24f99a1a3999a8f15b466c8fea5291fab36931b2c485efe304",
"preview-tools/ru/rental-shortlist.html":"014841064db6f010780fce536221704700c40c62d049abe8659a05cde0c2418d",
"preview-tools/en/rental-shortlist.html":"91ac7f29e59ecd43a9defc8515dfb3ad07ad8bbd5df90cd79544181bee6b4834",
"preview-tools/ru/rental-move-in.html":"ddee53772565a7fce82b098eaadd309338ec22dc2c39d94a4a1c38c3f8f74ac7",
"preview-tools/en/rental-move-in.html":"f00b8f807bd1cfbe0bb823f09e29cb447b2810def906083a8c8480b07da553f8",
"preview-tools/ru/rental-move-out.html":"52eae55df3b93785ad98fcad81be8b56da2bf402f4c6de9ef5371b566df98c20",
"preview-tools/en/rental-move-out.html":"8d79f72033a2733e41eb809176fbe483dc6f8fab102eda563054a177efe3f05a"}
STAGES={
"ru":[("Поиск и район","Выберите район и условия, затем перейдите к фильтрам жилья."),("Сравнение вариантов","Сверьте бюджет, срок аренды и вопросы перед просмотром."),("Заселение","Зафиксируйте состояние, ключи, опись и показания."),("Выезд","Сверьте документы, передачу жилья и фактический возврат депозита.")],
"en":[("Search and area","Choose your area and criteria, then open the housing filters."),("Compare options","Check your budget, lease term and questions before a viewing."),("Move-in","Record condition, keys, inventory and meter readings."),("Move-out","Check the records, return of the property and the refund actually received.")]}
# Indices are positions in the exact nine-link R8 navigation, not invented routes.
GROUPS=((0,1,6),(2,4,5,3),(7,),(8,))
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def modify(raw,l,css):
 old=raw.decode()
 start='<nav aria-labelledby="rental-journey-title">'
 need(old.count(start)==1,"unique journey nav")
 i=old.index(start);j=old.index("</nav>",i)+len("</nav>");original=old[i:j]
 items=re.findall(r'<li>(<a class="pu-s082" href="[^"]+">[^<]+</a>)</li>',original)
 need(len(items)==9,"exact nine original links")
 need(original==start+'<ul class="pu-s102" role="list">'+''.join('<li>'+a+'</li>' for a in items)+'</ul></nav>',"nav boundary")
 destinations=[a["href"] for t,a in Tags(original).tags if t=="a"]
 root="/preview-tools/"+l+"/rental-";parent="/phuket-universe" if l=="ru" else "/en/phuket-universe"
 need(destinations==["#rental-search-plan","#area-compare","#rental-cost-compare","#rental-viewing-checklist",root+"budget-calculator.html",root+"shortlist.html",parent+"#homes",root+"move-in.html",root+"move-out.html"],"exact R8 destinations")
 need(all(("."+c).encode() in css for c in ["pu-s097","pu-pad","pu-s098","pu-s105","pu-s095","pu-s102","pu-s072","pu-s082"]),"existing styles")
 parts=[]
 for n,((title,desc),indices) in enumerate(zip(STAGES[l],GROUPS),1):
  gid="rental-stage-"+str(n)
  links="".join('<li class="pu-s072">'+items[k]+'</li>' for k in indices)
  parts.append(f'<div class="pu-s098" role="group" aria-labelledby="{gid}"><h2 id="{gid}" class="pu-s105">{n:02d} · {html.escape(title)}</h2><p class="pu-s095">{html.escape(desc)}</p><ul class="pu-s102" role="list">{links}</ul></div>')
 newnav='<nav class="pu-s097 pu-pad" aria-labelledby="rental-journey-title">'+"".join(parts)+'</nav>'
 new=old[:i]+newnav+old[j:]
 need(new.replace(newnav,original,1)==old,"byte preservation outside nav")
 oldtags,newtags=Tags(original).tags,Tags(newnav).tags
 need(Counter(tuple(sorted(a.items())) for t,a in oldtags if t=="a")==Counter(tuple(sorted(a.items())) for t,a in newtags if t=="a"),"unchanged link attributes")
 need(sorted(re.findall(r'<a\b[^>]*>[^<]+</a>',newnav))==sorted(items),"unchanged original link text")
 need(sum(a.get("role")=="group" for t,a in newtags)==4,"four groups")
 need(not any(t in {"script","style","form","input","button"} for t,a in newtags),"native nav only")
 ids=[a["id"] for t,a in Tags(new).tags if "id" in a]
 need(len(ids)==len(set(ids)),"unique IDs")
 return new.encode()
def build(manifest,css,r8):
 need(sha(manifest)==MANIFEST,"parent manifest")
 need(sha(css)==CSS_SHA,"exact CSS")
 out={}
 for n,pin in PINS.items():
  b=(r8/n).read_bytes();need(sha(b)==pin,"R8 pin "+n)
  out[n]=modify(b,n.split("/")[1],css) if n.endswith("/rental-journey.html") else b
 need(len(out)==12 and all(len(b)<=38912 for b in out.values()),"historical per-file cap")
 report={n:{"sha256":sha(b),"bytes":len(b),"old_sha256":PINS[n],"changed":PINS[n]!=sha(b)} for n,b in out.items()}
 need(sum(v["changed"] for v in report.values())==2,"only two guide pages")
 return out,{"base":BASE,"r8":R8,"scope":"STAGE_NAV_DRAFT_ONLY","files":report,"release_approval":False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--r8",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 need(out!=repo and repo not in out.parents and not out.exists(),"new external directory")
 files,report=build(git("show",BASE+":deploy/live/_release.json"),git("show",BASE+":deploy/live/phuket-universe.css"),a.r8)
 out.mkdir(parents=True,exist_ok=False)
 for n,b in files.items():
  f=out/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
