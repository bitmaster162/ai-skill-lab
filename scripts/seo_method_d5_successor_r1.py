"""Exact, read-only admission of the unapproved SEO-method static review candidate.

Only permits the two source <main> fingerprints when the complete new 108-file
candidate, the immutable historical archive, and the exact 3-file delta match.
This does not authorize merging or deploying the draft static candidate.
"""
from __future__ import annotations
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import hashlib, json, re

PARENT_SHA = "79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889"
MANIFEST_SHA = "ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0"
ARCHIVE_SHA = "189f273538137c2d4603a7bd9f25b8969e1deed5c7314c2e5509092ecd89b56d"
RELEASE = "AISL_SEO_METHOD_R1_DRAFT_20261121"
FOLDER = "docs/release-candidates/seo-method-r1-20261121"
SOURCES = {
    "app/method/page.tsx": (
        "app/(ru)/method/page.tsx",
        "ada13cf8a2f95e8443b2a55039c36a9732378b4643d68f15115d9ef8a6ba345c",
        "14a38b3578fb6d8e94d5fb32e8e929d2e51371b3f4e58aa1bf38dc13adc79eea",
        "method.html",
    ),
    "app/en/method/page.tsx": (
        "app/(en)/en/method/page.tsx",
        "67aa5fa4440a398bf43c50829fe8e3693b29b76af81e6d490c82b5289919fc59",
        "f978d0c01795cc8527e2939e9ed3b072569a4730b6cedace02c70deb94fe6296",
        "en/method.html",
    ),
}
CHANGED = {"en/method.html", "method.html", "sitemap.xml"}
class CandidateDeny(ValueError):
    pass

def require(value, reason):
    if not value:
        raise CandidateDeny("SEO_METHOD_D5_DENY:" + reason)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main(raw):
    rows = re.findall(rb'<main id="main"[\s\S]*?</main>', raw)
    require(len(rows) == 1, "MAIN_COUNT")
    return rows[0]

def verified_source_main(root: Path, *, sources_override=None, zip_override=None):
    root = Path(root)
    release_dir = root / FOLDER
    parent_data = (root / "deploy/live/_release.json").read_bytes()
    require(sha(parent_data) == PARENT_SHA, "PARENT_SHA")
    parent = json.loads(parent_data)
    require(parent.get("file_count") == 108 and len(parent.get("files", [])) == 108, "PARENT_FILES")
    expected = {r["path"]: r for r in parent["files"]}
    require(len(expected) == 108, "PARENT_DUPLICATE")
    old = {}
    for name, row in expected.items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "PARENT_PATH")
        p = root / "deploy/live" / name
        require(p.is_file() and not p.is_symlink(), "PARENT_FILE:" + name)
        old[name] = p.read_bytes()
        require(len(old[name]) == row["size"] and sha(old[name]) == row["sha256"], "PARENT_BYTES:" + name)

    manifest_raw = (release_dir / "manifest.json").read_bytes()
    require(sha(manifest_raw) == MANIFEST_SHA, "CANDIDATE_MANIFEST_SHA")
    m = json.loads(manifest_raw)
    require(m.get("schema") == "ai-skill-lab.static-release.v1"
        and m.get("release_id") == RELEASE and m.get("patch_id") == RELEASE
        and m.get("parent_manifest_sha256") == PARENT_SHA
        and m.get("file_count") == 108, "CANDIDATE_IDENTITY")
    rows = m.get("files", [])
    require(len(rows) == 108 and len({x["path"] for x in rows}) == 108, "CANDIDATE_ROWS")
    bypath = {x["path"]: x for x in rows}
    require(set(bypath) == set(expected), "CANDIDATE_FILESET")
    digest = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n"
                     for r in sorted(rows, key=lambda v: v["path"])).encode()
    require(sha(digest) == m.get("payload_sha256")
        == "f2678f7fb3ff5381e421795f83bd8115fa7365613806443cfeea9802efacdf88",
        "CANDIDATE_PAYLOAD")
    archive = zip_override if zip_override is not None else (release_dir / "review.zip").read_bytes()
    require(sha(archive) == ARCHIVE_SHA, "ARCHIVE_SHA")
    with ZipFile(BytesIO(archive)) as z:
        paths = z.namelist()
        require(len(paths) == len(set(paths)) == 109
            and set(paths) == set(bypath) | {"_release.json"}, "ARCHIVE_FILESET")
        require(z.read("_release.json") == manifest_raw, "ARCHIVE_MANIFEST")
        new = {}
        for name, row in bypath.items():
            data = z.read(name)
            require(len(data) == row["size"] and sha(data) == row["sha256"], "ARCHIVE_BYTES:" + name)
            new[name] = data

    require({k for k in new if new[k] != old[k]} == CHANGED, "EXACT_DELTA")
    for name, src in SOURCES.items():
        source_path, full_sha, main_sha, html_path = src
        raw = (sources_override or {}).get(name)
        if raw is None:
            raw = (root / source_path).read_bytes()
        require(sha(raw) == full_sha, "SOURCE_SHA:" + name)
        require(sha(main(raw)) == main_sha, "SOURCE_MAIN:" + name)
        previous, candidate = old[html_path], new[html_path]
        first, second = main(previous), main(candidate)
        require(previous.replace(first, b"__MAIN__", 1)
             == candidate.replace(second, b"__MAIN__", 1), "OUTER_HTML:" + html_path)
        require(second.count(b"<article") == 5 and second.count(b"<h1") == 1
             and b'method-example' in second and b"<form" not in second
             and b"<script" not in second and b"/_next/" not in candidate,
            "SEMANTICS:" + html_path)
        require((release_dir / html_path).read_bytes() == candidate, "EXACT_REVIEW_HTML:" + html_path)
    sitemap = old["sitemap.xml"].decode("utf8")
    for route in ("/method", "/en/method"):
        old_row = f"<loc>https://aiskillab.work{route}</loc><lastmod>2026-10-16</lastmod>"
        new_row = f"<loc>https://aiskillab.work{route}</loc><lastmod>2026-11-21</lastmod>"
        require(sitemap.count(old_row) == 1, "SITEMAP_OLD:" + route)
        sitemap = sitemap.replace(old_row, new_row, 1)
    require(sitemap.encode() == new["sitemap.xml"]
        == (release_dir / "sitemap.xml").read_bytes(), "SITEMAP_DELTA")
    return {name: data[2] for name, data in SOURCES.items()}
