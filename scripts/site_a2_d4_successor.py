"""Exact SITE-A1/A2 R2 successor admission for inherited Workshop D4 only."""
from pathlib import Path
import hashlib
import json
import re

MANIFEST_SHA = "d03a2e227bae748dfb03d4d35bf2b619c500e8d73802ab60e58c1fa221914606"
ADMISSION_SHA = "4ff3e62bcacc46aa299e7225a32d765a537bd936e8b6aa3232e14994121283ea"
PATCH = "SITE_A1_A2_R2_20261026_DRAFT_REVIEW"
EXACT_PAYLOAD = 1371163
PINNED = {
    "README.md": "f92a12b93b041ac68a4768fa93f21fd58a27a1f7b904db2c2d97fdd4b4e5eff2",
    "app/sitemap.ts": "aaa42ef58032b7026496c251893bade8896240b92f37653cf915e5d3f5c79fb5",
    "components/ProjectStudio.tsx": "6f5acd278f268075aadf51e4bb79bc6ede67bb7d60e96895f36a353bfd22bc34",
    "components/workshop/WorkshopAudience.tsx": "be7f68db93db6b18bf007c6715a24fe30c7c67116e619f36780c98a8c07903f7",
    "deploy/live/personal.html": "288ed72d677b37a80510413e647f0bf87ae3365a9d29a354a657b373d009fc69",
    "deploy/live/_release.json": MANIFEST_SHA,
}
RU_CHANGED = frozenset(("/business", "/challenge", "/faq", "/phuket", "/privacy",
    "/projects", "/proof", "/start", "/studio", "/teens", "/terms"))
PRICING = frozenset(("/pricing", "/en/pricing"))
SITEMAP_EXPRESSION = ('lastModified: universeRoutes.includes(route) ? "2026-10-15" : '
    '(route === "/pricing" || route === "/en/pricing") ? "2026-10-26" : '
    'siteA2Routes.includes(route) ? "2026-10-26" : lastModified')

def sha(data):
    return hashlib.sha256(data).hexdigest()

def verify_identity(manifest, admission, actual):
    if sha(manifest) != MANIFEST_SHA or sha(admission) != ADMISSION_SHA:
        raise ValueError("SITE_A2_D4_DENY SHA")
    m, a = json.loads(manifest), json.loads(admission)
    if (m.get("patch_id") != PATCH or m.get("file_count") != 108
        or a.get("candidate_manifest_sha256") != MANIFEST_SHA
        or a.get("source_r2_manifest_sha256") !=
            "ad8282f6b7a670c9e5e5f840dd0d427f3c24f87a2210f64d40dab1cf7bf497e5"
        or actual != EXACT_PAYLOAD
        or sum(x["size"] for x in m["files"]) != EXACT_PAYLOAD):
        raise ValueError("SITE_A2_D4_DENY identity or payload")
    return True

def source_sha(root, path):
    raw = (root / path).read_bytes()
    if b"\r" in raw.replace(b"\r\n", b""):
        raise ValueError("SITE_A2_D4_DENY mixed EOL")
    return sha(raw.replace(b"\r\n", b"\n"))

def admit(root):
    import site_a1_a2_r2_successor as successor
    successor.verify()
    m = (root / "deploy/live/_release.json").read_bytes()
    a = (root / "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json").read_bytes()
    verify_identity(m, a, sum(x["size"] for x in json.loads(m)["files"]))
    for p, expected in PINNED.items():
        if source_sha(root, p) != expected:
            raise ValueError("SITE_A2_D4_DENY source pin: " + p)
    verify_sitemap(root)
    return dict(PINNED)

def verify_sitemap(root):
    source = (root / "app/sitemap.ts").read_text(encoding="utf-8")
    xml = (root / "deploy/live/sitemap.xml").read_text(encoding="utf-8")
    if source.count(SITEMAP_EXPRESSION) != 1:
        raise ValueError("SITE_A2_D4_DENY source lastmod expression")
    for route in RU_CHANGED | PRICING:
        if xml.count('<loc>https://aiskillab.work' + route +
            '</loc><lastmod>2026-10-26</lastmod>') != 1:
            raise ValueError("SITE_A2_D4_DENY changed route " + route)
    if (xml.count("<lastmod>2026-10-26</lastmod>") != 13
        or xml.count("<lastmod>2026-10-15</lastmod>") != 2
        or xml.count("<lastmod>2026-10-16</lastmod>") != 41):
        raise ValueError("SITE_A2_D4_DENY sitemap counts")
    return True

def semantic(rel, original, expected):
    if (rel, original) == ("studio.html", "CUSTOM SCOPE"):
        return "ИНДИВИДУАЛЬНЫЙ ОБЪЁМ"
    if (rel, original) == ("challenge.html", "DEFINE"):
        return "ЦЕЛЬ"
    return expected

def exact_payload_limit(measured):
    if measured != EXACT_PAYLOAD:
        raise ValueError("SITE_A2_D4_DENY changed payload")
    return EXACT_PAYLOAD


# D5 exact successors; inherited legal/English files remain byte-pinned.
D5_LEGAL_RU = "62744a75116170b3ffc83e291776d3e4a1de8e6f17276c8f08de4d3519b6330f"
D5_STATIC_MAIN = {
    "privacy.html": "fb5afd0bf70e30e4368797536970ca12e5532d5cc52b494530a2c1639745dd9c",
    "terms.html": "46efe3eea549f4d95d35cdbe8151bce58d74cfda9701ea8a8131f3447874dffe",
}
def d5_legal_source(root):
    if source_sha(root,"app/(ru)/privacy/page.tsx") != D5_LEGAL_RU:
        raise ValueError("SITE_A2_D5_DENY legal source")
    return D5_LEGAL_RU

def d5_main_pins(root):
    import re
    for rel,expected in D5_STATIC_MAIN.items():
        text=(root/"deploy/live"/rel).read_text(encoding="utf-8")
        match=re.search(r'<main id="main".*?</main>', text, re.S)
        if match is None or sha(match.group(0).encode()) != expected:
            raise ValueError("SITE_A2_D5_DENY static main: "+rel)
    return dict(D5_STATIC_MAIN)
