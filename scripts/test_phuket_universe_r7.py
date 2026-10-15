#!/usr/bin/env python3
"""R7 targeted acceptance, only local, exact known release payload."""
from __future__ import annotations
import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
import phuket_universe_r7_release_profile as release

class R7Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files={p.relative_to(release.LIVE).as_posix():p.read_bytes()
                   for p in release.LIVE.rglob("*") if p.is_file()}
        cls.profile=json.loads(release.PROFILE_PATH.read_text(encoding="utf-8"))

    def test_exact_identity_and_immutable_r6(self):
        x=release.verify_integrity()
        self.assertEqual((x["files"],x["routes"],x["r6_files_unchanged"]),(107,56,50))
        from build_phuket_universe_r7 import render,r6_parent
        parent=r6_parent()
        self.assertEqual(render(),self.files)
        self.assertEqual(len(parent),107)
        self.assertEqual({k for k in parent if parent[k]!=self.files[k]},
                         set(self.profile["changed_r6_files"])|{"_release.json"})
        self.assertEqual(parent["vercel.json"],self.files["vercel.json"])
        self.assertEqual(parent["lab-command.js"],self.files["lab-command.js"])
        self.assertEqual(parent["phuket-housing-u2.js"],self.files["phuket-housing-u2.js"])
        self.assertEqual(parent["sitemap.xml"],self.files["sitemap.xml"])

    def test_all_56_footers_plus_locale(self):
        from html.parser import HTMLParser
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.footer=False;self.links=[]
            def handle_starttag(self,t,attrs):
                a=dict(attrs)
                if t=="footer":self.footer=True
                if t=="a" and self.footer and a.get("data-universe-event")=="universe_click":
                    self.links.append(a)
            def handle_endtag(self,t):
                if t=="footer":self.footer=False
        for route in self.profile["changed_r6_files"]:
            with self.subTest(route=route):
                text=self.files[route].decode("utf-8")
                p=Links();p.feed(text)
                self.assertEqual(len(p.links),1)
                href="/en/phuket-universe" if route.startswith("en/") or route=="en.html" else "/phuket-universe"
                self.assertEqual(p.links[0].get("href"),href)
                self.assertEqual(text.count('src="/phuket-universe-events.js"'),1)

    def test_only_approved_five_project_links(self):
        domains={"phuketravel.vercel.app","stasph.vercel.app","muaithaiph.vercel.app",
                 "haven-ruddy.vercel.app","rostikson-portfolio.vercel.app"}
        for route in release.PAGES:
            text=self.files[route].decode("utf-8")
            self.assertEqual(text.count('data-universe-event="project_click"'),5)
            for domain in domains:
                self.assertIn('data-universe-event="project_click" rel="noopener" href="https://'+domain+'"',text)
            self.assertNotIn('data-u2-card',text)
            self.assertIn('id="agency-pilot-terms"',text)
            self.assertIn('data-u2-catalog=""',text)

    def test_only_phuket_has_visitor_teaser(self):
        pages={"phuket.html","en/phuket.html"}
        for route in self.profile["changed_r6_files"]:
            text=self.files[route].decode("utf-8")
            self.assertEqual(text.count('data-u3-universe-teaser="true"'),1 if route in pages else 0)

    def test_dormant_events_no_pii_or_network_on_site(self):
        script=self.files["phuket-universe-events.js"].decode("utf-8")
        self.assertIn('const ENABLED = false;',script)
        self.assertIn("JSON.stringify({event, page, locale})",script)
        for forbidden in ("localStorage","sessionStorage","document.cookie","sendBeacon","serviceWorker"):
            self.assertNotIn(forbidden,script)
        self.assertEqual(self.profile["authority"],release.AUTHORITY)
        self.assertEqual(self.profile["accepted_listings"],0)
        self.assertEqual(set(self.profile["u3_universe_events"]),release.EVENTS)

    def test_unknown_manifest_rejected(self):
        manifest=json.loads(self.files["_release.json"])
        manifest["files"][1]=manifest["files"][0]
        old=Path.read_bytes
        target=release.LIVE/"_release.json"
        def tampered(path):
            return json.dumps(manifest).encode() if path==target else old(path)
        with patch.object(Path,"read_bytes",tampered):
            with self.assertRaises(ValueError):release.verify_integrity()

    def test_mutated_html_rejected(self):
        target=release.LIVE/"phuket.html"
        old=Path.read_bytes
        def tampered(path):
            return old(path)+b"forbidden" if path==target else old(path)
        with patch.object(Path,"read_bytes",tampered):
            with self.assertRaisesRegex(ValueError,"content/manifest"):
                release.verify_integrity()

    def test_profile_authority_tampering_rejected(self):
        old=Path.read_bytes
        data=json.loads(old(release.PROFILE_PATH))
        data["authority"]["deploy"]=True
        def tampered(path):
            return json.dumps(data).encode() if path==release.PROFILE_PATH else old(path)
        with patch.object(Path,"read_bytes",tampered):
            with self.assertRaises(ValueError):release.profile()

    def test_existing_event_receiver_and_sqlite_schema_untouched(self):
        # Code does not require D1 or ingress changes for disabled client events.
        from build_phuket_universe_r7 import git
        for k in ("schema/public_event_daily_e38.sql",
                  "services/lead-ingress/api/event.js",
                  "services/lead-receiver-cloudflare/src/index.js",
                  "package-lock.json"):
            self.assertEqual(git("show",release.R6_HEAD+":"+k),(release.ROOT/k).read_bytes())
        self.assertEqual(self.files["lab-command.js"].count(b'fetch("/api/event"'),1)

def run_units():
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(R7Acceptance)
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise ValueError("R7 unit acceptance failure")
if __name__=="__main__":
    run_units()
    print("PHUKET_R7_TARGETED_ACCEPTANCE_PASS")
