"""Pinned historical R6 projection for SITE-A1/A2 E3 lineage; never trust modified current HTML."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import site_a1_a2_r2_successor as successor
from build_phuket_universe_r7 import make_page
from phuket_universe_r7b_release_profile import PREV_HEAD

ROOT = Path(__file__).resolve().parents[1]
R6 = "3d58999a382b2c11eae7da3d97e9e650c1326f46"
PROFILE_SHA = "4bb0b241618a3d75aee2de39ffd1771279e4d13399e00af2fa45661e57b26d39"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def historical_profile():
    data=(ROOT/"data/phuket_universe_u3_e38_r7b_profile.json").read_bytes()
    if sha(data)!=PROFILE_SHA:
        raise ValueError("SITE_A2_E3_DENY profile SHA")
    return json.loads(data)

@lru_cache(maxsize=1)
def authorize():
    if not successor.active():
        raise ValueError("SITE_A2_E3_DENY unauthorized release")
    successor.verify()
    return historical_profile()

def legacy_r6_html(rel):
    profile=authorize()
    if rel not in profile["changed_r6_files"] or not rel.endswith(".html"):
        raise ValueError("SITE_A2_E3_DENY route")
    old=successor.git_blob(R6,"deploy/live/"+rel)
    r7=successor.git_blob(PREV_HEAD,"deploy/live/"+rel)
    r6_pin=profile["r6_file_pins"][rel]
    r7_pin=profile["r7_html_pins"][rel]
    if (len(old)!=r6_pin["size"] or sha(old)!=r6_pin["sha256"] or
        len(r7)!=r7_pin["size"] or sha(r7)!=r7_pin["sha256"] or
        make_page(rel,old.decode("utf-8")).encode("utf-8")!=r7):
        raise ValueError("SITE_A2_E3_DENY historical R6/R7 replay")
    return old
