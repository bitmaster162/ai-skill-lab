"""Exact R3 successor adding one contextual guide link on each of two existing pages."""
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile

import adult_analytics_release as r3

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
PARENT_COMMIT = "3b77fdf9d3a48571420ef588bbf33e72e53df71a"
PARENT_SHA = "9758df02a2c862c643cd87c5005176ff3751ca72011ffbdaacd7112588043c73"
RELEASE_ID = "AISL_ADULT_GUIDE_DONORS_R1_20261121"
MANIFEST_SHA = "b222558702afafb10849792f693b8322272461098c2385b7a3b6acf4fdbd5fc7"
PAYLOAD_SHA = "b0042500ae2b8ef56311d2c6d14807f94742a64b56ce207bd4916e4e6280b2e1"
R3_VERIFIER = "scripts/adult_analytics_release.py"
R3_TEST = "scripts/test_adult_analytics_release.py"
CHANGED = {"index.html", "en/method.html"}
SOURCE_SHA = {
    "app/(en)/en/method/page.tsx": "a62a42526466a34994792e1091ad610c4a50cd5af403158fc30c528056079358",
    "components/workshop/WorkshopHome.tsx": "c73ab8dfd80a915ce81e14831d4122f3b1fc479c206902128b2f866156401251",
    "lib/guides.ts": "ea820d13629b2ecc2707902b985a45610addc1056c58e787587485fd79c78723",
}
RU_LINK = '<a href="/guides/ai-first-tasks-for-adults"><u>первые практические задачи для взрослых</u></a>'
EN_LINK = '<a href="/en/guides/ai-first-tasks-for-adults"><u>practical AI tasks for adults</u></a>'
INSERTIONS = {
    "index.html": "<p>Если вы осваиваете ИИ для работы, попробуйте " + RU_LINK + ".</p>",
    "en/method.html": " For a first hands-on exercise, try these " + EN_LINK + ".",
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError("GUIDE_DONOR_RELEASE_DENY: " + reason)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=30)


def parent_blob(rel):
    return git("show", f"{PARENT_COMMIT}:{rel}")


def active():
    return (LIVE / "_release.json").is_file() and sha((LIVE / "_release.json").read_bytes()) == MANIFEST_SHA


@contextmanager
def parent_r3_workspace():
    """Materialize the frozen R3 evidence and run its own verifier against those exact bytes."""
    git("merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD")
    files = ["deploy/live", R3_VERIFIER, R3_TEST, *r3.SOURCE_SHA]
    archive = git("archive", "--format=tar", PARENT_COMMIT, "--", *files)
    with TemporaryDirectory(prefix="aisl-guide-donor-parent-") as temp:
        root = Path(temp)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            for member in bundle:
                if member.isdir():
                    continue
                require(member.isfile() and not Path(member.name).is_absolute()
                        and ".." not in Path(member.name).parts, "parent snapshot path")
                dest = root / member.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(bundle.extractfile(member).read())
        # The original verifier only reads git history for its own predecessor and ancestry.
        gitdir = git("rev-parse", "--absolute-git-dir").decode().strip()
        (root / ".git").write_text("gitdir: " + gitdir + "\n", encoding="utf-8")
        yield root


@lru_cache(maxsize=1)
def verify_parent_r3():
    with parent_r3_workspace() as root:
        require((root / R3_VERIFIER).read_bytes() == (ROOT / R3_VERIFIER).read_bytes(),
                "original R3 verifier changed")
        prior = (root / "deploy/live/_release.json").read_bytes()
        require(sha(prior) == PARENT_SHA == r3.MANIFEST_SHA, "R3 manifest")
        subprocess.run([sys.executable, "-B", R3_VERIFIER], cwd=root, check=True,
                       timeout=30, stdout=subprocess.DEVNULL)
        return json.loads(prior)


def old_method_source():
    rel = "app/(en)/en/method/page.tsx"
    return {rel: parent_blob(rel)}


def source_sha(rel):
    expected = SOURCE_SHA[rel] if rel in SOURCE_SHA else r3.SOURCE_SHA[rel]
    require(sha((ROOT / rel).read_bytes()) == expected, "source " + rel)
    return expected


def static_main_sha(rel):
    manifest = verify()
    row = next(r for r in manifest["files"] if r["path"] == rel)
    body = (LIVE / rel).read_bytes()
    require(sha(body) == row["sha256"], "static main document " + rel)
    parts = re.findall(rb'<main id="main".*?</main>', body, re.S)
    require(len(parts) == 1, "single static main " + rel)
    return sha(parts[0])


def verify(*, manifest_override=None, file_overrides=None, source_overrides=None):
    raw = (LIVE / "_release.json").read_bytes() if manifest_override is None else manifest_override
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    m = json.loads(raw)
    require(m["release_id"] == m["patch_id"] == RELEASE_ID and
            m["parent_manifest_sha256"] == PARENT_SHA and
            m["schema"] == "ai-skill-lab.static-release.v1", "manifest identity")
    parent = verify_parent_r3()
    before = {r["path"]: r for r in parent["files"]}
    rows = {r["path"]: r for r in m["files"]}
    require(rows.keys() == before.keys() and len(rows) == len(m["files"]) == m["file_count"] == 112,
            "exact asset inventory")
    require({p for p in rows if rows[p] != before[p]} == CHANGED, "exact two donor pages")
    require({p.relative_to(LIVE).as_posix() for p in LIVE.rglob("*") if p.is_file()}
            == set(rows) | {"_release.json"}, "on-disk inventory")
    require(set(file_overrides or {}) <= set(rows), "unknown file")
    for rel,row in rows.items():
        path = LIVE / rel
        require(not path.is_symlink(), "symlink " + rel)
        data = (file_overrides or {}).get(rel)
        if data is None:
            data = path.read_bytes()
        require(len(data) == row["size"] and sha(data) == row["sha256"], "static byte " + rel)
        if rel in CHANGED:
            insertion = INSERTIONS[rel].encode()
            require(data.count(insertion) == 1 and
                    sha(data.replace(insertion, b"", 1)) == before[rel]["sha256"],
                    "donor changed outside one localized link " + rel)
    aggregate = "".join(f"{p}\t{r['size']}\t{r['sha256']}\n" for p,r in sorted(rows.items()))
    require(sha(aggregate.encode()) == PAYLOAD_SHA == m["payload_sha256"], "aggregate payload")
    allowed_sources = r3.SOURCE_SHA.keys() | SOURCE_SHA.keys()
    require(set(source_overrides or {}) <= allowed_sources, "unknown source")
    for rel in allowed_sources:
        override = (source_overrides or {}).get(rel)
        if override is None:
            source_sha(rel)
        else:
            expected = SOURCE_SHA[rel] if rel in SOURCE_SHA else r3.SOURCE_SHA[rel]
            require(sha(override) == expected, "source " + rel)
    source_insertions = {
        "components/workshop/WorkshopHome.tsx": "          {!en && " +
            INSERTIONS["index.html"].replace("<a ", "<Link ").replace("</a>", "</Link>") + "}\n",
        "app/(en)/en/method/page.tsx": INSERTIONS["en/method.html"].replace("<a ", "<Link ").replace("</a>", "</Link>"),
    }
    for rel,text in source_insertions.items():
        source = (ROOT / rel).read_bytes()
        insertion = text.encode()
        require(source.count(insertion) == 1 and source.replace(insertion, b"", 1) == parent_blob(rel),
                "source changed outside one localized link " + rel)
    return m


if __name__ == "__main__":
    print(verify()["release_id"] + " two contextual links; frozen R3 verified")
