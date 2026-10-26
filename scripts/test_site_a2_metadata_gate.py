#!/usr/bin/env python3
"""Exact SITE-A1/A2 revised-route sitemap and preexisting EN title gate contract."""
from __future__ import annotations
import json,re,subprocess,unittest,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/"deploy/live"
SRC=ROOT/"app/sitemap.ts"
GATE=ROOT/"scripts/check_search_metadata.py"
CHANGED=frozenset({"/business","/challenge","/faq","/phuket","/privacy",
                    "/projects","/proof","/start","/studio","/teens","/terms"})
PRICE=frozenset({"/pricing","/en/pricing"})
ORIGIN="https://aiskillab.work"
def git(*a):
 return subprocess.run(["git","--no-optional-locks","-C",str(ROOT),*a],
     check=True,capture_output=True,timeout=30).stdout
class Sitemaps(unittest.TestCase):
 def setUp(self):
  self.source=SRC.read_text("utf-8")
  self.gate=GATE.read_text("utf-8")
  namespace={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}
  xml=ET.fromstring((LIVE/"sitemap.xml").read_bytes())
  self.data={node.find("x:loc",namespace).text.split(ORIGIN,1)[1]:
             node.find("x:lastmod",namespace).text
             for node in xml.findall("x:url",namespace)}
 def test_exact_source_modified_ru_routes(self):
  string='  const siteA2Routes = ["/business", "/challenge", "/faq", "/phuket", "/privacy", "/projects", "/proof", "/start", "/studio", "/teens", "/terms"];'
  self.assertEqual(self.source.count(string),1)
  self.assertEqual(len(CHANGED),11)
 def test_only_thirteen_new_sitemap_dates(self):
  got={p for p,date in self.data.items() if date=="2026-10-26"}
  self.assertEqual(got,CHANGED|PRICE)
  self.assertEqual(len(got),13)
 def test_preserve_every_other_date(self):
  previous=git("show","9d2ed0c1fa98d94457052392208cb3526385a2ba:deploy/live/sitemap.xml")
  namespace={"x":"http://www.sitemaps.org/schemas/sitemap/0.9"}
  xml=ET.fromstring(previous)
  old={node.find("x:loc",namespace).text.split(ORIGIN,1)[1]:
       node.find("x:lastmod",namespace).text
       for node in xml.findall("x:url",namespace)}
  self.assertEqual(set(old),set(self.data))
  for route,stamp in self.data.items():
   if route not in CHANGED:self.assertEqual(stamp,old[route],route)
 def test_en_start_historic_title_main_unchanged(self):
  baseline=git("show","d0a858a7787088dabf6d914e45fb0cde41b743e8:deploy/live/en/start.html")
  pr=git("show","9d2ed0c1fa98d94457052392208cb3526385a2ba:deploy/live/en/start.html")
  self.assertEqual(baseline,pr)
  title=re.search(rb"<title>(.*?)</title>",baseline).group(1).decode()
  self.assertEqual(title,"Start — pick a track and first task | AI Skill Lab · Phuket")
  self.assertIn('"/en/start": "Start — pick a track and first task | AI Skill Lab · Phuket"',self.gate)
  self.assertNotIn('"/en/start": "Start — pick a track and a first task | AI Skill Lab · Phuket"',self.gate)
 def test_exact_gate_pricing_routes(self):
  self.assertIn('successor_price = frozenset(("/pricing", "/en/pricing"))',self.gate)
  self.assertIn('per_route_lastmod = "2026-10-26"',self.gate)
  self.assertIn('SITE-A2 exact per-route lastModified expression missing',self.gate)
 def test_historic_r7b_files_unchanged(self):
  for name in ("scripts/phuket_universe_r7b_release_profile.py",
    "data/phuket_universe_u3_e38_r7b_profile.json"):
   self.assertEqual(git("show","HEAD:"+name),
                    git("show","d0a858a7787088dabf6d914e45fb0cde41b743e8:"+name))
if __name__=="__main__":
 unittest.main(verbosity=2)
