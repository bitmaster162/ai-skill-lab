"""Local-only U3/E3.8-disabled preview from immutable R6. No external actions."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "deploy/live"
PREVIEW = ROOT / "deploy/preview"
PARENT_SHA = "5d07745a1220b1da82e224409210635ae83511f6184101671ea24987468b5966"
PARENT = "PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014"
RELEASE = "PHUKET_UNIVERSE_U3_E38_DORMANT_PREVIEW_R7_20261015"
FRIENDS = ("phuketravel.vercel.app", "stasph.vercel.app", "muaithaiph.vercel.app",
           "haven-ruddy.vercel.app", "rostikson-portfolio.vercel.app")
ICON = ('<svg viewBox="0 0 34 34" width="20" height="20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8">'
        '<ellipse cx="17" cy="17" rx="15" ry="9" transform="rotate(-16 17 17)"></ellipse>'
        '<circle cx="17" cy="17" r="5"></circle>'
        '<circle cx="30" cy="12.5" r="2.8" fill="currentColor" stroke="none"></circle></svg> ')
SCRIPT = '<script src="/phuket-universe-events.js" defer></script>'
def need(ok, why):
    if not ok: raise ValueError(why)
def sha(b): return hashlib.sha256(b).hexdigest()

def parent_payload():
    raw = (LIVE / "_release.json").read_bytes()
    need(sha(raw) == PARENT_SHA, "parent manifest pin drift")
    m = json.loads(raw)
    need(m.get("release_id") == PARENT and m.get("file_count") == 106, "R6 identity drift")
    files = {p.relative_to(LIVE).as_posix():p.read_bytes() for p in LIVE.rglob("*") if p.is_file()}
    need(len(files) == 107 and not any(p.is_symlink() for p in LIVE.rglob("*")), "R6 file scope")
    records = m["files"]
    need(len(records)==106 and len({x["path"] for x in records})==106
         and set(files)=={x["path"] for x in records}|{"_release.json"}, "R6 manifest file list")
    for x in records:
        b=files[x["path"]]
        need(len(b)==x["size"] and sha(b)==x["sha256"], "R6 file digest drift: "+x["path"])
    return files

def orbit_link(locale):
    href = "/en/phuket-universe" if locale=="en" else "/phuket-universe"
    label = "Phuket Universe" if locale=="en" else "Вселенная Пхукета"
    return (f'<a class="workshopButton" href="{href}" data-universe-event="universe_click" '
            f'aria-label="{label}">{ICON}Phuket Universe</a>')

def teaser(locale):
    en=locale=="en"
    title="Explore Phuket Universe" if en else "Откройте Вселенную Пхукета"
    desc=("Projects from people we know in Phuket, plus a property catalogue awaiting partner listings. Browse the island map and go directly to project websites."
          if en else "Проекты знакомых людей на Пхукете и каталог жилья, который ждёт объекты от агентств. Исследуйте карту острова и переходите напрямую на сайты проектов.")
    label="Open Phuket Universe →" if en else "Перейти во Вселенную Пхукета →"
    href="/en/phuket-universe" if en else "/phuket-universe"
    return (f'<section class="section" data-u3-universe-teaser="true" aria-labelledby="phuket-universe-teaser-title">'
            f'<div class="shell"><article class="programCard"><span class="cardMeta">PHUKET UNIVERSE</span>'
            f'<h2 id="phuket-universe-teaser-title">{title}</h2><p>{desc}</p>'
            f'<a class="button buttonPrimary" href="{href}">{label}</a></article></div></section>')

def mark_listing_links(page):
    # Future approved source cards only; never adds inventory to an empty catalog.
    def one(match):
        card=match.group()
        needle=re.compile(r'<a href="(https://[^"]+)" rel="noopener">')
        need(len(needle.findall(card))==1 and "data-universe-event" not in card,
             "listing source/marker mismatch")
        return needle.sub(r'<a data-universe-event="listing_click" href="\1" rel="noopener">', card, count=1)
    return re.sub(r'<article class="u2-card"[\s\S]*?</article>', one, page)

def make_page(name,page):
    loc="en" if name.startswith("en/") or name=="en.html" else "ru"
    href="/en/phuket-universe" if loc=="en" else "/phuket-universe"
    need("phuket-universe-events.js" not in page and "data-u3-universe-teaser" not in page,
         "duplicate U3 injection")
    if name in ("phuket-universe.html", "en/phuket-universe.html"):
        needle='<a class="pu-s112" href="#top">'
        need(page.count(needle)==1 and page.count('<footer class="pu-s039">')==1, "U3 Universe footer")
        page=page.replace(needle,
            f'<a class="pu-s112" data-universe-event="universe_click" href="{href}">',1)
        start,end=page.index('id="orbit"'),page.index('id="homes"')
        need(start<end,"orbit boundary")
        orbit=page[start:end]
        for host in FRIENDS:
            orig=f'class="pu-s053" rel="noopener" href="https://{host}"'
            need(orbit.count(orig)==1,"project card missing: "+host)
            orbit=orbit.replace(orig,
                f'class="pu-s053" data-universe-event="project_click" rel="noopener" href="https://{host}"',1)
        page=page[:start]+orbit+page[end:]
    else:
        need(page.count('<footer class="workshopFooter">')==1,"Workshop footer: "+name)
        start=page.index('<nav class="workshopFooterExplore"')
        end=page.index("</nav>",start)
        nav=page[start:end]
        need(('href="/en/phuket"' if loc=="en" else 'href="/phuket"') in nav, "Phuket link")
        page=page[:end]+orbit_link(loc)+page[end:]
        if name in ("phuket.html","en/phuket.html"):
            need(page.count("</main>")==1,"Phuket main boundary")
            page=page.replace("</main>",teaser(loc)+"</main>",1)
    page=mark_listing_links(page)
    need(page.count("</body>")==1,"one body close")
    page=page.replace("</body>",SCRIPT+"</body>",1)
    need(page.count('data-universe-event="universe_click"')==1,"footer event count")
    return page

def render():
    originals=parent_payload()
    files=dict(originals)
    pages=sorted(k for k in files if k.endswith(".html") and k!="404.html")
    need(len(pages)==56,"expected 56 canonical HTML")
    for k in pages:files[k]=make_page(k,files[k].decode("utf-8")).encode("utf-8")
    asset=(ROOT/"public/phuket-universe-events.js").read_bytes()
    need(b"const ENABLED = false" in asset and b'credentials: "omit"' in asset
         and "phuket-universe-events.js" not in files, "unapproved event authority")
    files["phuket-universe-events.js"]=asset
    need(all(originals[k]==files[k] for k in originals if k not in pages),"R6 collateral mutation")
    rows=[{"path":k,"size":len(v),"sha256":sha(v)} for k,v in sorted(files.items()) if k!="_release.json"]
    need(len(rows)==107,"R7 inventory")
    payload=sha("".join(f"{x['path']}\t{x['size']}\t{x['sha256']}\n" for x in rows).encode())
    m={"schema":"ai-skill-lab.static-release.v1","release_id":RELEASE,
       "file_count":len(rows),"payload_sha256":payload,"files":rows}
    files["_release.json"]=(json.dumps(m,indent=2,sort_keys=True)+"\n").encode()
    return files,{"status":"LOCAL_PREVIEW_NOT_RELEASE_INTEGRATED","release_id":RELEASE,
        "file_count":len(rows),"public_routes":len(pages),"manifest_sha256":sha(files["_release.json"]),
        "payload_sha256":payload,"real_listings":0,"events_enabled":False,
        "authority":{"push":False,"pr":False,"merge":False,"deploy":False,
                     "production":False,"d1_migration":False,"event_receiver":False}}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    out=args.out
    need(out.resolve().is_relative_to(PREVIEW.resolve()) and out.resolve()!=PREVIEW.resolve()
         and not out.exists() and not any(p.is_symlink() for p in [out,*out.parents]),
         "Create-only preview path required")
    files,info=render()
    out.mkdir(parents=True,exist_ok=False)
    for name,data in sorted(files.items(),key=lambda x:x[0]=="_release.json"):
        p=out/name;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("xb") as f:f.write(data)
    need(files=={p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob("*") if p.is_file()},
         "STOP preview write verification")
    print(json.dumps(info,ensure_ascii=False,sort_keys=True),flush=True)
if __name__=="__main__":main()
