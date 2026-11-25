"""Phuket rental toolkit R5: link exact R2 journey and R1 shortlist previews.
Draft only. No data transfer between tools, no storage, no live release writes.
Run: python connect.py --repo <checkout> --r2 <preview dir> --shortlist <preview dir>
 --output <new external directory>
"""
import argparse,base64,hashlib,html,json,re,subprocess
from html.parser import HTMLParser
from pathlib import Path
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
R2="7f6c489b57ac6d529e1e129d3b8d04364a8f5243"
SHORTLIST="3b1ea1be33d90da07880fb0167a31dfe86a25aa9"
PINS={
"ru":("phuket-universe.html","a231e27e1687ad4229b2ebf863d6b00a50cfa0e17f7b7e8b7f9657e16798c325","d027f0bfff40fbb52f74c0b4c2a289a9044479610ee4a8a5976431285a0ad4d0","3615d7e9daf0ff1a15b80d320ecb4dc4b66c4f31f0eefc576cd1510f5de9223b","d50c37931c2896e4982651877345dc911906bd2f6f19ee3f3e0dc9d305d1cb20"),
"en":("en/phuket-universe.html","abbea4cc42de6bf639a4e1bed51556aee4428a5538f8d7f8f3199a5280ec7b9b","27933ed6c17232051d2d2043dede24f572063dabf9cc219bc80af049908efbea","2a37c9bf6010d3fea8c8e8201c1ecc982c14af24f233f45d7f7dfadc352670e6","d95e58a549140d3999cc100788d4497691b492e6b5f2da5eb22ae7d0a82fb392")}
COPY={
"ru":("Личная подборка жилья","К калькулятору аренды","К маршруту арендатора","Инструменты арендатора","Значения между страницами не переносятся. При необходимости запишите нужные суммы для себя перед переходом.","English"),
"en":("Personal rental shortlist","Rental calculator","Rental journey","Rental tools","Values are not transferred between pages. Note any amounts you need before navigating.","Русский")}
NAV_CSS=".tool-nav{border-top:1px solid #61728a;margin-top:24px;padding-top:12px}.tool-nav ul{display:flex;flex-wrap:wrap;gap:12px;list-style:none;padding:0}.tool-nav a{display:inline-block;color:#8ef5df;text-decoration:underline;padding:8px;overflow-wrap:anywhere}.tool-nav a:focus-visible{outline:3px solid #39e1c6;outline-offset:3px}.tool-nav p{color:#b8c8da}"
def sha(b):return hashlib.sha256(b).hexdigest()
def csp(s):return base64.b64encode(hashlib.sha256(s.encode()).digest()).decode()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def once(s,old,new):
 need(s.count(old)==1,"unique boundary "+old[:60]);return s.replace(old,new,1)
class Tags(HTMLParser):
 def __init__(self,s):super().__init__(convert_charrefs=True);self.tags=[];self.feed(s);self.close()
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_startendtag(self,t,a):self.handle_starttag(t,a)
def route(l,kind):return "/preview-tools/"+l+"/rental-"+kind+".html"
def checked(path,pin):
 b=path.read_bytes();need(sha(b)==pin,"input pin "+str(path));return b
def add_guide(raw,l):
 s=raw.decode();target=route(l,"budget-calculator")
 pattern=r'<li><a class="pu-s082" href="'+re.escape(target)+r'">[^<]+</a></li>'
 hit=re.findall(pattern,s);need(len(hit)==1,"calculator nav entry")
 entry='<li><a class="pu-s082" href="'+route(l,"shortlist")+'">'+html.escape(COPY[l][0])+'</a></li>'
 new=once(s,hit[0],hit[0]+entry)
 need(once(new,entry,"")==s,"guide preservation")
 return new.encode()
