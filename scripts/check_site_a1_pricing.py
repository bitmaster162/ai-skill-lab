#!/usr/bin/env python3
"""SITE-A1 read-only 2-locale pricing, structured offers, manifests, scope and copy parity."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import hashlib,html,json,re,subprocess,sys
from site_a1_pricing_contract import catalog,snapshot,facts
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
BASE="d0a858a7787088dabf6d914e45fb0cde41b743e8"
PARENT="fc57c61c7ac502644665f7cc06152f43fb0b5d7f67827eb6fd4b12aadfc83f37"
PATCH="SITE_A1_PRICING_COPY_20261026_LOCAL_R1"
errors=[];checks=0
def assertq(ok,why):
    global checks
    checks+=1
    if not ok:errors.append(why)
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):
    r=subprocess.run(["git","--no-optional-locks","-C",str(ROOT),*args],capture_output=True,timeout=35)
    if r.returncode:raise RuntimeError("git failed:"+repr(args))
    return r.stdout
class CatalogParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ld=False;self.buf=[];self.blocks=[]
    def handle_starttag(self,t,attrs):
        if t=="script" and dict(attrs).get("type")=="application/ld+json":
            self.ld=True;self.buf=[]
    def handle_data(self,data):
        if self.ld:self.buf.append(data)
    def handle_endtag(self,t):
        if self.ld and t=="script":
            self.blocks.append("".join(self.buf));self.ld=False;self.buf=[]
assertq(git("rev-parse","HEAD").decode().strip()==BASE,"BASE_HEAD")
manifest_path=LIVE/"_release.json"
m=json.loads(manifest_path.read_bytes())
assertq(m.get("patch_id")==PATCH,"PATCH_ID")
assertq(m.get("parent_manifest_sha256")==PARENT,"PARENT_MANIFEST")
assertq(m.get("file_count")==108,"FILE_COUNT")
for route,lang in (("pricing.html","ru"),("en/pricing.html","en")):
    path=LIVE/route
    b=path.read_bytes()
    old=git("show",BASE+":deploy/live/"+route)
    strong=lambda x:re.findall(r"<strong(?:\s[^>]*)?>(.*?)</strong>",x.decode("utf-8"),re.S)
    assertq(strong(b)==strong(old),route+":ALL_VISIBLE_STRONG_AMOUNTS_UNCHANGED")
    p=CatalogParser();p.feed(b.decode("utf-8"))
    blocks=[json.loads(x) for x in p.blocks]
    found=[o for o in blocks if isinstance(o,dict) and o.get("@type")=="OfferCatalog"]
    assertq(found==[catalog(lang)],route+":JSONLD_CATALOG_PARITY")
    assertq(len(found)==1 and len(found[0]["itemListElement"])==18,route+":18_OFFERS")
    assertq(b.count(b"application/ld+json")>=3,route+":LD_BLOCKS")
    if lang=="ru":
        text=b.decode("utf-8")
        for wrong,right in (
            ("Внедрение пилотааа","Внедрение пилота"),
            ("Работа support","Операционная поддержка"),
            ("Работа partner","Операционный партнёр"),
            ("Office часы","Часы консультаций")):
            assertq(wrong not in text and text.count(right)>=1,"RU_LABEL:"+right)
        # Scope prevents accidental deletion of all price numbers.
        assertq(text.count("от $4,900")==1,"PILOT_START_AMOUNT")
        assertq(text.count("$178/мес")==1,"OFFICE_MONTH_PRICE")
    else:
        assertq("Operating support" in b.decode("utf-8"),"EN_COPY_UNCHANGED")
text=(LIVE/"llms.txt").read_text("utf-8")
assertq(text.count(snapshot())==1,"LLMS_PRICING_FACTS")
assertq(len(text.encode("utf-8"))<=4096,"LLMS_SIZE")
assertq("RU: https://aiskillab.work/pricing | EN: https://aiskillab.work/en/pricing" in text,"LLMS_BILINGUAL_URLS")
xml=(LIVE/"sitemap.xml").read_text("utf-8")
for route in ("/pricing","/en/pricing"):
    assertq(("<loc>https://aiskillab.work"+route+"</loc><lastmod>2026-10-26</lastmod>") in xml,
            route+":LASTMOD_26")
assertq(xml.count("<lastmod>2026-10-26</lastmod>")==2,"SITEMAP_ONLY_TWO_26")
assertq(xml.count("<lastmod>2026-10-15</lastmod>")==2,"UNIVERSE_LASTMOD_UNCHANGED")
assertq(xml.count("<lastmod>2026-10-16</lastmod>")==52,"OTHER_LASTMOD_UNCHANGED")
assertq("route === \"/pricing\" || route === \"/en/pricing\"" in
        (ROOT/"app/sitemap.ts").read_text("utf-8"),"SOURCE_SITEMAP_DATE")
rows={}
for p in LIVE.rglob("*"):
    if p.is_file() and p.name!="_release.json":
        b=p.read_bytes();rel=p.relative_to(LIVE).as_posix()
        rows[rel]={"size":len(b),"sha256":sha(b)}
listed={x["path"]:{"size":x["size"],"sha256":x["sha256"]} for x in m["files"]}
assertq(rows==listed,"MANIFEST_BYTE_PARITY")
payload=sha("".join(rel+"\t"+str(rows[rel]["size"])+"\t"+rows[rel]["sha256"]+"\n"
                    for rel in sorted(rows)).encode())
assertq(payload==m["payload_sha256"],"MANIFEST_PAYLOAD")
old_m=json.loads(git("show",BASE+":deploy/live/_release.json"))
oldrows={x["path"]:x for x in old_m["files"]}
changed={x for x in rows if rows[x]!={"size":oldrows[x]["size"],"sha256":oldrows[x]["sha256"]}}
assertq(changed=={"pricing.html","en/pricing.html","llms.txt","sitemap.xml","vercel.json"},"STATIC_DELTA")
assertq(facts()["currency"]=="USD","FACTS_USD")
print("SITE_A1_PRICING_CHECKS "+str(checks)+" RU/EN offers=18 each; live manifest files=108; changed="+",".join(sorted(changed)))
if errors:
    print("SITE_A1_PRICING_FAIL "+json.dumps(errors,ensure_ascii=False))
    sys.exit(1)
print("SITE_A1_PRICING_PASS")
