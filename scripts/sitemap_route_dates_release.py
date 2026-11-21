"""Verify the dated sitemap as an exact one-asset successor of diagnostic R2."""
from functools import lru_cache
import json
import re

import diagnostic_intent_release as previous
from guide_donor_release import git, sha

ROOT, LIVE = previous.ROOT, previous.LIVE
RELEASE_ID = "AISL_SITEMAP_ROUTE_DATES_R1_20261122"
PARENT_COMMIT = "eb5ee27a102b16ed06c662096ae650f4931ac709"
PARENT_SHA = previous.MANIFEST_SHA
MANIFEST_SHA = "eafa144171a7deed62f06d4a18b6fa98bab7c169cf6ec829b6709060be4b52ca"
PAYLOAD_SHA = "0e377c619f86a36f55d925056b4073dc17a3cc5e5ff2f19962a7a5fedf77202f"
CHANGED = {"sitemap.xml"}
SOURCE_SHA = {
    **previous.SOURCE_SHA,
    "app/sitemap.ts": "6aa1426352d1b60e50839cf7eccf385cc381dd1f45d28470bb2dba1229d7e7c5",
    "lib/guides.ts": "05fc14abef9884da221a73e02a7c18aded8b6be04f41d4fde16d00e88eeb0130",
}
# Each locale shipped one updated diagnostic link on each of these nine routes.
ROUTES = {prefix + path for prefix in ("", "/en")
          for path in ("", "/business", "/kids", "/matcher", "/parents", "/personal", "/pricing", "/start", "/teens")}


def require(ok, message):
    if not ok:
        raise ValueError("SITEMAP_ROUTE_DATES_DENY " + message)


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


@lru_cache(maxsize=1)
def parent_inputs():
    git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    manifest, sitemap, guides = (
        git("show", PARENT_COMMIT + ":" + rel)
        for rel in ("deploy/live/_release.json", "deploy/live/sitemap.xml", "lib/guides.ts")
    )
    require(sha(manifest) == PARENT_SHA, "parent manifest")
    require((ROOT / "scripts/diagnostic_intent_release.py").read_bytes() ==
            git("show", PARENT_COMMIT + ":scripts/diagnostic_intent_release.py"), "parent verifier")
    return manifest, sitemap, guides


def updated_sitemap(original):
    """Use the published XML as the template; only replace the 18 evidenced dates."""
    result = original
    for route in sorted(ROUTES):
        url = ("https://aiskillab.work" + (route or "/")).encode()
        prefix = b"<loc>" + url + b"</loc><lastmod>"
        pattern = re.escape(prefix) + rb"2026-10-\d\d</lastmod>"
        result, count = re.subn(pattern, prefix + b"2026-11-21</lastmod>", result)
        require(count == 1, "parent route " + url.decode())
    return result


def source_sha(rel):
    digest = sha((ROOT / rel).read_bytes())
    require(digest == SOURCE_SHA[rel], "source " + rel)
    return digest


def verify(*, manifest_override=None, file_overrides=None, source_overrides=None):
    raw = (LIVE / "_release.json").read_bytes() if manifest_override is None else manifest_override
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    manifest = json.loads(raw)
    prior, original_xml, original_guides = parent_inputs()
    require(manifest["release_id"] == manifest["patch_id"] == RELEASE_ID and
            manifest["parent_manifest_sha256"] == PARENT_SHA, "manifest identity")

    files = dict(file_overrides or {})
    xml = files.pop("sitemap.xml", (LIVE / "sitemap.xml").read_bytes())
    require(xml == updated_sitemap(original_xml), "sitemap delta")
    sources = dict(source_overrides or {})
    for rel in ("app/sitemap.ts", "lib/guides.ts"):
        data = sources.pop(rel, (ROOT / rel).read_bytes())
        require(sha(data) == SOURCE_SHA[rel], "source " + rel)

    # Reuse R2's complete inventory, on-disk, source, and historical checks.
    # Reconstruct its three superseded inputs with the exact Git predecessor.
    old = previous.verify(manifest_override=prior, file_overrides={**files, "sitemap.xml": original_xml},
                          source_overrides={**sources, "lib/guides.ts": original_guides})
    new_rows = [dict(row, size=len(xml), sha256=sha(xml)) if row["path"] == "sitemap.xml" else row
                for row in old["files"]]
    require(manifest["files"] == new_rows and manifest["file_count"] == old["file_count"] == 112,
            "one changed asset")
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in new_rows)
    require(sha(listing.encode()) == manifest["payload_sha256"] == PAYLOAD_SHA, "payload")
    return manifest


def static_main_sha(rel):
    verify()
    matches = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(matches) == 1, "main " + rel)
    return sha(matches[0])
