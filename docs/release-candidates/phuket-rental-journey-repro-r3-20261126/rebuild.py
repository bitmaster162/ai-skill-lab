"""Rebuild the exact split R2 rental journey from pinned Git objects.
Python 3.10+, Node.js. Either local Git objects (--repo) or explicit public
immutable GitHub downloads (--fetch). No previous preview files required.
Run: python rebuild.py --fetch --output <new external folder>
This is a draft review bundle, not a production release.
"""
import argparse,hashlib,json,subprocess,urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit

BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
ROOT="https://raw.githubusercontent.com/bitmaster162/ai-skill-lab/"
PREFIX="docs/release-candidates/"
# role: commit, repo-relative path, exact Git blob
SOURCES={
"plan":("721ffc0800566c5882e68118d4a6f8b78d848fcd","phuket-rental-search-plan-r1-20261125/build_candidate.py","2ede2647a60aac4fc663f2b6bba944e5afb47c86"),
"cost":("62ffc9f7c4143415977b474cc0f5b38415313149","phuket-rental-cost-compare-r1-20261125/build_candidate.mjs","3ef5d1b527f97970fcf450ff52c8ea50cb284453"),
"viewing":("203d21b31516e00a9aa8119cbca057ffdc4002fa","phuket-viewing-checklist-r1-20261125/build_candidate.py","7fb0e6853c265b6ca08bc9e6135ab60060d35996"),
"areas":("89c3ac1acd651d6cfc9596c6b206fb20153825ec","phuket-area-compare-r1-20261125/build_candidate.py","e4a8043eb2bfd75ca353c87a50aa749757099308"),
"calculator":("fb3744a568390a5c3549a793e3ac22b290aa26ab","phuket-rental-budget-calculator-r1-20261125/build_candidate.py","9a89f43b152ab1f02829afcb5530b348f0c04356"),
"compose":("23c15862d3140266b6c0e307593068f2de141b9f","phuket-rental-journey-r1-20261125/compose.py","99f1c6c61a3cb5e52182558a53e8946a68b10450"),
"split":("7f6c489b57ac6d529e1e129d3b8d04364a8f5243","phuket-rental-journey-split-r2-20261125/split.py","a44415724070306f5a22770934c41d5121e346db")}
PARENT={
"_release.json":"66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5",
"phuket-universe.html":"2b7c61e013d25815d27b98bb64db9357a64c36a7ec2e6c53a5dfc0ccf357de3a",
"en/phuket-universe.html":"74f02c92d9595673c289b6dc714a32c8fa099f565fa7272194967fd6befdb9ba",
"phuket-universe.css":"c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"}
EXPECTED={
"phuket-universe.html":"a231e27e1687ad4229b2ebf863d6b00a50cfa0e17f7b7e8b7f9657e16798c325",
"en/phuket-universe.html":"abbea4cc42de6bf639a4e1bed51556aee4428a5538f8d7f8f3199a5280ec7b9b",
"preview-tools/ru/rental-journey.html":"d027f0bfff40fbb52f74c0b4c2a289a9044479610ee4a8a5976431285a0ad4d0",
"preview-tools/en/rental-journey.html":"27933ed6c17232051d2d2043dede24f572063dabf9cc219bc80af049908efbea",
"preview-tools/ru/rental-budget-calculator.html":"3615d7e9daf0ff1a15b80d320ecb4dc4b66c4f31f0eefc576cd1510f5de9223b",
"preview-tools/en/rental-budget-calculator.html":"2a37c9bf6010d3fea8c8e8201c1ecc982c14af24f233f45d7f7dfadc352670e6"}
ASSET_PINS={
"phuket-universe.css":"c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287",
"phuket-housing-u2.css":"8696c711fa7bc961a6ac5e949c80e242d76601668f2af96dfd4b0020679577d0",
"fonts/Unbounded-ru-en.woff2":"1600f2b8c27dc942601fdd2fc3f894f0375e371287d740289bf58945ab1991b1",
"fonts/Manrope-latin.woff2":"a30ddcd349703aff7464c34bef3fffdff405ee50c113440d7c8693c02d210972",
"fonts/Manrope-cyrillic.woff2":"c268b459a9329e59fecf39a17618efd44c71735532048d60b12aab76a8c14914"}
ASSETS=tuple(ASSET_PINS)
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def write(root,files):
 for name,b in files.items():
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open("xb") as f:f.write(b)
def reader(repo):
 if repo:
  repo=repo.resolve()
  git=lambda *v:subprocess.check_output(["git","-C",str(repo),*v],timeout=20)
  for ref in [BASE]+[x[0] for x in SOURCES.values()]:
   need(git("rev-parse",ref+"^{commit}").decode().strip()==ref,"missing exact commit "+ref)
  return lambda ref,path:git("show",ref+":"+path)
 def get(ref,path):
  req=urllib.request.Request(ROOT+ref+"/"+path,headers={"User-Agent":"PhuketUniverse-Pinned-Preview"})
  with urllib.request.urlopen(req,timeout=15) as f:b=f.read(200001)
  need(len(b)<=200000,"input bound")
  return b
 return get
