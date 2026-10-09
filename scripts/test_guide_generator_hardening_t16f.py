#!/usr/bin/env python3
"""T1.6F1 local-only tests. All generator writes are trapped in memory."""
from __future__ import annotations

import copy
import hashlib
import os
import re
import unittest
from pathlib import Path
from unittest.mock import patch

import build_guides as builder
import guide_route_admission as admission

SLUG = "ai-first-tasks-for-adults"
RU_TITLE = "Гайды по ИИ — AI Skill Lab · Пхукет"
RU_DESCRIPTION = (
    "Короткие проверенные материалы об ИИ для родителей, взрослых учеников "
    "и команд. У каждого — дата проверки и источники."
)
EN_DESCRIPTION = (
    "Short, checked guides for parents, adult learners and teams. "
    "Each one shows when it was checked and its sources."
)
QUIZ = '<script src="/safety-quiz.js" defer></script>'


class GeneratorHardeningT16F(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.existing = builder.guides()
        cls.by_lang = {
            lang: [g for g in cls.existing if g["lang"] == lang]
            for lang in ("ru", "en")
        }

    def _spoof(self, target: Path, payload: str):
        original = Path.read_text

        def mocked(path: Path, *args, **kwargs):
            if path == target:
                return payload
            return original(path, *args, **kwargs)

        return patch.object(Path, "read_text", mocked)

    def test_01_exact_52_route_authority(self):
        html_paths = [
            p for p in builder.LIVE.rglob("*.html") if p.name != "404.html"
        ]
        actual = [builder.route_for_file(p) for p in html_paths]
        self.assertEqual(admission.require_route_set(actual), 52)
        self.assertEqual(len(self.existing), 2)
        self.assertEqual(len(admission.admitted_routes()), 52)
        self.assertEqual(admission.APPROVED_ADDITIONAL_GUIDE_SLUGS, frozenset())

    def test_02_safety_template_only(self):
        for lang in ("ru", "en"):
            with self.subTest(lang=lang):
                path = builder.LIVE / ("en/safety.html" if lang == "en" else "safety.html")
                original = path.read_text(encoding="utf-8")
                self.assertEqual(original.count(QUIZ), 1)
                prefix, suffix = builder.shell(lang)
                self.assertNotIn(QUIZ, prefix + suffix)
                self.assertIn(QUIZ, original)
                self.assertEqual(original[:original.index('<main id="main">')], prefix)

    def test_03_safety_marker_negative_guards(self):
        target = builder.LIVE / "safety.html"
        original = target.read_text(encoding="utf-8")
        changed = {
            "missing": original.replace(QUIZ, ""),
            "duplicate": original.replace(QUIZ, QUIZ + QUIZ),
            "in_header": original.replace(QUIZ, "").replace(
                '<main id="main">', QUIZ + '<main id="main">', 1
            ),
            "within_main": original.replace(QUIZ, "").replace(
                '<main id="main">', '<main id="main">' + QUIZ, 1
            ),
        }
        for name, payload in changed.items():
            with self.subTest(case=name), self._spoof(target, payload):
                with self.assertRaisesRegex(RuntimeError, "quiz script"):
                    builder.shell("ru")

    def test_04_ru_seo_and_visible_subtitle(self):
        self.assertEqual(builder.RU_GUIDES_SEO_TITLE, RU_TITLE)
        self.assertEqual(builder.RU_GUIDES_DESCRIPTION, RU_DESCRIPTION)
        body = builder.listing_main("ru", self.by_lang["ru"])
        self.assertIn("<h1>Гайды</h1>", body)
        self.assertIn("<p>" + RU_DESCRIPTION + "</p>", body)
        published = (builder.LIVE / "guides.html").read_text(encoding="utf-8")
        self.assertIn("<title>" + RU_TITLE + "</title>", published)
        self.assertIn('name="description" content="' + RU_DESCRIPTION + '"', published)
        self.assertIn("<p>" + RU_DESCRIPTION + "</p>", published)
        en_body = builder.listing_main("en", self.by_lang["en"])
        self.assertIn(EN_DESCRIPTION, en_body)
        self.assertIn("<h1>Guides</h1>", en_body)

    def test_05_sitemap_date_source_and_negative_guards(self):
        source = builder.ROOT / "app" / "sitemap.ts"
        original = source.read_text(encoding="utf-8")
        self.assertEqual(builder.read_sitemap_lastmod(), "2026-10-09")
        line = '  const lastModified = "2026-10-09";'
        self.assertEqual(original.count(line), 1)
        cases = {
            "missing": original.replace(line, ""),
            "duplicate": original.replace(line, line + "\n" + line),
            "invalid_calendar": original.replace(line, '  const lastModified = "2026-02-30";'),
            "valid_but_stale": original.replace(line, '  const lastModified = "2026-10-08";'),
            "invalid_format": original.replace(line, '  const lastModified = "09-10-2026";'),
            "dynamic_expression": original.replace(line, "  const lastModified = new Date();"),
        }
        for name, payload in cases.items():
            with self.subTest(case=name), self._spoof(source, payload):
                with self.assertRaisesRegex(RuntimeError, "lastModified"):
                    builder.read_sitemap_lastmod()

    def test_06_css_byte_identity_and_strict_guard(self):
        path = builder.LIVE / "workshop.css"
        original = path.read_bytes()
        text = original.decode("utf-8")
        marker = re.search(
            r"/\* E2_GUIDES_START \*/[\s\S]*?/\* E2_GUIDES_END \*/", text
        )
        self.assertIsNotNone(marker)
        self.assertNotEqual(marker.group(0), builder.GUIDE_CSS)
        self.assertEqual(
            builder.css_rule_linebreaks_only(marker.group(0)),
            builder.css_rule_linebreaks_only(builder.GUIDE_CSS),
        )
        with patch.object(Path, "write_text", side_effect=AssertionError("CSS write forbidden")):
            builder.update_css()
        self.assertEqual(path.read_bytes(), original)
        cases = {
            "selector_semantic_drift": text.replace(".guideCard h2", ".guideCardh2", 1),
            "declaration_drift": text.replace("min-height:60vh", "min-height:61vh", 1),
            "extra_selector_space": text.replace(".guideCard h2", ".guideCard  h2", 1),
            "missing_marker": text.replace("/* E2_GUIDES_END */", "", 1),
            "duplicate_marker": text.replace(
                "/* E2_GUIDES_START */", "/* E2_GUIDES_START *//* E2_GUIDES_START */", 1
            ),
        }
        for name, payload in cases.items():
            with self.subTest(case=name), self._spoof(path, payload):
                with patch.object(Path, "write_text", side_effect=AssertionError("CSS write forbidden")):
                    with self.assertRaisesRegex(RuntimeError, "CSS"):
                        builder.update_css()

    def test_07_full_52_route_regeneration_in_memory(self):
        expected_paths = {
            builder.LIVE / "guides.html",
            builder.LIVE / "en" / "guides.html",
            builder.LIVE / "guides" / "ai-safety-for-kids.html",
            builder.LIVE / "en" / "guides" / "ai-safety-for-kids.html",
            builder.LIVE / "sitemap.xml",
            builder.LIVE / "llms.txt",
        }
        generated: dict[Path, bytes] = {}

        def no_disk_write(path: Path, content: str, **kwargs):
            self.assertIn(path, expected_paths, f"UNAUTHORIZED_WRITE_TARGET {path}")
            self.assertNotIn(path, generated, f"DUPLICATE_WRITE {path}")
            self.assertIsInstance(content, str)
            generated[path] = content.encode("utf-8")
            return len(content)

        def no_mkdir(path: Path, **kwargs):
            self.assertTrue(path.is_dir(), f"UNAUTHORIZED_DIRECTORY_CREATE {path}")

        with patch.object(Path, "write_text", no_disk_write), patch.object(Path, "mkdir", no_mkdir):
            self.assertEqual(builder.main(), 0)
        self.assertEqual(set(generated), expected_paths)
        for path, content in sorted(generated.items()):
            with self.subTest(path=path.relative_to(builder.ROOT)):
                actual = path.read_bytes()
                generated_hash = hashlib.sha256(content).hexdigest()
                actual_hash = hashlib.sha256(actual).hexdigest()
                if content != actual:
                    mismatch = next(
                        (i for i, (a, b) in enumerate(zip(content, actual)) if a != b),
                        min(len(content), len(actual)),
                    )
                    self.fail(
                        f"BYTE_DRIFT {path.relative_to(builder.ROOT)} first_offset={mismatch} "
                        f"generated={generated_hash} published={actual_hash} "
                        f"size_generated={len(content)} size_published={len(actual)} "
                        f"generated_context={content[max(0,mismatch-55):mismatch+85]!r} "
                        f"published_context={actual[max(0,mismatch-55):mismatch+85]!r}"
                    )

    def test_08_synthetic_54_route_pair_no_admission(self):
        self.assertEqual(len(admission.admitted_routes()), 52)
        preview_routes = admission.admitted_routes([SLUG])
        self.assertEqual(len(preview_routes), 54)
        self.assertIn("/guides/" + SLUG, preview_routes)
        self.assertIn("/en/guides/" + SLUG, preview_routes)
        self.assertNotIn("/guides/" + SLUG, admission.admitted_routes())
        staged_dir = os.environ.get("T16F_STAGED_RELEASE_PREP_DIR")
        if staged_dir:
            source_dir = Path(staged_dir)
            staged = [
                builder.parse_guide(source_dir / (SLUG + "." + lang + ".md"))
                for lang in ("ru", "en")
            ]
        else:
            staged = []
            for lang in ("ru", "en"):
                base = copy.deepcopy(self.by_lang[lang][0])
                base["slug"] = SLUG
                base["path"] = ("/en" if lang == "en" else "") + "/guides/" + SLUG
                base["alternate"] = ("" if lang == "en" else "/en") + "/guides/" + SLUG
                base["title"] = "First AI tasks" if lang == "en" else "Первые задачи с ИИ"
                base["seo_title"] = base["title"]
                base["markdown"] = "# " + base["title"] + "\n\nIntro.\n\n## Sources\n\n- [Reference](https://example.org)"
                staged.append(base)
        self.assertEqual({g["lang"] for g in staged}, {"ru", "en"})
        self.assertEqual(len({g["path"] for g in staged}), 2)
        self.assertEqual({g["path"] for g in staged}, preview_routes.difference(admission.admitted_routes()))
        pages = {}
        with patch.object(Path, "write_text", side_effect=AssertionError("preview write forbidden")):
            for guide in staged:
                html = builder.build_page(
                    guide["lang"], title=guide["seo_title"],
                    description=guide["description"], route=guide["path"],
                    alternate=guide["alternate"], page_type="article",
                    image_alt="AI Skill Lab · Phuket", main=builder.article_main(guide),
                    schemas=builder.schemas_for(guide),
                )
                pages[guide["path"]] = html
                self.assertEqual(html.count("<h1>"), 1)
                self.assertIn('href="https://aiskillab.work' + guide["path"] + '"', html)
                self.assertNotIn(QUIZ, html)
                self.assertIn("BreadcrumbList", html)
                self.assertIn('"@type":"Article"', html)
            for lang in ("ru", "en"):
                originals = self.by_lang[lang]
                addition = [g for g in staged if g["lang"] == lang]
                listing = builder.listing_main(lang, originals + addition)
                self.assertEqual(listing.count('class="guideCard"'), 2)
                self.assertIn("/guides/" + SLUG, listing)
        self.assertEqual(len(pages), 2)
        self.assertEqual(admission.APPROVED_ADDITIONAL_GUIDE_SLUGS, frozenset())

    def test_09_e3_2_ru_card_glossary_exact_and_negative(self):
        ru = self.by_lang["ru"][0]
        self.assertEqual(ru["slug"], "ai-safety-for-kids")
        self.assertIn("пять вопросов к любому AI-сервису", ru["description"])
        displayed = builder.listing_description(ru, "ru")
        self.assertIn("пять вопросов к любому ИИ-сервису", displayed)
        self.assertIn(
            displayed,
            (builder.LIVE / "guides.html").read_text(encoding="utf-8"),
        )
        self.assertEqual(builder.listing_description(ru, "en"), ru["description"])
        altered = copy.deepcopy(ru)
        altered["description"] = altered["description"].replace(
            "пять вопросов к любому AI-сервису", "пять вопросов об ИИ"
        )
        with self.assertRaisesRegex(RuntimeError, "E3.2 RU kids"):
            builder.listing_description(altered, "ru")


if __name__ == "__main__":
    unittest.main(verbosity=2)
