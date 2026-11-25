"""R10 reproducible review bundle for exact Phuket Universe R9.
Python 3.10+ and Node.js; no prior local previews needed.
Build: python review_bundle.py --fetch --output <new folder>
Review: python review_bundle.py --serve <bundle> --port 8765
Explicit immutable public source fetch; review server binds only to loopback.
No live release, submission, analytics, or publication.
"""
import argparse,hashlib,html,json,urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a"
R9="04ee35dd37a1c8ac76127beb781bf77c3855f490"
ROOT="https://raw.githubusercontent.com/bitmaster162/ai-skill-lab/"
PREFIX="docs/release-candidates/"
SOURCES={
"runner":("9cc91a1e0d1f7298c2504527cbe3a3da2fe18a6f","phuket-rental-journey-repro-r3-20261126/rebuild.py","bf2689c92172e063b8d5e4244f99474f5a9f703d"),
"shortlist":("3b1ea1be33d90da07880fb0167a31dfe86a25aa9","phuket-rental-shortlist-r1-20261126/build_candidate.py","7179f0ae0228590504b8689159e2960c9bbca80f"),
"connect":("8dc243e1f0764ac3c833ece07b690fa57d0e9b6d","phuket-rental-toolkit-r5-20261126/connect.py","e2fd74893aba8e97c6bad5cac93de55653d40098"),
"note":("149c0f175a944acf2504fbb03d1b7a3a482a823c","phuket-rental-note-r6-20261126/build_note.py","18c5f2ad703a0288651800fcade492f6b1ead25c"),
"move_in":("a3ccda9cb448ba2756cb46d16c812c4e8c22cf80","phuket-move-in-r7-20261126/build_move_in.py","ed7154e38c645fb77c625f088534570411db54c0"),
"move_out":("10676f62d13b37c8e8603ff41b1ebb3856828f67","phuket-move-out-r8-20261126/build_move_out.py","9f0ac405c1e54023a3c1a1907ab28d2ff98f421b"),
"stages":(R9,"phuket-journey-stages-r9-20261126/build_stages.py","81caad5f553abd32b561571168bee81cdbdca391")}
EXPECTED={
"phuket-universe.html":"a231e27e1687ad4229b2ebf863d6b00a50cfa0e17f7b7e8b7f9657e16798c325",
"en/phuket-universe.html":"abbea4cc42de6bf639a4e1bed51556aee4428a5538f8d7f8f3199a5280ec7b9b",
"preview-tools/ru/rental-journey.html":"6d89e84dce820a1591b4ad9d3d1342baf89c7a5afaa40adc179e89ca86487daf",
"preview-tools/en/rental-journey.html":"60a5f812148e98063e37e7366bc7b922d758e082a728aa9f2d2db84d83699d5b",
"preview-tools/ru/rental-budget-calculator.html":"0b3c1d338e221fe774903ec5f2ba54d208df23bad19fd3f368b2b7a8a64d8be7",
"preview-tools/en/rental-budget-calculator.html":"73642f56ec0c7c24f99a1a3999a8f15b466c8fea5291fab36931b2c485efe304",
"preview-tools/ru/rental-shortlist.html":"014841064db6f010780fce536221704700c40c62d049abe8659a05cde0c2418d",
"preview-tools/en/rental-shortlist.html":"91ac7f29e59ecd43a9defc8515dfb3ad07ad8bbd5df90cd79544181bee6b4834",
"preview-tools/ru/rental-move-in.html":"ddee53772565a7fce82b098eaadd309338ec22dc2c39d94a4a1c38c3f8f74ac7",
"preview-tools/en/rental-move-in.html":"f00b8f807bd1cfbe0bb823f09e29cb447b2810def906083a8c8480b07da553f8",
"preview-tools/ru/rental-move-out.html":"52eae55df3b93785ad98fcad81be8b56da2bf402f4c6de9ef5371b566df98c20",
"preview-tools/en/rental-move-out.html":"8d79f72033a2733e41eb809176fbe483dc6f8fab102eda563054a177efe3f05a"}
ASSETS={
"phuket-universe.css":"c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287",
"phuket-housing-u2.css":"8696c711fa7bc961a6ac5e949c80e242d76601668f2af96dfd4b0020679577d0",
"fonts/Unbounded-ru-en.woff2":"1600f2b8c27dc942601fdd2fc3f894f0375e371287d740289bf58945ab1991b1",
"fonts/Manrope-latin.woff2":"a30ddcd349703aff7464c34bef3fffdff405ee50c113440d7c8693c02d210972",
"fonts/Manrope-cyrillic.woff2":"c268b459a9329e59fecf39a17618efd44c71735532048d60b12aab76a8c14914"}
MANIFEST="66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def write(root,files):
 for name,b in files.items():
  p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open("xb") as f:f.write(b)
