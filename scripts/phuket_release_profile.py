"""Exact U1 R3 local release profile; historical releases retain their own gates.

The 54 inherited Workshop routes are byte-pinned. The two Universe routes use
an explicit alternative shell, never a blanket exemption for arbitrary pages.
This module performs reads only; it grants no push, merge, or deploy authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from html.parser import HTMLParser
import phuket_agency_release_profile as agency_r5
import phuket_housing_release_profile as housing_r6
import phuket_universe_r7_release_profile as universe_r7
import phuket_universe_r7b_release_profile as universe_r7b

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
RELEASE = "PHUKET_UNIVERSE_U1_STATIC_R3_20261014"
PARENT_RELEASE = "T1_6F2_ADULT_FIRST_TASKS_R1"
PAYLOAD_SHA = "40606d00063d1ec99f495bf3623f8a8ddba23bc04298c530cf6cd97f92965c10"
PARENT_MANIFEST_SHA = "1c0486827cac8fceab7c2a395d3c12a47edaac56af0ecf72459cce256429e74f"
UNIVERSE_FILES = frozenset({"phuket-universe.html", "en/phuket-universe.html"})
UNIVERSE_ROUTES = frozenset({"/phuket-universe", "/en/phuket-universe"})
ADULT_ROUTES = frozenset({"/guides/ai-first-tasks-for-adults", "/en/guides/ai-first-tasks-for-adults"})
NEW_FILES = UNIVERSE_FILES | frozenset({"phuket-universe.css", "fonts/Manrope-cyrillic.woff2", "fonts/Manrope-latin.woff2", "fonts/OFL-Manrope.txt"})


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def active() -> bool:
    return json.loads((LIVE / "_release.json").read_text(encoding="utf-8")).get("release_id") in {RELEASE, agency_r5.RELEASE, housing_r6.RELEASE, universe_r7.RELEASE, universe_r7b.RELEASE}


def profile() -> dict:
    import site_a1_a2_r2_successor as site_a2
    if site_a2.active():
        status = site_a2.verify()
        return {**json.loads((ROOT / "data/phuket_universe_u3_e38_r7b_profile.json").read_text(encoding="utf-8")),
                "file_count": status["static_assets"], "payload_sha256": status["payload_sha256"]}
    import site_r31_post_r7c_profile as post_r31
    if post_r31.active():
        post_r31.check_release()
        return {**universe_r7b.profile(), "file_count": 108}
    if universe_r7b.active():
        return universe_r7b.profile()
    if universe_r7.active():
        return universe_r7.profile()
    if housing_r6.active():
        return housing_r6.profile()
    if agency_r5.active():
        return agency_r5.profile()
    p = json.loads((ROOT / "data/phuket_universe_u1_static_r3_profile.json").read_text(encoding="utf-8"))
    if (p.get("schema") != "ai-skill-lab.release-profile.v1" or p.get("release_id") != RELEASE
            or p.get("payload_sha256") != PAYLOAD_SHA or p.get("parent_manifest_sha256") != PARENT_MANIFEST_SHA
            or p.get("file_count") != 104 or p.get("public_routes") != 56 or p.get("workshop_routes") != 54
            or set(p.get("universe_routes", [])) != UNIVERSE_ROUTES
            or set(p.get("new_files", [])) != NEW_FILES
            or set(p.get("modified_parent_files", [])) != {"llms.txt", "sitemap.xml"}
            or p.get("authority") != {"push": False, "pr": False, "merge": False, "deploy": False, "production": False}):
        raise ValueError("U1 R3 profile identity/scope mismatch")
    expected_budgets = {"payload_max_bytes": 1323645, "nonfont_max_bytes": 1202257,
                        "font_max_bytes": 121388, "font_max_file_bytes": 54*1024,
                        "html_max_file_bytes": 36*1024, "css_max_file_bytes": 41*1024}
    if p.get("budgets") != expected_budgets:
        raise ValueError("U1 R3 bounded budget changed")
    transfers = p.get("transfer_profiles", {})
    if set(transfers) != UNIVERSE_FILES:
        raise ValueError("U1 transfer profile route scope changed")
    for name, data in transfers.items():
        ru = name == "phuket-universe.html"
        expected_fonts = ["Unbounded-ru-en.woff2", "Manrope-latin.woff2"] + (["Manrope-cyrillic.woff2"] if ru else [])
        expected_caps = {"css_br_max": 9728, "first_br_max": 18432, "first_gzip_max": 21760,
                         "first_with_fonts_max": 108544 if ru else 102400, "font_bytes": 91352 if ru else 76852}
        if data.get("fonts") != expected_fonts or any(data.get(k) != v for k, v in expected_caps.items()):
            raise ValueError("U1 transfer limits or exact font set changed")
    return p


def verify_integrity() -> dict:
    import site_a1_a2_r2_successor as site_a2
    if site_a2.active():
        return site_a2.verify()
    import site_r31_post_r7c_profile as post_r7c
    if post_r7c.active():
        return post_r7c.check_release()
    import phuket_terms_withdrawal_r7c_profile as terms_hotfix
    if terms_hotfix.active():
        return terms_hotfix.check_release()
    if universe_r7b.active():
        return universe_r7b.verify_integrity()
    if universe_r7.active():
        return universe_r7.verify_integrity()
    if housing_r6.active():
        return housing_r6.verify_integrity()
    if agency_r5.active():
        return agency_r5.verify_integrity()
    p = profile()
    m = json.loads((LIVE / "_release.json").read_text(encoding="utf-8"))
    if m.get("schema") != "ai-skill-lab.static-release.v1" or m.get("release_id") != RELEASE:
        raise ValueError("Not the exact R3 release")
    records = m.get("files", [])
    if len(records) != 104 or len({e["path"] for e in records}) != 104:
        raise ValueError("R3 duplicate/missing file records")
    actual = {}
    for path in LIVE.rglob("*"):
        if path.is_symlink():
            raise ValueError("R3 symlink forbidden")
        if path.is_file() and path.name != "_release.json":
            rel = path.relative_to(LIVE).as_posix()
            raw = path.read_bytes()
            actual[rel] = {"size": len(raw), "sha256": sha(raw)}
    recorded = {e["path"]: {"size": e["size"], "sha256": e["sha256"]} for e in records}
    if actual != recorded or m.get("file_count") != 104:
        raise ValueError("R3 actual payload differs from manifest")
    digest = sha("".join(f"{name}\t{entry['size']}\t{entry['sha256']}\n" for name, entry in sorted(actual.items())).encode("utf-8"))
    if digest != PAYLOAD_SHA or m.get("payload_sha256") != PAYLOAD_SHA:
        raise ValueError("R3 independent payload pin mismatch")
    parent = p["parent_file_pins"]
    parent_digest = sha("".join(f"{name}\t{e['size']}\t{e['sha256']}\n" for name, e in sorted(parent.items())).encode("utf-8"))
    if parent_digest != "188c0b7c3204dd4c1366a51facafeb09421c929e58913e34c7500d9fdf2ea30e":
        raise ValueError("Independent historical payload pin mismatch")
    if len(parent) != 98 or set(actual) - set(parent) != NEW_FILES or set(parent) - set(actual):
        raise ValueError("R3 lineage inventory changed")
    differences = {name for name in parent if actual[name] != parent[name]}
    if differences != {"llms.txt", "sitemap.xml"}:
        raise ValueError("Inherited Workshop payload changed")
    fonts = {name: entry for name, entry in actual.items() if name.endswith(".woff2")}
    if len(fonts) != 4 or fonts != p["fonts"]:
        raise ValueError("R3 exact font inventory changed")
    total = sum(e["size"] for e in actual.values())
    font_bytes = sum(e["size"] for e in fonts.values())
    if total != 1323645 or font_bytes != 121388 or total - font_bytes != 1202257:
        raise ValueError("R3 measured payload budget changed")
    return {"release": RELEASE, "files": 104, "routes": 56, "workshop_routes": 54,
            "parent_files_unchanged": 96, "font_bytes": font_bytes, "payload_bytes": total}


def inherited_pin_overrides() -> dict[str, str]:
    """Use committed R3 pins only; do not regenerate expected hashes at runtime."""
    import site_a1_a2_r2_successor as site_a2
    if site_a2.active():
        return site_a2.inherited_pin_overrides()
    if not active():
        return {}
    p = profile()
    verified = verify_integrity()
    inherited = {"deploy/live/" + name: pin["sha256"] for name, pin in p["parent_file_pins"].items() if name not in {"sitemap.xml", "llms.txt"}}
    inherited.update(p["source_override_sha256"])
    if universe_r7b.active():
        inherited.update({"deploy/live/" + name: pin["sha256"]
                          for name, pin in p["r7_html_pins"].items()})
    if universe_r7.active():
        inherited.update({"deploy/live/" + name: pin["sha256"]
                          for name, pin in p["r7_html_pins"].items()})
    # Only the independently verified R7C withdrawal supersedes these three R7B pins.
    # All other historical seals stay unchanged; never derive expected hashes from live files.
    import phuket_terms_withdrawal_r7c_profile as r7c
    if r7c.active():
        if verified.get("manifest_sha256") != r7c.R7C_MANIFEST_SHA:
            raise ValueError("R7C inheritance not independently verified")
        inherited.update({
            "deploy/live/_release.json": r7c.R7C_MANIFEST_SHA,
            "deploy/live/phuket-universe.html": "2b7c61e013d25815d27b98bb64db9357a64c36a7ec2e6c53a5dfc0ccf357de3a",
            "deploy/live/en/phuket-universe.html": "5acd537b8c1d8e346f05ac04719c7a9e1b3978ccd130d680b3216f0ef93eefa6",
        })
    import site_r31_post_r7c_profile as post_r7c
    if post_r7c.active():
        if verified.get("manifest_sha256") != post_r7c.expected_manifest_sha():
            raise ValueError("Post-R7C site inheritance not independently verified")
        inherited.update(post_r7c.inherited_pin_overrides())
    return inherited


class Tags(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.tags = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def universe_page(path: Path) -> bool:
    """Validate the approved alternate shell before separating it from Workshop."""
    if not active():
        return False
    try:
        rel = path.resolve().relative_to(LIVE.resolve()).as_posix()
    except ValueError:
        return False
    if rel not in UNIVERSE_FILES:
        return False
    verify_integrity()
    text = path.read_text(encoding="utf-8")
    tags = Tags(text).tags
    if ([a.get("id") for t, a in tags if t == "section"] != ["top", "orbit", "homes", "agencies"]
            or sum(t == "h1" for t, a in tags) != 1 or sum(t == "svg" for t, a in tags) != (7 if housing_r6.active() or universe_r7.active() or universe_r7b.active() else 8)
            or not any(t == "main" and a.get("id") == "main" for t, a in tags)
            or not any(t == "header" for t, a in tags) or not any(t == "footer" for t, a in tags)
            or any(t == "style" or "style" in a for t, a in tags)
            or any(t == "form" for t, a in tags)
            or "[TERMS FOR AGENCIES]" in text or "[УСЛОВИЯ ДЛЯ АГЕНТСТВ]" in text
            or "mailto:robert@aiskillab.work" not in text):
        raise ValueError("Universe alternative shell failed: " + rel)
    return True
