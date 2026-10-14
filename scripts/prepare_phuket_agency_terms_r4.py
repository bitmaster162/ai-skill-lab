#!/usr/bin/env python3
"""Create-only LOCAL R4 preview from immutable R3 and source-report pilot copy.

R3 deploy/live and its manifest are never written. R4 needs separate release
integration and external approval before it can replace R3 in a remote PR.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = "17c751146ed1abdb2526b736e1153cdbb34188b9"
BASE_TREE = "692400cae0ea8f7e4ceeff4453890eddb018e0c9"
BASE_MANIFEST = "8200834001cbecdfae4cad7976886730561c138ae1d61e9340f984d5ddac4cf1"
BASE_PAYLOAD = "40606d00063d1ec99f495bf3623f8a8ddba23bc04298c530cf6cd97f92965c10"
REPORT_SHA = "926336a8df1baa55d89de11bcbf96b87ebcf70acbf03db6a228a34aece056770"
EXCERPT_SHA = {"ru": "42fb14aa81ae1aeae09074c63fce5a74ed8a11fcc88f9a7f8f0b775e6049f8bc",
               "en": "efa71cfcb5c1b4e1d9196250cdf13040eb3a1ed2b386b82f220c4ad7a9f93803"}
RELEASE = "PHUKET_UNIVERSE_U1_AGENCY_TERMS_R4_20261014"
OUT = ROOT / "deploy/preview" / RELEASE
BRANCH = "agent/phuket-universe-agency-terms-r4-local-r1"
COPY_PATH = ROOT / "data/phuket_universe_agency_pilot_terms_r1.json"
CSS_PATH = ROOT / "app/phuket-universe-agency-terms.css"
ROUTES = {"ru": "/phuket-universe", "en": "/en/phuket-universe"}
MARKER = '<a class="pu-s101" href="mailto:robert@aiskillab.work?subject='
BLOCK_MARKER = 'data-agency-terms-version="pilot-r1"'


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(*args: str) -> bytes:
    p = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, timeout=40)
    need(p.returncode == 0, "Git verification failed: " + p.stderr.decode("utf-8", "replace")[-600:])
    return p.stdout


def copy_data() -> dict:
    data = json.loads(COPY_PATH.read_bytes())
    need(data.get("schema") == "phuket-universe.agency-pilot-copy.v1" and data.get("version") == "pilot-r1", "Copy version drift")
    need(data.get("source", {}).get("sha256") == REPORT_SHA, "Report provenance drift")
    need(data.get("authority") == {"publish": False, "deploy": False, "legal_review_completed": False, "agency_consent_obtained": False}, "Copy authority drift")
    for locale in ROUTES:
        value = data[locale]
        need(len(value["paragraphs"]) == 3 and all(isinstance(t, str) and t for t in value["paragraphs"]), "Missing source paragraphs")
        need(sha("\n\n".join(value["paragraphs"]).encode("utf-8")) == EXCERPT_SHA[locale], "Public copy differs from report excerpt")
    return data


def add_terms(markup: str, locale: str, data: dict | None = None) -> str:
    need(locale in ROUTES, "Unknown terms locale")
    data = copy_data() if data is None else data
    start = markup.find('id="agencies"')
    end = markup.find("</section>", start)
    point = markup.find(MARKER)
    need(start >= 0 and end > start and start < point < end and markup.count(MARKER) == 1
         and BLOCK_MARKER not in markup, "Agency boundary drift or duplicate terms")
    value = data[locale]
    block = ('<details class="pu-agency-terms" id="agency-pilot-terms" ' + BLOCK_MARKER + '>'
             + '<summary>' + html.escape(value["summary"], quote=True) + '</summary><div class="pu-agency-terms-body">'
             + ''.join('<p>' + html.escape(p, quote=True) + '</p>' for p in value["paragraphs"])
             + '</div></details>\n')
    return markup[:point] + block + markup[point:]


def verify_payload(files: dict[str, bytes]) -> dict:
    m = json.loads(files["_release.json"])
    payload = {n: b for n, b in files.items() if n != "_release.json"}
    records = m["files"]
    need(len(records) == len({r['path'] for r in records}) == len(payload) == m['file_count'], "Manifest duplicate/missing entries")
    actual = [{"path": n, "sha256": sha(b), "size": len(b)} for n, b in sorted(payload.items())]
    need(sorted(records, key=lambda r: r['path']) == actual, "Payload bytes differ from manifest")
    digest = sha(''.join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in actual).encode("utf-8"))
    need(digest == m['payload_sha256'], "Payload digest mismatch")
    return m


def r3_payload() -> dict[str, bytes]:
    need(git("rev-parse", BASE + "^{tree}").decode().strip() == BASE_TREE, "Wrong R3 base tree")
    result = {}
    with tarfile.open(fileobj=io.BytesIO(git("archive", "--format=tar", BASE, "deploy/live"))) as archive:
        for item in archive:
            if item.isdir():
                continue
            need(item.isfile() and item.name.startswith("deploy/live/"), "Unexpected R3 archive entry")
            name = item.name[len("deploy/live/"):]
            need(name and not PurePosixPath(name).is_absolute() and ".." not in PurePosixPath(name).parts and "\\" not in name and name not in result, "Unsafe R3 path")
            stream = archive.extractfile(item)
            need(stream is not None, "Unreadable R3 archive entry")
            result[name] = stream.read()
    need(sha(result["_release.json"]) == BASE_MANIFEST, "R3 manifest drift")
    m = verify_payload(result)
    need(m['payload_sha256'] == BASE_PAYLOAD and m['file_count'] == 104, "R3 payload identity drift")
    return result


def render() -> tuple[dict[str, bytes], dict]:
    base = r3_payload()
    data = copy_data()
    files = base.copy()
    for locale, route in ROUTES.items():
        key = route.lstrip('/') + '.html'
        files[key] = add_terms(base[key].decode('utf-8'), locale, data).encode('utf-8')
    files['phuket-universe.css'] = base['phuket-universe.css'] + CSS_PATH.read_bytes()
    changed = {n for n in base if base[n] != files[n]}
    need(changed == {'phuket-universe.html', 'en/phuket-universe.html', 'phuket-universe.css'}, 'R4 content delta drift')
    payload = {n: b for n, b in files.items() if n != '_release.json'}
    rows = [{"path": n, "size": len(b), "sha256": sha(b)} for n, b in sorted(payload.items())]
    digest = sha(''.join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows).encode('utf-8'))
    m = {"schema": "ai-skill-lab.static-release.v1", "release_id": RELEASE, "file_count": len(rows), "payload_sha256": digest, "files": rows}
    files['_release.json'] = (json.dumps(m, sort_keys=True, indent=2) + '\n').encode('utf-8')
    verify_payload(files)
    return files, {"release_id": RELEASE, "parent_commit": BASE, "parent_manifest_sha256": BASE_MANIFEST,
        "manifest_sha256": sha(files['_release.json']), "payload_sha256": digest,
        "payload_files": len(payload), "payload_bytes": sum(map(len, payload.values())),
        "r3_payload_files_unchanged": 101, "changed_payload_files": sorted(changed),
        "source_report_sha256": REPORT_SHA, "terms_excerpt": "verbatim RU/EN public draft",
        "source_copy_sha256": sha(COPY_PATH.read_bytes()), "remote_push": False,
        "deploy": False, "production": False, "release_integration": "NOT_PERFORMED",
        "legal_review_completed": False}


def write_candidate(files: dict[str, bytes]) -> None:
    need(git('branch', '--show-current').decode().strip() == BRANCH, 'Wrong local branch')
    need(not git('status', '--porcelain=v1').strip(), 'Commit and clean source before seal')
    need(not OUT.exists() and OUT.parent.resolve().is_relative_to(ROOT.resolve()), 'Existing/unsafe R4 target')
    OUT.mkdir(parents=True, exist_ok=False)
    for name in sorted(files, key=lambda n: (n == '_release.json', n)):
        need(not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and '\\' not in name, 'Unsafe output path')
        p = OUT / name
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as stream:
            stream.write(files[name])
    observed = {p.relative_to(OUT).as_posix(): p.read_bytes() for p in OUT.rglob('*') if p.is_file()}
    need(observed == files, 'Write mismatch; STOP without retry')
    print('R4_CANDIDATE_WRITTEN', OUT, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-candidate', action='store_true')
    args = parser.parse_args()
    files, stats = render()
    if args.write_candidate:
        write_candidate(files)
    print(json.dumps(stats, ensure_ascii=True, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