def get(ref,path):
 need(len(ref)==40 and all(c in "0123456789abcdef" for c in ref),"exact commit only")
 req=urllib.request.Request(ROOT+ref+"/"+path,headers={"User-Agent":"PhuketUniverse-R10-Pinned-Review"})
 with urllib.request.urlopen(req,timeout=15) as f:b=f.read(200001)
 need(len(b)<=200000,"input bound");return b
def source(role):
 ref,path,pin=SOURCES[role];b=get(ref,PREFIX+path);need(blob(b)==pin,"Git source pin "+role);return role,b
def load(b,role):
 ns={"__name__":"pinned_review_"+role};exec(compile(b,role+".py","exec"),ns);return ns
def index():
 # Reviewer-only entry; not a production route or additional live page.
 labels=[("rental-journey","Маршрут арендатора","Rental journey"),("rental-budget-calculator","Калькулятор аренды","Rental calculator"),("rental-shortlist","Личная подборка и заметка","Shortlist and note"),("rental-move-in","Заселение","Move-in"),("rental-move-out","Выезд и депозит","Move-out and deposit")]
 rows=['<tr><th scope="row">Phuket Universe</th><td><a lang="ru" href="/phuket-universe">Открыть</a></td><td><a lang="en" href="/en/phuket-universe">Open</a></td></tr>']
 for key,ru,en in labels:rows.append(f'<tr><th scope="row">{html.escape(ru)} / <span lang="en">{html.escape(en)}</span></th><td><a lang="ru" href="/preview-tools/ru/{key}.html">Открыть</a></td><td><a lang="en" href="/preview-tools/en/{key}.html">Open</a></td></tr>')
 style="*{box-sizing:border-box}body{margin:0;padding:24px;font:1rem/1.6 system-ui,sans-serif;background:#0d1320;color:#eef4fc}main{max-width:860px;margin:auto}a{color:#8ef5df}a:focus-visible{outline:3px solid #39e1c6}table{border-collapse:collapse;width:100%;table-layout:fixed}td,th{text-align:left;padding:10px 6px;border-bottom:1px solid #61728a;overflow-wrap:anywhere}th:first-child{width:58%}small{color:#b8c8da}"
 return ('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Phuket Universe — R9 preview</title><style>'+style+'</style></head><body><main><h1>Phuket Universe — R9</h1><p>Локальный предпросмотр, не действующий сайт. / <span lang="en">Local review preview, not a live site.</span></p><table><thead><tr><th scope="col">Раздел / Tool</th><th scope="col">RU</th><th scope="col">EN</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table><p><small>Каталог пуст. Серверные функции не подключены. / <span lang="en">Empty catalogue. Server features are disabled.</span></small></p></main></body></html>\n').encode()
