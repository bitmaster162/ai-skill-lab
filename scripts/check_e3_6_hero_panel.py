#!/usr/bin/env python3
"""E3.6 isolated release seal; retain E3.5 content and earlier byte protections.

Never writes files, updates SHA seals, changes route admission or deploys.
The historical E3.5 checker and its SHA pins remain byte-for-byte unchanged.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "E3_6_WORKSHOP_HERO_PANEL_R1"
BASE = "97233ea8bb154fca22f232b8f02c5af84d69fc61"
BASE_TREE = "2a244dc1c45d014b97dc17ab5b5b8471c27e8a8b"
PINS_PATH = "data/e3_6_hero_panel_pins.json"
PINS_SHA = "5d24c15bf8d62a0ea56a2559eaf78b7b98692ca727254a124e4982b95a88070e"
E35_PINS_SHA = "c7a65c3e4dfb110bbaa573f2c7f4939ee55753215e1b86f829ab84ce5ad9037d"
MANIFEST_SHA = "3b762726614a3a0cf292abf23501be4f68d49df857f72bed26065e6515103c81"
PAYLOAD_SHA = "cd18e15cdea7996b5164778983f413616309222fac323cc64966887ad1712bad"
SOURCE_CSS_SHA = "8d85d9d61e84cc178af370b7faa840b8dd73b5318ce0eb1ccd07b63c80924109"
STATIC_CSS_SHA = "a666815eb37b12ab643de504fd17e0a12255d25989c63b364ea5c58693a3da06"
SOURCE_SUFFIX = b".hero>.heroPanel{align-self:start}\n"
STATIC_SUFFIX = b".workshopHero>.heroPanel{align-self:start}\n"
E2_GUIDES = rb"/\* E2_GUIDES_START \*/[\s\S]*?/\* E2_GUIDES_END \*/"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def lf(raw: bytes) -> bytes:
    out = raw.replace(b"\r\n", b"\n")
    if b"\r" in out or raw.count(b"\r\n") not in (0, raw.count(b"\n")):
        raise ValueError("mixed or invalid source line endings")
    return out


def validate(overrides: Mapping[str, bytes] | None = None) -> dict:
    """Fully read-only verifier. Optional byte overrides support negative QA."""
    provided = {} if overrides is None else dict(overrides)
    errors: list[str] = []
    checks = 0

    def need(ok: bool, msg: str) -> None:
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(msg)

    def read(rel: str) -> bytes:
        if rel in provided:
            return provided[rel]
        return (ROOT / rel).read_bytes()

    def exact_lf(rel: str, expected: str, size: int | None = None) -> None:
        try:
            raw = lf(read(rel))
            need(sha(raw) == expected, f"protected byte drift {rel}")
            if size is not None:
                need(len(raw) == size, f"protected byte length drift {rel}")
        except (OSError, ValueError) as err:
            need(False, f"protected byte read/EOL {rel}: {err}")

    try:
        pin_bytes = read(PINS_PATH)
        need(sha(pin_bytes) == PINS_SHA, "E3.6 pins SHA drift")
        pin = json.loads(pin_bytes)
        need(isinstance(pin, dict), "E3.6 pins must be object")
        if not isinstance(pin, dict):
            return {"checks": checks, "errors": errors}
        need(pin.get("schema") == "aiskillab.e3-6.hero-panel.exact-source-seal.v1", "E3.6 pins schema")
        need(pin.get("release_id") == RELEASE, "E3.6 pins release ID")
        need(pin.get("base_main") == BASE and pin.get("base_tree") == BASE_TREE, "E3.6 pin lineage")
        need(pin.get("e35_release_id") == "E3_5_HEADING_STRUCTURE_R1", "E3.5 lineage")
        need(pin.get("e35_manifest_sha256") == "1fa3f65800dc734ed976b06b5c4f6fe96a13ec61fb3a57e2d2f4fab2136c499e", "E3.5 manifest lineage")
        need(pin.get("e35_payload_sha256") == "32438c2091a002ca14424629066759b6eb8798222488c3d24bfb881131bbb296", "E3.5 payload lineage")
        need(pin.get("e35_pins_sha256") == E35_PINS_SHA, "E3.5 SHA seal lineage")
        prior_pin_bytes = read("data/e3_5_heading_pins.json")
        need(sha(prior_pin_bytes) == E35_PINS_SHA, "E3.5 historical pins modified")
        old = json.loads(prior_pin_bytes)
        need(old["release_id"] == "E3_5_HEADING_STRUCTURE_R1", "E3.5 historical pin release")
        old_assets = dict(old["assets"])
        old_assets.pop("deploy/live/workshop.css")
        need(pin.get("e35_inherited_assets") == old_assets, "E3.5 non-CSS protected assets changed")
        need(pin.get("e35_inherited_preserved") == old["preserved"], "E3.5 preserved protection set changed")
        need(len(old_assets) == 7 and len(old["preserved"]) == 10, "E3.5 inherited pin count")
        for rel, item in old_assets.items():
            exact_lf(rel, item["accepted_sha256"], item["accepted_lf_bytes"])
        for rel, expected in old["preserved"].items():
            exact_lf(rel, expected)

        e36_src = pin["e36_source_css"]
        e36_css = pin["e36_static_css"]
        need(e36_src["path"] == "components/workshop/WorkshopShell.module.css", "E3.6 source CSS path")
        need(e36_css["path"] == "deploy/live/workshop.css", "E3.6 static CSS path")
        need(e36_src["sha256"] == SOURCE_CSS_SHA and e36_css["sha256"] == STATIC_CSS_SHA, "E3.6 CSS pin digest")
        need(e36_src["suffix_ascii"].encode("ascii") == SOURCE_SUFFIX, "E3.6 source CSS scoped suffix")
        need(e36_css["suffix_ascii"].encode("ascii") == STATIC_SUFFIX, "E3.6 static CSS scoped suffix")
        for key, value, suffix, expected_sha, expected_bytes in [
            (e36_src, "components/workshop/WorkshopShell.module.css", SOURCE_SUFFIX, SOURCE_CSS_SHA, 32276),
            (e36_css, "deploy/live/workshop.css", STATIC_SUFFIX, STATIC_CSS_SHA, 41174),
        ]:
            try:
                raw = lf(read(value))
                need(len(raw) == expected_bytes == key["bytes"], f"{value} exact size")
                need(sha(raw) == expected_sha, f"{value} exact E3.6 SHA")
                need(raw.endswith(suffix) and raw.count(suffix) == 1, f"{value} unique appended CSS")
                if raw.endswith(suffix):
                    before = raw[:-len(suffix)]
                    need(len(before) == key["prior_bytes"], f"{value} original CSS length")
                    need(sha(before) == key["prior_sha256"], f"{value} original CSS changed outside one selector")
            except (OSError, UnicodeError, ValueError) as err:
                need(False, f"E3.6 CSS failed {value}: {err}")
        need(e36_css["prior_sha256"] == old["assets"]["deploy/live/workshop.css"]["accepted_sha256"], "E3.5 CSS SHA reference")
        need(e36_css["prior_bytes"] == old["assets"]["deploy/live/workshop.css"]["accepted_lf_bytes"], "E3.5 CSS length reference")
        try:
            section = re.search(E2_GUIDES, read("deploy/live/workshop.css"))
            need(section is not None, "E2 guides CSS marker missing")
            if section is not None:
                need(sha(section.group()) == pin.get("e2_guides_css_sha256"), "E2 guide CSS marker section drift")
        except (OSError, ValueError) as err:
            need(False, f"guide CSS read failure: {err}")

        manifest_bytes = read("deploy/live/_release.json")
        need(sha(manifest_bytes) == MANIFEST_SHA, "E3.6 release manifest exact seal drift")
        manifest = json.loads(manifest_bytes)
        need(manifest.get("release_id") == RELEASE, "E3.6 release manifest identity")
        need(manifest.get("schema") == "ai-skill-lab.static-release.v1", "E3.6 release schema")
        need(type(manifest.get("file_count")) is int and manifest["file_count"] == 96, "96 released payload files")
        need(manifest.get("payload_sha256") == PAYLOAD_SHA, "E3.6 payload digest")
        expected_manifest = pin.get("manifest", {})
        need(expected_manifest.get("sha256") == MANIFEST_SHA and expected_manifest.get("payload_sha256") == PAYLOAD_SHA,
             "E3.6 manifest cross-pin mismatch")
        need(expected_manifest.get("file_count") == 96 and expected_manifest.get("routes") == 52, "E3.6 released route count")
        need(len(manifest_bytes) == expected_manifest.get("bytes"), "E3.6 manifest file size")
        entries = manifest.get("files")
        need(isinstance(entries, list) and len(entries) == 96, "96 manifest entries")
        if not isinstance(entries, list) or len(entries) != 96:
            return {"checks": checks, "errors": errors}
        listed = {}
        for row in entries:
            if not isinstance(row, dict):
                need(False, "manifest asset record malformed")
                continue
            name = row.get("path")
            need(isinstance(name, str) and name not in listed, "manifest duplicate or invalid asset path")
            if isinstance(name, str):
                listed[name] = (row.get("size"), row.get("sha256"))
        need(len(listed) == 96, "unique manifest file count")
        live = ROOT / "deploy/live"
        present = set(p.relative_to(live).as_posix() for p in live.rglob("*") if p.is_file() and p.name != "_release.json")
        need(present == set(listed), "96-file exact manifest inventory mismatch")
        actual = {}
        for name in sorted(present):
            file_bytes = read("deploy/live/" + name)
            pair = (len(file_bytes), sha(file_bytes))
            actual[name] = pair
            need(pair == listed.get(name), f"manifest exact asset SHA mismatch {name}")
        aggregate = "".join(f"{name}\t{length}\t{digest}\n" for name, (length, digest) in sorted(actual.items())).encode()
        need(sha(aggregate) == PAYLOAD_SHA, "release aggregate SHA")
        total = sum(x[0] for x in actual.values())
        nonfont = sum(x[0] for name, x in actual.items() if not name.endswith(".woff2"))
        need(total == expected_manifest.get("total_payload_bytes") == 1162770, "E3.6 payload bytes")
        need(nonfont == expected_manifest.get("nonfont_bytes") == 1080718, "E3.6 non-font bytes")
        need(total <= 1140 * 1024 and nonfont <= 1060 * 1024, "E3.5 aggregate ceilings preserved")
        need(actual.get("workshop.css") == (41174, STATIC_CSS_SHA), "new CSS exact listed SHA")
        need(len([x for x in actual if x.endswith(".html")]) == 53, "52 public routes and 404")
        need("guides/ai-first-tasks-for-adults.html" not in actual, "unapproved new guide in E3.6")
        need("en/guides/ai-first-tasks-for-adults.html" not in actual, "unapproved new EN guide in E3.6")

        for lang, rel in (("ru", "deploy/live/pricing.html"), ("en", "deploy/live/en/pricing.html")):
            text = read(rel).decode("utf-8")
            h2 = [re.sub(r"<[^>]+>", "", x).strip()
                  for x in re.findall(r"<h2[^>]*>(.*?)</h2>", text, re.S | re.I)]
            need(len(h2) == 10 and len(set(h2)) == 10, f"E3.5 pricing 10 unique H2 {lang}")
            need(all(h2.count(x) == 1 for x in old["age_labels"][lang]), f"E3.5 pricing labels {lang}")
            need(old["tagline"][lang] not in h2, f"E3.5 pricing generic heading {lang}")
            need(text.count('class="priceGrid"') == 5, f"E3.5 five price grids {lang}")
            for label in old["age_labels"][lang]:
                expected = f'<div class="sectionHead"><span>{old["tagline"][lang]}</span><h2>{label}</h2></div>'
                need(text.count(expected) == 1, f"E3.5 heading/eyebrow relation {lang} {label}")
        for rel in ("deploy/live/index.html", "deploy/live/en.html"):
            text = read(rel).decode("utf-8")
            h2 = [re.sub(r"<[^>]+>", "", x).strip()
                  for x in re.findall(r"<h2[^>]*>(.*?)</h2>", text, re.S | re.I)]
            need(len(h2) == 8 and all(len(x) >= 3 for x in h2), f"E3.5 homepage H2 semantics {rel}")
            need(text.count('<p class="promptAuditScore"><span data-pa-score></span>/10</p>') == 1, f"E3.5 Prompt Auditor non-heading score {rel}")
            need(text.count('src="/prompt-auditor.js"') == 1, f"E3.5 Prompt Auditor runtime {rel}")
            need(text.count("data-prompt-auditor") == 1, f"E3.5 Prompt Auditor widget {rel}")
        source = read("components/workshop/WorkshopShell.module.css")
        compiled = read("deploy/live/workshop.css")
        need(source.count(SOURCE_SUFFIX) == 1 and compiled.count(STATIC_SUFFIX) == 1,
             "one E3.6 hero self-align rule per renderer")
    except (OSError, KeyError, TypeError, ValueError, UnicodeError, AttributeError) as err:
        need(False, f"E3.6 verifier input failure: {err}")

    return {"checks": checks, "errors": errors, "release": RELEASE,
            "route_count": 52, "file_count": 96}


def main() -> int:
    try:
        release = json.loads((ROOT / "deploy/live/_release.json").read_text(encoding="utf-8")).get("release_id")
    except (OSError, ValueError, TypeError) as err:
        print(f"E3_6_HERO_PANEL_FAIL manifest: {err}")
        return 1
    if release != RELEASE:
        print(f"E3_6_HERO_PANEL_NOT_APPLICABLE release={release}")
        return 0
    answer = validate()
    print(f"E3_6_HERO_PANEL_CHECK checks={answer['checks']} files=96 routes=52")
    if answer["errors"]:
        print("E3_6_HERO_PANEL_FAIL")
        for e in answer["errors"]:
            print("FAIL:", e)
        return 1
    print("E3_6_HERO_PANEL_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
