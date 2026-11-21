"""Exact successor preserving diagnostic intent across the two Start language links."""
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
import io
import json
import re
import tarfile

import guide_donor_release as parent

ROOT, LIVE = parent.ROOT, parent.LIVE
sha = parent.sha
GUIDE_COMMIT = "5c004dd5fb45d0621999e50e6ff2ec30b03d9e61"
PARENT_COMMIT = "aa2717fca150640660769ac1d6daa2ec3f9ccbf2"
PARENT_SHA = "78cb75d81138d54f47a37555f6eea6dff9f53f578a76779d902f0c39e97530dc"
RELEASE_ID = "AISL_DIAGNOSTIC_INTENT_R2_20261121"
MANIFEST_SHA = "aa60dba1a0760c0b74eb02e84a5168d397d87d38263fc27e54935687ce12a6ff"
PAYLOAD_SHA = "b5a10b18ca918fd8f5de0e9746c0f12ed337b7760c23ee8a10aee9b8770d7c0b"

ROUTE_NAMES = ("business", "kids", "matcher", "parents", "personal", "pricing", "start", "teens")
DONOR_PAGES = {"index.html", "en.html"} | {
    prefix + name + ".html" for prefix in ("", "en/") for name in ROUTE_NAMES
}
RUNTIME = "lead-form-runtime.js"
START_PAGES = {"start.html", "en/start.html"}
CHANGED = START_PAGES | {RUNTIME}
R1_SOURCE_SHA = {
    **parent.r3.SOURCE_SHA,
    **parent.SOURCE_SHA,
    # Pins for changed sources supplement the inherited analytics and guide seals.
    "components/IntroCallCta.tsx": "18bc9dadd6ef83fa53b5ee84e24533ee7d90ea5ec4ea1b39d1e88474a09c9d48",
    "components/LeadForm.tsx": "232e436879b60d2b76a4b71a5894ca51e5eb1c6a206b75c29b6ef51db19b1ce2",
    "components/workshop/WorkshopPricing.tsx": "ac6f20b713b4d3beb123e6a0dc0be3fb12d75e47dd1a692c8cf2c522fc6ae8ce",
    "lib/diagnostic-intent.ts": "8d226a82ab3e08fa55b341cb542ea8f1d27aa1db4075dda1275530bfcb61bdeb",
    "lib/guides.ts": "d2cf3ce7fcab511243330fcf3a29569e4707d012a363cac2f28cfad22a35cdc7",
    "public/lead-form-runtime.js": "8637e076806ad5291b0ec438337428108c6798f81adbd950f6346024d02bd8cf",
}
SOURCE_SHA = {
    **R1_SOURCE_SHA,
    "components/workshop/WorkshopShell.tsx": "5f226146c568393bdccd7162903a3e0da48e9f68e3493c3447520f39598c1bd9",
    "components/workshop/StartLanguageLink.tsx": "984b9b6a4c44c73ec15151be3ba14ef9b29de1a18a711bb370f3023c77bb5d63",
    "lib/guides.ts": "c7ecb56dd131faf619e2363acb5749cc27dc9f45826d22f2f7832f37f4928a89",
    "public/lead-form-runtime.js": "cb0582dcccfb813112b06c70f9ab2638586af346383f2f9c919e4bea94b1cc17",
}
PARENT_VERIFIER = "scripts/guide_donor_release.py"
PARENT_TEST = "scripts/test_guide_donor_release.py"


def require(ok, reason):
    if not ok:
        raise ValueError("DIAGNOSTIC_INTENT_RELEASE_DENY: " + reason)


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


@contextmanager
def historical_workspace(commit, files):
    """Materialize the original release and tests with access to its fixed Git ancestors."""
    parent.git("merge-base", "--is-ancestor", commit, "HEAD")
    archive = parent.git("archive", "--format=tar", commit, "--", *files)
    with TemporaryDirectory(prefix="aisl-diagnostic-parent-") as tmp:
        root = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            for item in bundle:
                if item.isdir():
                    continue
                rel = Path(item.name)
                require(item.isfile() and not rel.is_absolute() and ".." not in rel.parts,
                        "parent archive path")
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(bundle.extractfile(item).read())
        gitdir = parent.git("rev-parse", "--absolute-git-dir").decode().strip()
        (root / ".git").write_text("gitdir: " + gitdir + "\n", encoding="utf-8")
        yield root


def parent_guide_workspace():
    files = ["deploy/live", PARENT_VERIFIER, PARENT_TEST, parent.R3_VERIFIER, parent.R3_TEST,
             *parent.r3.SOURCE_SHA, *parent.SOURCE_SHA]
    return historical_workspace(GUIDE_COMMIT, files)


def diagnostic_r1_workspace():
    files = ["deploy/live", "scripts/diagnostic_intent_release.py", "scripts/test_diagnostic_intent_release.py",
             PARENT_VERIFIER, PARENT_TEST, parent.R3_VERIFIER, parent.R3_TEST, *R1_SOURCE_SHA]
    return historical_workspace(PARENT_COMMIT, files)