def rebuild(out):
 need(not out.exists(),"new output required")
 with ThreadPoolExecutor(max_workers=4) as ex:src=dict(ex.map(source,SOURCES))
 runner=load(src["runner"],"runner")
 # The pinned R3 runner independently validates all seven earlier source blobs.
 cache={}
 def cached(ref,path):
  k=(ref,path)
  if k not in cache:cache[k]=get(ref,path)
  return cache[k]
 manifest=cached(BASE,"deploy/live/_release.json");css=cached(BASE,"deploy/live/phuket-universe.css")
 need(sha(manifest)==MANIFEST and sha(css)==ASSETS["phuket-universe.css"],"parent inputs")
 out.mkdir(parents=True,exist_ok=False);write(out/"sources",{k+".py":b for k,b in src.items()})
 prior=out/"r3"
 old=runner["rebuild"](cached,prior)
 need(old["exact_match"]=="6/6" and len(old["sources"])==7,"R3 rebuild")
 def stage(role,files):
  p=out/"stages"/role;write(p,files);return p
 short=stage("shortlist",load(src["shortlist"],"shortlist")["build"](manifest))
 r5=stage("r5",load(src["connect"],"connect")["build"](manifest,prior/"preview",short)[0])
 r6=stage("r6",load(src["note"],"note")["build"](manifest,r5)[0])
 r7=stage("r7",load(src["move_in"],"move_in")["build"](manifest,r6)[0])
 r8=stage("r8",load(src["move_out"],"move_out")["build"](manifest,r7)[0])
 final=load(src["stages"],"stages")["build"](manifest,css,r8)[0]
 need(set(final)==set(EXPECTED),"exact R9 output inventory")
 for n,b in final.items():need(sha(b)==EXPECTED[n],"R9 output pin "+n)
 assets={n:(prior/"preview"/n).read_bytes() for n in ASSETS}
 for n,b in assets.items():need(sha(b)==ASSETS[n],"asset pin "+n)
 write(out/"preview",{**final,**assets,"index.html":index()})
 result={"scope":"R9_REVIEW_ONLY","base":BASE,"r9":R9,"source_blobs":{k:{"commit":SOURCES[k][0],"blob":blob(b),"sha256":sha(b)} for k,b in src.items()},"earlier_sources":old["sources"],"html":{n:{"sha256":sha(b),"bytes":len(b)} for n,b in final.items()},"assets":ASSETS,"index_sha256":sha(index()),"exact_match":"12/12","release_approval":False}
 write(out,{"REVIEW.json":(json.dumps(result,indent=2,sort_keys=True)+"\n").encode()})
 return result
def verified(folder):
 p=folder.resolve();m=json.loads((p/"REVIEW.json").read_bytes())
 need(m["base"]==BASE and m["r9"]==R9 and m["exact_match"]=="12/12","bundle identity")
 need(set(m["html"])==set(EXPECTED) and m["assets"]==ASSETS,"bundle inventory")
 allowed={}
 for n,pin in {**EXPECTED,**ASSETS,"index.html":sha(index())}.items():
  b=(p/"preview"/n).read_bytes();need(sha(b)==pin,"serve pin "+n)
  if n in EXPECTED:need(m["html"][n]=={"sha256":pin,"bytes":len(b)},"report pin "+n)
  t="text/html; charset=utf-8" if n.endswith(".html") else "font/woff2" if n.endswith(".woff2") else "text/css"
  allowed["/"+n]=(b,t)
 allowed["/"]=allowed["/index.html"]
 allowed["/phuket-universe"]=allowed["/phuket-universe.html"]
 allowed["/en/phuket-universe"]=allowed["/en/phuket-universe.html"]
 return allowed
def serve(folder,port):
 allowed=verified(folder)
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   if self.headers.get("Host")!=f"127.0.0.1:{self.server.server_port}":self.send_error(403);return
   u=urlsplit(self.path);p=u.path
   if u.query or p not in allowed:self.send_error(404);return
   b,t=allowed[p];self.send_response(200);self.send_header("Content-Type",t);self.send_header("Content-Length",str(len(b)));self.send_header("X-Robots-Tag","noindex,nofollow");self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff")
   if t.startswith("text/html"):
    policy="frame-ancestors 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'"
    if p in {"/","/index.html"}:policy+="; default-src 'none'; style-src 'unsafe-inline'"
    elif "rental-journey.html" in p or "phuket-universe" in p:policy+="; default-src 'none'; script-src 'none'; style-src 'self'; font-src 'self'; img-src 'self' data:"
    # Interactive tools retain their exact hash-pinned CSP meta tags.
    self.send_header("Content-Security-Policy",policy)
   self.end_headers();self.wfile.write(b)
 with ThreadingHTTPServer(("127.0.0.1",port),Handler) as server:
  print(f"Review only: http://127.0.0.1:{server.server_port}/",flush=True)
  server.serve_forever()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--fetch",action="store_true");p.add_argument("--output",type=Path);p.add_argument("--serve",type=Path);p.add_argument("--port",type=int,default=8765);a=p.parse_args()
 if a.serve:
  need(not a.fetch and not a.output,"serve mode only");serve(a.serve,a.port);return
 need(a.fetch and a.output is not None,"explicit --fetch and new --output required")
 print(json.dumps(rebuild(a.output.resolve()),indent=2))
if __name__=="__main__":main()