def load_py(b,role):
 # Only the exact previously authored and verified Git blob is executed.
 ns={"__name__":"pinned_candidate_"+role};exec(compile(b,role+".py","exec"),ns);return ns
def rebuild(get,out):
 parent={n:get(BASE,"deploy/live/"+n) for n in PARENT}
 for n,b in parent.items():need(sha(b)==PARENT[n],"parent pin "+n)
 manifest=json.loads(parent["_release.json"]);pins={r["path"]:r for r in manifest["files"]}
 assets={n:(parent[n] if n in parent else get(BASE,"deploy/live/"+n)) for n in ASSETS}
 for n,b in assets.items():need(len(b)==pins[n]["size"] and sha(b)==pins[n]["sha256"]==ASSET_PINS[n],"asset pin "+n)
 source={role:get(ref,PREFIX+path) for role,(ref,path,pin) in SOURCES.items()}
 for role,b in source.items():need(blob(b)==SOURCES[role][2],"source blob "+role)
 out.mkdir(parents=True,exist_ok=False)
 write(out/"sources",{role+(".mjs" if role=="cost" else ".py"):b for role,b in source.items()})
 read=lambda n:parent[n]
 dirs={}
 def stage(role,files):
  p=out/"stages"/role;write(p,files);dirs[role]=p
 stage("plan",load_py(source["plan"],"plan")["validate_and_build"](lambda n:read(n.removeprefix("deploy/live/")))[0])
 for role in ("viewing","areas"):stage(role,load_py(source[role],role)["build"](read)[0])
 stage("calculator",load_py(source["calculator"],"calculator")["build"](manifest))
 js=source["cost"].decode();marker="const args=process.argv.slice(2);"
 need(js.count(marker)==1,"cost CLI boundary")
 # Execute its exact pure renderer, not the command-line entrypoint.
 wrapper=js.split(marker,1)[0]+"""
const data=JSON.parse(await new Promise(resolve=>{let s="";process.stdin.setEncoding("utf8");process.stdin.on("data",c=>s+=c);process.stdin.on("end",()=>resolve(s));}));
for(const l of ['ru','en']) need(createHash('sha256').update(data[l]).digest('hex')===PINS[l][1],'page pin');
need(createHash('sha256').update(data.css).digest('hex')==='c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287','CSS pin');
console.log(JSON.stringify(Object.fromEntries(['ru','en'].map(l=>[l,validate(l,data[l],data.css)]))));
"""
 # Triple quotes inside Python source preserved; wrapper is bounded and pinned upstream.
 w=out/"sources"/"cost_adapter.mjs";write(w.parent,{w.name:wrapper.encode()})
 data={"ru":read("phuket-universe.html").decode(),"en":read("en/phuket-universe.html").decode(),"css":read("phuket-universe.css").decode()}
 cost=json.loads(subprocess.check_output(["node",str(w)],input=json.dumps(data,ensure_ascii=False).encode(),timeout=20))
 stage("cost",{"phuket-universe.html":cost["ru"].encode(),"en/phuket-universe.html":cost["en"].encode()})
 stage("r1",load_py(source["compose"],"compose")["compose"](read,dirs)[0])
 final,report=load_py(source["split"],"split")["build"](read,dirs["r1"])
 need(set(final)==set(EXPECTED),"exact six outputs")
 for n,b in final.items():need(sha(b)==EXPECTED[n],"R2 output pin "+n)
 write(out/"preview",{**final,**assets})
 result={"scope":"EXACT_R2_REBUILD_DRAFT_ONLY","base":BASE,"sources":{k:{"commit":SOURCES[k][0],"blob":blob(b),"sha256":sha(b)} for k,b in source.items()},"html":{n:{"sha256":sha(b),"bytes":len(b)} for n,b in final.items()},"assets":{n:sha(b) for n,b in assets.items()},"exact_match":"6/6","release_approval":False}
 write(out,{"REBUILD.json":(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()})
 return result
def serve(folder,port):
 root=folder.resolve();m=json.loads((root/"REBUILD.json").read_bytes())
 need(m["base"]==BASE and m["exact_match"]=="6/6","bundle identity")
 need(set(m["html"])==set(EXPECTED) and set(m["assets"])==set(ASSETS),"bundle inventory")
 allowed={}
 for n,pin in EXPECTED.items():
  b=(root/"preview"/n).read_bytes();need(sha(b)==pin,"preview pin "+n);allowed["/"+n]=(b,"text/html; charset=utf-8")
 for n in ASSETS:
  b=(root/"preview"/n).read_bytes();need(sha(b)==m["assets"][n]==ASSET_PINS[n],"asset pin "+n)
  allowed["/"+n]=(b,"font/woff2" if n.endswith(".woff2") else "text/css")
 allowed["/phuket-universe"]=allowed["/phuket-universe.html"]
 allowed["/en/phuket-universe"]=allowed["/en/phuket-universe.html"]
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   if self.headers.get("Host")!=f"127.0.0.1:{self.server.server_port}":self.send_error(403);return
   p=urlsplit(self.path).path
   if p not in allowed:self.send_error(404);return
   b,t=allowed[p];self.send_response(200);self.send_header("Content-Type",t);self.send_header("Content-Length",str(len(b)));self.send_header("X-Robots-Tag","noindex,nofollow");self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff")
   if t.startswith("text/html"):
    policy="frame-ancestors 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
    if not p.endswith("/rental-budget-calculator.html"):policy+="; default-src 'none'; script-src 'none'; style-src 'self'; font-src 'self'; img-src 'self' data:"
    self.send_header("Content-Security-Policy",policy)
   self.end_headers();self.wfile.write(b)
 with ThreadingHTTPServer(("127.0.0.1",port),Handler) as server:
  print(f"Review only: http://127.0.0.1:{server.server_port}/phuket-universe",flush=True)
  server.serve_forever()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--repo",type=Path);p.add_argument("--fetch",action="store_true");p.add_argument("--output",type=Path);p.add_argument("--serve",type=Path);p.add_argument("--port",type=int,default=8765);a=p.parse_args()
 if a.serve:
  need(not a.repo and not a.fetch and not a.output,"serve mode only");serve(a.serve,a.port);return
 need(bool(a.repo)!=a.fetch and a.output is not None,"choose --repo or --fetch and --output")
 out=a.output.resolve();need(not out.exists(),"new output required")
 if a.repo:need(out!=a.repo.resolve() and a.repo.resolve() not in out.parents,"external output")
 result=rebuild(reader(a.repo),out);print(json.dumps(result,indent=2))
if __name__=="__main__":main()
