"""Exact static successor for optional adult analytics, rooted in the prior Git release."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
PARENT_COMMIT = "dbc97ca6537df48a96e8eb9273fed1f0a4e69d93"
PARENT_SHA = "ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0"
RELEASE_ID = "AISL_ADULT_GA4_OPT_IN_R3_20261121"
# Frozen release identity
MANIFEST_SHA = "9758df02a2c862c643cd87c5005176ff3751ca72011ffbdaacd7112588043c73"
PAYLOAD_SHA = "a436546681cb59eafb62b7faf8237fee7202c85cb5517cb57bd5bd1ad3db5113"
SOURCE_SHA = {
    "app/(en)/en/business/page.tsx": "961c660eca8e453076ff88cf1fdabcc01ca7c2f99a218e5702c6ec86ff1de750",
    "app/(en)/en/personal/page.tsx": "1f1d2cf6970c7866d297fd7a2dbf42c3b253d2acf1181298109039440e4f2386",
    "app/(en)/en/privacy/page.tsx": "2a731d0abda2ccfd573125afcae3012893b139a47d92d39b6c3e558a65ef8e97",
    "app/(en)/en/proof/page.tsx": "e96bd4411cdd70a094e1d832e62ac92a5170bb8f62df1a47b93248a30ecef241",
    "app/(ru)/business/page.tsx": "80bc0fc1f28a2fa79d79e89535267a6f358199c608dd46599fcf0464e3851562",
    "app/(ru)/personal/page.tsx": "5ce8d669f612f9d6bd366802366342c489b294bb155733d9d7d412930fb469e2",
    "app/(ru)/privacy/page.tsx": "b10f651c3d0b324d3f170e2d1913861c98eaa7c86cd13a98e9ff8291ddd8dc8b",
    "app/(ru)/proof/page.tsx": "af2f02e2d49a01be42d884de1333413f247256aa83b385fb910cc92bee8f457a",
    "components/AdultAnalyticsPreference.tsx": "99225a7c1a756eb6fe06739d3bf55c9d902662e7bb8264b5d4fe1a3a08e3e340",
    "lib/guides.ts": "9baa1778d79a1b3b44de9e707f1acf48065a11331dcaef88b54acbb84d9b06a0",
    "public/analytics/preferences.css": "f01b317812dfb7d66a33c9a2a71c04644aa16344bbb231b8d0c23a8fd64c15ac",
    "public/analytics/preferences.htm": "7abf4359d21644d5ee5d0e622a67fdaf3ff7fa34e0c1a47a6d873858a1df8edc",
    "public/analytics/preferences.js": "74dfa71045f4dff74ebc7773dc6a729f7008a82e3648605c1c3b1678c7708499",
    "public/analytics/restore.js": "514cb77287256018bf4f23590da4e5c431a96e2b9681e19445bb92876731a33f"
}
# End release identity
ELIGIBLE = {"business.html", "personal.html", "en/business.html", "en/personal.html"}
DISCLOSURES = {"privacy.html", "en/privacy.html", "proof.html", "en/proof.html"}
ADDITIONS = {"analytics/preferences." + ext for ext in ("htm", "css", "js")} | {"analytics/restore.js"}
CHANGED = ELIGIBLE | DISCLOSURES | {"vercel.json"} | ADDITIONS


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError("ADULT_ANALYTICS_RELEASE_DENY: " + message)


def active():
    path = LIVE / "_release.json"
    return path.is_file() and sha(path.read_bytes()) == MANIFEST_SHA


def source_sha(rel):
    """Return the reviewed source pin, after checking on-disk bytes."""
    expected = SOURCE_SHA[rel]
    require(sha((ROOT / rel).read_bytes()) == expected, "source " + rel)
    return expected


def static_main_sha(rel):
    """A main digest can only be derived from the sealed, verified document."""
    manifest = verify()
    row = next(row for row in manifest["files"] if row["path"] == rel)
    data = (LIVE / rel).read_bytes()
    require(sha(data) == row["sha256"], "static main document " + rel)
    main = re.findall(rb'<main id="main".*?</main>', data, re.S)
    require(len(main) == 1, "single static main " + rel)
    return sha(main[0])


def verify(*, manifest_override=None, file_overrides=None):
    raw = manifest_override if manifest_override is not None else (LIVE / "_release.json").read_bytes()
    require(sha(raw) == MANIFEST_SHA, "manifest digest")
    manifest = json.loads(raw)
    require(manifest["release_id"] == manifest["patch_id"] == RELEASE_ID and
            manifest["parent_manifest_sha256"] == PARENT_SHA and
            manifest["schema"] == "ai-skill-lab.static-release.v1", "manifest identity")
    subprocess.run(["git", "merge-base", "--is-ancestor", PARENT_COMMIT, "HEAD"], cwd=ROOT,
                   check=True, timeout=15, stdout=subprocess.DEVNULL)
    prior = subprocess.check_output(["git", "show", PARENT_COMMIT + ":deploy/live/_release.json"],
                                   cwd=ROOT, timeout=15)
    require(sha(prior) == PARENT_SHA, "parent manifest digest")
    old_rows = {r["path"]: r for r in json.loads(prior)["files"]}
    rows = {r["path"]: r for r in manifest["files"]}
    require(len(rows) == len(manifest["files"]) == manifest["file_count"] == 112, "asset count")
    require(rows.keys() - old_rows.keys() == ADDITIONS and not old_rows.keys() - rows.keys(),
            "successor file set")
    require({name for name in rows if rows[name] != old_rows.get(name)} == CHANGED,
            "exact successor scope")
    inventory = {p.relative_to(LIVE).as_posix() for p in LIVE.rglob("*") if p.is_file()}
    require(inventory == set(rows) | {"_release.json"}, "static inventory")
    require(set(file_overrides or {}) <= set(rows), "unknown file")
    aggregate = []
    for name, row in sorted(rows.items()):
        path = LIVE / name
        require(not path.is_symlink(), "symlink " + name)
        data = (file_overrides or {}).get(name)
        if data is None:
            data = path.read_bytes()
        require(len(data) == row["size"] and sha(data) == row["sha256"], "static byte " + name)
        if name.endswith(".html"):
            require(data.count(b'src="/analytics/preferences.htm"') == int(name in ELIGIBLE),
                    "scope " + name)
        if name in ADDITIONS:
            require(data == (ROOT / "public" / name).read_bytes(), "source/static parity " + name)
        aggregate.append(f"{name}\t{row['size']}\t{row['sha256']}\n")
    require(sha("".join(aggregate).encode()) == manifest["payload_sha256"] == PAYLOAD_SHA,
            "aggregate payload")
    for rel in SOURCE_SHA:
        source_sha(rel)
    return manifest


if __name__ == "__main__":
    evidence = verify()
    print(f"{evidence['release_id']} assets={evidence['file_count']} manifest={MANIFEST_SHA}")
