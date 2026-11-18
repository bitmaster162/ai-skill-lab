"""Exercise the complete static release candidate offline, including both form paths."""
import hashlib
import json
import os
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree.ElementTree import parse

import build_conversion_r1 as release
from conversion_mobile_r1 import run as check_mobile


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.links = []
        self.ids = set()
        self.tables = 0
        self.canonical = None
        self.alternates = {}
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "table":
            self.tables += 1
        if "id" in attr:
            self.ids.add(attr["id"])
        if tag == "a" and "href" in attr:
            self.links.append(attr["href"])
        if tag == "link" and attr.get("rel") == "canonical":
            self.canonical = attr["href"]
        if tag == "link" and attr.get("rel") == "alternate" and "hreflang" in attr:
            self.alternates[attr["hreflang"]] = attr["href"]


class ConversionCandidateTest(unittest.TestCase):
    def test_release(self):
        with tempfile.TemporaryDirectory() as work:
            out, repeat = Path(work) / "first", Path(work) / "second"
            if os.environ.get("CONVERSION_CANDIDATE_DIR"):
                out = Path(os.environ["CONVERSION_CANDIDATE_DIR"])
            release.build(out)
            release.build(repeat)
            check_mobile(out)
            self.assertEqual((out / "_release.json").read_bytes(), (repeat / "_release.json").read_bytes())
            parent = json.loads((release.LIVE / "_release.json").read_bytes())
            old = {row["path"]: row["sha256"] for row in parent["files"]}
            manifest = json.loads((out / "_release.json").read_bytes())
            self.assertEqual(manifest["parent_manifest_sha256"], release.PARENT)
            self.assertEqual(manifest["file_count"], len(old) + 4)
            rows = {row["path"]: row for row in manifest["files"]}
            expected_changes = {"index.html", "en.html", "guides.html", "en/guides.html", "sitemap.xml", "llms.txt", "vercel.json"}
            new_routes = {f"{prefix}guides/{slug}.html" for prefix in ("", "en/") for slug in release.NEW_GUIDES}
            self.assertEqual(set(rows), set(old) | new_routes)
            for rel, row in rows.items():
                raw = (out / rel).read_bytes()
                sha = hashlib.sha256(raw).hexdigest()
                self.assertEqual((sha, len(raw)), (row["sha256"], row["size"]))
                if rel in old and rel not in expected_changes:
                    self.assertEqual(sha, old[rel], rel)
            sitemap = {item.text for item in parse(out / "sitemap.xml").iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
            llms = (out / "llms.txt").read_text(encoding="utf-8")
            config = json.loads((out / "vercel.json").read_bytes())
            self.assertEqual(config["rewrites"], json.loads((release.LIVE / "vercel.json").read_bytes())["rewrites"])
            for locale in ("ru", "en"):
                prefix = "" if locale == "ru" else "/en"
                alt = "/en" if locale == "ru" else ""
                home = Page(out / ("index.html" if locale == "ru" else "en.html"))
                form_url = f"{prefix}/start#application-form"
                self.assertGreaterEqual(home.links.count(form_url), 2)
                self.assertIn(f"{prefix}/matcher", home.links)
                self.assertGreaterEqual(home.links.count(f"{prefix}/guides"), 2)
                self.assertGreaterEqual(home.links.count(f"{prefix}/proof"), 3)
                form = Page(out / (prefix.lstrip("/") + "/start.html").lstrip("/"))
                self.assertIn("application-form", form.ids)
                listing = Page(out / (prefix.lstrip("/") + "/guides.html").lstrip("/"))
                for slug in release.NEW_GUIDES:
                    route = f"{prefix}/guides/{slug}"
                    article = Page(out / (route.lstrip("/") + ".html"))
                    self.assertIn(route, listing.links)
                    self.assertIn(form_url, article.links)
                    self.assertEqual(article.tables, 4)
                    self.assertEqual(article.canonical, release.guides.ORIGIN + route)
                    self.assertEqual(article.alternates["ru" if locale == "en" else "en"], release.guides.ORIGIN + alt + "/guides/" + slug)
                    self.assertIn(article.canonical, sitemap)
                    self.assertIn(article.canonical, llms)
                    for href in article.links:
                        url = urlsplit(href)
                        if url.scheme or url.netloc:
                            continue
                        if not url.path:
                            if url.fragment:
                                self.assertIn(url.fragment, article.ids, href)
                            continue
                        self.assertTrue(url.path.startswith("/"), href)
                        target = out / ((url.path.strip("/") or "index") + ".html")
                        self.assertTrue(target.exists(), href)
                        if url.fragment:
                            self.assertIn(url.fragment, Page(target).ids, href)


if __name__ == "__main__":
    unittest.main()