@lru_cache(maxsize=1)
def verified_parent():
    parent.git("merge-base", "--is-ancestor", GUIDE_COMMIT, PARENT_COMMIT)
    for rel in (PARENT_VERIFIER, parent.R3_VERIFIER):
        require((ROOT / rel).read_bytes() == parent.git("show", f"{PARENT_COMMIT}:{rel}"),
                "historical verifier changed " + rel)
    parent.git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    raw = parent.git("show", f"{PARENT_COMMIT}:deploy/live/_release.json")
    require(sha(raw) == PARENT_SHA, "diagnostic R1 manifest digest")
    previous = json.loads(raw)
    require(previous["parent_manifest_sha256"] == parent.MANIFEST_SHA and
            previous["release_id"] == previous["patch_id"] == "AISL_DIAGNOSTIC_INTENT_R1_20261121",
            "diagnostic R1 identity")
    return previous


def source_sha(rel):
    actual = sha((ROOT / rel).read_bytes())
    require(actual == SOURCE_SHA[rel], "source " + rel)
    return actual


def static_main_sha(rel):
    verify()
    parts = re.findall(rb'<main id="main".*?</main>', (LIVE / rel).read_bytes(), re.S)
    require(len(parts) == 1, "single main " + rel)
    return sha(parts[0])


def restore_parent_link(rel, new):
    """Restore the exact parent CTA and, on the largest page, its two optional EOF tags."""
    en = rel == "en.html" or rel.startswith("en/")
    pricing = rel.split("/")[-1] == "pricing.html"
    start = "/en/start" if en else "/start"
    label = ("Book diagnostic →" if pricing else "Discuss diagnostic →") if en else "Обсудить диагностику →"
    old = start if pricing else start + "#application-form"
    url = start + "?program=diagnostic#application-form"
    anchor_end = ('">' + label + "</a>").encode()
    exact = ('href="' + url).encode() + anchor_end
    require(new.count(exact) == 1, "one localized diagnostic link " + rel)
    restored = new.replace(exact, ('href="' + old).encode() + anchor_end, 1)
    if rel == "business.html":
        # Keep the published cold-load transfer budget. Only these HTML5 optional
        # closing tags are omitted at EOF; the document tree and scripts are identical.
        require(restored.endswith(b"</script>\n"), "business document ending")
        restored = restored[:-1] + b"</body></html>\n"
    return restored


def verify(*, manifest_override=None, file_overrides=None, source_overrides=None):
    raw = (LIVE / "_release.json").read_bytes() if manifest_override is None else manifest_override
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    manifest = json.loads(raw)
    previous = verified_parent()
    require(manifest["release_id"] == manifest["patch_id"] == RELEASE_ID and
            manifest["parent_manifest_sha256"] == PARENT_SHA and
            manifest["schema"] == previous["schema"], "manifest identity")
    before = {r["path"]: r for r in previous["files"]}
    rows = {r["path"]: r for r in manifest["files"]}
    require(rows.keys() == before.keys() and len(rows) == len(manifest["files"]) ==
            manifest["file_count"] == 112, "112 inherited assets")
    require({p for p in rows if rows[p] != before[p]} == CHANGED, "exact static delta")
    require({p.relative_to(LIVE).as_posix() for p in LIVE.rglob("*") if p.is_file()}
            == set(rows) | {"_release.json"}, "on-disk inventory")
    overrides = file_overrides or {}
    require(set(overrides) <= set(rows), "unknown file")
    for rel, row in rows.items():
        path = LIVE / rel
        require(not path.is_symlink(), "symlink " + rel)
        data = overrides[rel] if rel in overrides else path.read_bytes()
        require(len(data) == row["size"] and sha(data) == row["sha256"], "static byte " + rel)
        if rel in START_PAGES:
            en = rel == "en/start.html"
            href, label = ("/start", "RU") if en else ("/en/start", "EN")
            original = f'<a class="workshopUtility" href="{href}">{label}</a>'.encode()
            tagged = original.replace(b'>', b' referrerpolicy="no-referrer">', 1)
            require(data.count(tagged) == 1 and sha(data.replace(tagged, original, 1)) == before[rel]["sha256"],
                    "only the language link referrer policy changed " + rel)
        elif rel == RUNTIME:
            require(data == (ROOT / "public" / RUNTIME).read_bytes(), "public/static runtime parity")
    listing = "".join(f"{p}\t{r['size']}\t{r['sha256']}\n" for p, r in sorted(rows.items()))
    require(sha(listing.encode()) == manifest["payload_sha256"] == PAYLOAD_SHA, "aggregate payload")
    overrides = source_overrides or {}
    require(set(overrides) <= set(SOURCE_SHA), "unknown source")
    for rel, expected in SOURCE_SHA.items():
        if rel in overrides:
            require(sha(overrides[rel]) == expected, "source " + rel)
        else:
            source_sha(rel)
    return manifest


if __name__ == "__main__":
    print(verify()["release_id"] + ": 18 diagnostic links, 112 sealed assets")
