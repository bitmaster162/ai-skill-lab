"""Exact static release attributing the diagnostic action on 18 existing pages."""
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
import io
import json
import re
import subprocess
import sys
import tarfile

import guide_donor_release as parent

ROOT, LIVE = parent.ROOT, parent.LIVE
sha = parent.sha
PARENT_COMMIT = "5c004dd5fb45d0621999e50e6ff2ec30b03d9e61"
PARENT_SHA = "b222558702afafb10849792f693b8322272461098c2385b7a3b6acf4fdbd5fc7"
RELEASE_ID = "AISL_DIAGNOSTIC_INTENT_R1_20261121"
MANIFEST_SHA = "78cb75d81138d54f47a37555f6eea6dff9f53f578a76779d902f0c39e97530dc"
PAYLOAD_SHA = "8a0a23c11b4977021bb8b1ef8417746e21f0aef0f49beba2aaaf88edcb55be29"

ROUTE_NAMES = ("business", "kids", "matcher", "parents", "personal", "pricing", "start", "teens")
DONOR_PAGES = {"index.html", "en.html"} | {
    prefix + name + ".html" for prefix in ("", "en/") for name in ROUTE_NAMES
}
RUNTIME = "lead-form-runtime.js"
CHANGED = DONOR_PAGES | {RUNTIME}
SOURCE_SHA = {
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
PARENT_VERIFIER = "scripts/guide_donor_release.py"
PARENT_TEST = "scripts/test_guide_donor_release.py"


def require(ok, reason):
    if not ok:
        raise ValueError("DIAGNOSTIC_INTENT_RELEASE_DENY: " + reason)


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


@contextmanager
def parent_guide_workspace():
    """Run the parent's own code and fixtures against its exact Git inventory."""
    parent.git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    files = ["deploy/live", PARENT_VERIFIER, PARENT_TEST, parent.R3_VERIFIER, parent.R3_TEST,
             *parent.r3.SOURCE_SHA.keys(), *parent.SOURCE_SHA.keys()]
    archive = parent.git("archive", "--format=tar", PARENT_COMMIT, "--", *files)
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


@lru_cache(maxsize=1)
def verified_parent():
    with parent_guide_workspace() as root:
        for script in (PARENT_VERIFIER, parent.R3_VERIFIER):
            require((ROOT / script).read_bytes() == (root / script).read_bytes(),
                    "parent verifier changed " + script)
        raw = (root / "deploy/live/_release.json").read_bytes()
        require(sha(raw) == PARENT_SHA == parent.MANIFEST_SHA, "parent manifest digest")
        subprocess.run([sys.executable, "-B", PARENT_VERIFIER], cwd=root, check=True,
                       stdout=subprocess.DEVNULL, timeout=45)
        return json.loads(raw)


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
        if rel in DONOR_PAGES:
            require(sha(restore_parent_link(rel, data)) == before[rel]["sha256"],
                    "HTML outside diagnostic href " + rel)
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
