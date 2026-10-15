#!/usr/bin/env python3
"""Targeted U3 + dormant-E3.8 acceptance against exact immutable R6."""
from __future__ import annotations
import json,sqlite3,unittest
from pathlib import Path
from html.parser import HTMLParser
from preview import (ROOT,LIVE,FRIENDS,PARENT_SHA as MANIFEST_PIN,PARENT as PARENT_RELEASE,RELEASE,
                     parent_payload,render,make_page,mark_listing_links,sha)

class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[];self.tags=[];self.stack=[]
    def handle_starttag(self,t,a):
        d=dict(a);self.tags.append((t,d))
        if t=="a" and d.get("data-universe-event"):self.links.append(d)

class U3Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=parent_payload()
        cls.files,cls.meta=render()
        cls.public=sorted(k for k in cls.files if k.endswith(".html") and k!="404.html")
    def test_exact_scope_and_source_freeze(self):
        self.assertEqual((len(self.original),len(self.files),len(self.public)),(107,108,56))
        self.assertEqual(self.meta["file_count"],107)
        self.assertEqual(self.meta["public_routes"],56)
        self.assertEqual(self.meta["authority"],{
            "push":False,"pr":False,"merge":False,"deploy":False,
            "production":False,"d1_migration":False,"event_receiver":False})
        self.assertEqual(self.meta["events_enabled"],False)
        changed={k for k in self.original if self.original[k]!=self.files[k]}
        self.assertEqual(changed,set(self.public)|{"_release.json"})
        self.assertEqual(self.files["vercel.json"],self.original["vercel.json"])
        self.assertEqual(self.files["lab-command.js"],self.original["lab-command.js"])
        self.assertEqual(self.files["phuket-housing-u2.js"],self.original["phuket-housing-u2.js"])
        self.assertEqual(self.files["sitemap.xml"],self.original["sitemap.xml"])
        self.assertEqual(sha(self.original["_release.json"]),MANIFEST_PIN)
    def test_manifest_integrity_determinism(self):
        m=json.loads(self.files["_release.json"])
        self.assertEqual(m["release_id"],RELEASE)
        self.assertEqual(m["file_count"],107)
        self.assertEqual(len(m["files"]),107)
        for row in m["files"]:
            b=self.files[row["path"]]
            self.assertEqual((len(b),sha(b)),(row["size"],row["sha256"]))
        self.assertEqual(render()[0],self.files)
    def test_footer_all_languages_including_universe(self):
        for name in self.public:
            with self.subTest(page=name):
                s=self.files[name].decode("utf-8")
                p=P();p.feed(s)
                universe=[x for x in p.links if x["data-universe-event"]=="universe_click"]
                self.assertEqual(len(universe),1)
                expected="/en/phuket-universe" if name.startswith("en/") or name=="en.html" else "/phuket-universe"
                self.assertEqual(universe[0]["href"],expected)
                self.assertEqual(s.count("/phuket-universe-events.js"),1)
                self.assertNotIn("<script src=\"https://",s)
    def test_project_card_markers_and_no_other_project_metadata(self):
        for name in ("phuket-universe.html","en/phuket-universe.html"):
            p=P();p.feed(self.files[name].decode("utf-8"))
            cards=[x for x in p.links if x["data-universe-event"]=="project_click"]
            self.assertEqual(len(cards),5)
            self.assertEqual({x["href"].removeprefix("https://") for x in cards},set(FRIENDS))
            self.assertTrue(all(x.get("rel")=="noopener" for x in cards))
            self.assertEqual(len([x for x in p.links if x["data-universe-event"]=="listing_click"]),0)
    def test_phuket_teasers_and_no_fake_objects(self):
        for name in ("phuket.html","en/phuket.html"):
            s=self.files[name].decode("utf-8")
            self.assertEqual(s.count('data-u3-universe-teaser="true"'),1)
            self.assertEqual(s.count('phuket-universe-teaser-title'),2)
            self.assertIn("catalogue awaiting partner listings" if name.startswith("en/") else
                          "каталог жилья, который ждёт объекты",s)
        for name in ("phuket-universe.html","en/phuket-universe.html"):
            s=self.files[name].decode("utf-8")
            self.assertNotIn("data-u2-card",s)
            self.assertIn('id="agency-pilot-terms"',s)
            self.assertIn("data-u2-catalog",s)
    def test_future_listing_anchor_is_limited_to_card(self):
        fragment='<article class="u2-card" data-u2-card><a href="https://agency.example/listing/1" rel="noopener">source</a></article>'
        tracked=mark_listing_links(fragment)
        self.assertEqual(tracked.count('data-universe-event="listing_click"'),1)
        with self.assertRaises(ValueError):
            mark_listing_links(tracked)
        with self.assertRaises(ValueError):
            mark_listing_links('<article class="u2-card"><a href="https://a.example" rel="noopener">X</a><a href="https://b.example" rel="noopener">Y</a></article>')
    def test_fail_closed_damaged_html(self):
        baseline=self.original["phuket.html"].decode("utf-8")
        with self.assertRaises(ValueError):
            make_page("phuket.html",baseline.replace('<footer class="workshopFooter">',""))
        with self.assertRaises(ValueError):
            make_page("phuket.html",make_page("phuket.html",baseline))
    def test_sqlite_migration_offline_preserves_seven_old_events(self):
        original=(ROOT/"schema/public_event_daily_e38.sql").read_text(encoding="utf-8")
        migration=(Path(__file__).with_name("e3_8_sqlite_candidate.sql")).read_text(encoding="utf-8")
        self.assertIn("OFFLINE SQLITE DESIGN ONLY",migration)
        conn=sqlite3.connect(":memory:")
        conn.executescript(original)
        legacy=["lead_submit_ok","lead_submit_error","cal_click",
                "telegram_click","whatsapp_click","line_click","email_click"]
        for i,event in enumerate(legacy):
            conn.execute("INSERT INTO public_event_daily_e38 VALUES(?,?,?,?,?)",
                         ("2026-10-14",event,"/pricing","en",i+1))
        before=conn.execute("SELECT day,event_name,page,locale,count FROM public_event_daily_e38 ORDER BY event_name").fetchall()
        conn.executescript(migration)
        after=conn.execute("SELECT day,event_name,page,locale,count FROM public_event_daily_e38 ORDER BY event_name").fetchall()
        self.assertEqual(after,before)
        self.assertEqual([x[1] for x in conn.execute("PRAGMA table_info(public_event_daily_e38)")],
                         ["day","event_name","page","locale","count"])
        for event in ["universe_click","project_click","listing_click"]:
            conn.execute("INSERT INTO public_event_daily_e38 VALUES(?,?,?,?,?)",
                         ("2026-10-15",event,"/phuket-universe","ru",1))
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM public_event_daily_e38").fetchone()[0],10)
        for event in ["other","project_click2","lead_submit_okx"]:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO public_event_daily_e38 VALUES(?,?,?,?,?)",
                             ("2026-10-15",event,"/","en",1))
        conn.close()
    def test_no_new_pii_in_event_wire(self):
        src=self.files["phuket-universe-events.js"].decode("utf-8")
        self.assertIn('const ENABLED = false;',src)
        self.assertIn('JSON.stringify({event, page, locale})',src)
        self.assertNotIn("sessionStorage",src)
        self.assertNotIn("localStorage",src)
        self.assertNotIn("document.cookie",src)

if __name__=="__main__":
    unittest.main(verbosity=2)