def add_tool(raw,l,kind):
 s=raw.decode();other="en" if l=="ru" else "ru";short,calc,guide,label,note,lang=COPY[l]
 linkkind="shortlist" if kind=="budget-calculator" else "budget-calculator"
 linktext=short if kind=="budget-calculator" else calc
 links=[(route(l,linkkind),linktext,""),(route(l,"journey"),guide,""),(route(other,kind),lang,other)]
 items="".join('<li><a href="'+url+'"'+(' lang="'+lng+'"' if lng else '')+'>'+html.escape(text)+'</a></li>' for url,text,lng in links)
 nav='<nav class="tool-nav" aria-label="'+html.escape(label,quote=True)+'"><p>'+html.escape(note)+'</p><ul role="list">'+items+'</ul></nav>'
 styles=re.findall(r'<style>(.*?)</style>',s,re.S);need(len(styles)==1,"single inline style")
 style=styles[0];newstyle=style+NAV_CSS
 need(s.count("sha256-"+csp(style))==1,"old CSP style hash")
 new=once(s,"<style>"+style+"</style>","<style>"+newstyle+"</style>")
 new=once(new,"sha256-"+csp(style),"sha256-"+csp(newstyle))
 new=once(new,"</main>",nav+"</main>")
 restored=once(new,nav,"");restored=once(restored,"sha256-"+csp(newstyle),"sha256-"+csp(style));restored=once(restored,"<style>"+newstyle+"</style>","<style>"+style+"</style>")
 need(restored==s,"tool preservation")
 need(re.findall(r'<script\b[^>]*>.*?</script>',new,re.S)==re.findall(r'<script\b[^>]*>.*?</script>',s,re.S),"unchanged scripts")
 return new.encode()
def build(manifest,r2,shortlist):
 need(sha(manifest)==MANIFEST,"parent manifest")
 out={};report=[]
 for l,(parent,p0,p1,p2,p3) in PINS.items():
  gp=route(l,"journey").lstrip("/");cp=route(l,"budget-calculator").lstrip("/");sp=route(l,"shortlist").lstrip("/")
  out[parent]=checked(r2/parent,p0)
  out[gp]=add_guide(checked(r2/gp,p1),l)
  out[cp]=add_tool(checked(r2/cp,p2),l,"budget-calculator")
  out[sp]=add_tool(checked(shortlist/l/"rental-shortlist.html",p3),l,"shortlist")
  for path in (gp,cp,sp):
   s=out[path].decode();tags=Tags(s).tags
   ids=[a["id"] for t,a in tags if "id" in a];need(len(ids)==len(set(ids)),"unique IDs "+path)
   need(not any(t=="form" for t,a in tags),"no submit "+path)
   need(any(a.get("name")=="robots" and "noindex" in a.get("content","") for t,a in tags),"noindex")
   for t,a in tags:
    if t=="a":
     dest=a.get("href","");need(dest.startswith(("#","/")) and not dest.startswith("//") and "?" not in dest,"local path only")
     if dest.startswith("#"):need(ids.count(dest[1:])==1,"anchor target")
   need(len(out[path])<=38912,"historical per-file cap")
  report.append({"locale":l,"parent_unchanged":True,"files":{n:{"bytes":len(out[n]),"sha256":sha(out[n])} for n in (parent,gp,cp,sp)}})
 return out,{"base":BASE,"r2":R2,"shortlist":SHORTLIST,"scope":"TOOLKIT_DRAFT_ONLY","pages":report,"release_approval":False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",required=True,type=Path);p.add_argument("--r2",required=True,type=Path);p.add_argument("--shortlist",required=True,type=Path);p.add_argument("--output",required=True,type=Path);a=p.parse_args()
 repo=a.repo.resolve();out=a.output.resolve();git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v])
 need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE,"baseline")
 need(out!=repo and repo not in out.parents and not out.exists(),"new external directory")
 files,report=build(git("show",BASE+":deploy/live/_release.json"),a.r2,a.shortlist)
 out.mkdir(parents=True,exist_ok=False)
 for name,b in files.items():
  f=out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b)
 (out/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
