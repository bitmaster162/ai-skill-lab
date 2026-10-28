"""Exact successor custody for the historical R1-only pricing QA checker."""
from pathlib import Path
import hashlib,json,re
import site_a1_a2_r2_successor as successor
from site_a1_pricing_contract import catalog,snapshot

CHECKER="scripts/check_site_a1_pricing.py"
CHECKER_SHA="d604b0ba337dc42d7a8901ec97859f6e4e7c59e1279a1947936a84b94f745898"

def sha(data):return hashlib.sha256(data).hexdigest()
def verify(root):
    successor.verify()
    old=(root/CHECKER).read_bytes().replace(b"\r\n",b"\n")
    if sha(old)!=CHECKER_SHA:
        raise ValueError("SITE_A2_QA_DENY original R1 pricing checker drift")
    for rel,lang in (("pricing.html","ru"),("en/pricing.html","en")):
        body=(root/"deploy/live"/rel).read_text("utf-8")
        items=re.findall(r'<script type="application/ld\+json">([\s\S]*?)</script>',body)
        objects=[json.loads(x) for x in items]
        offers=[x for x in objects if isinstance(x,dict) and x.get("@type")=="OfferCatalog"]
        if offers!=[catalog(lang)] or len(offers[0]["itemListElement"])!=18:
            raise ValueError("SITE_A2_QA_DENY exact pricing offer catalog")
    if (root/"deploy/live/llms.txt").read_text("utf-8").count(snapshot())!=1:
        raise ValueError("SITE_A2_QA_DENY llms pricing snapshot")
    return True
