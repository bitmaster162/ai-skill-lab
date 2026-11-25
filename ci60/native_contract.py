"""Run the unmodified Git policy CLI against two physical releases. No notifier entry point."""
import argparse
import ast
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree
from zipfile import ZipFile


BASE = "63fa9d3103e951edc3cdd801a51b0954bcb5a3fa"
BASE_LIVE_TREE = "ef41b3e155771a601b6c8c8e893f81ad15c1a11e"
BASE_MANIFEST = "3b762726614a3a0cf292abf23501be4f68d49df857f72bed26065e6515103c81"
ZIP_SHA = "a679d18882b161a12afd410369e68f042e893153198146d03696f5741f32937b"
MANIFEST = "01b68a85993c20f34614816df735e33af3c0636f4a787386a037fa453e671926"
PAYLOAD = "9b5e13d9441e8716cd9306e4ab10d77c35ddfe303b17bb1aba70997624f26425"
ORIGIN = "https://aiskillab.work"
KEY_FILE = "98ac1c70-f355-43f0-84f5-57cbf4c68e18.txt"
CONTRACT = "scripts/check_indexnow.py"
TEST = "scripts/test_guide_route_admission.py"
HELPER = "scripts/guide_route_admission.py"
POLICY_SHA = "493eb9cbe3440c36e33340589f05cf410dc510cb"
SCRIPTS_TREE = "44d9c89af5a43454f716e4c433722a6b62723edc"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0",
             "GIT_ALLOW_PROTOCOL": "file", "GIT_NO_REPLACE_OBJECTS": "1"},
        timeout=70,
    )


def checked_path(name):
    path = PurePosixPath(name)
    need(name == path.as_posix() and path.parts and not path.is_absolute()
         and ".." not in path.parts and "\\" not in name and ":" not in name, "invalid path " + name)
    return path


def git_files(repo, rev, *paths):
    """Read the actual blobs. Cross-check Git archive contents against their tree entries."""
    listing = git(repo, "ls-tree", "-rz", rev, "--", *paths)
    expected = {}
    for record in listing.split(b"\0"):
        if record:
            meta, name = record.decode().split("\t", 1)
            mode, kind, oid = meta.split()
            need(kind == "blob" and mode in ("100644", "100755"), "nonregular " + name)
            expected[name] = oid
    with ZipFile(BytesIO(git(repo, "archive", "--format=zip", rev, *paths))) as archive:
        data = {i.filename: archive.read(i) for i in archive.infolist() if not i.is_dir()}
    need(set(data) == set(expected), "Git archive member set changed")
    for name, raw in data.items():
        header = f"blob {len(raw)}\0".encode()
        need(hashlib.sha1(header + raw).hexdigest() == expected[name], "Git blob bytes changed " + name)
    return data


def target_files(path):
    raw = path.read_bytes()
    need(len(raw) == 685589 and sha(raw) == ZIP_SHA, "wrong physical ZIP")
    with ZipFile(BytesIO(raw)) as archive:
        names = archive.namelist()
        need(len(names) == len({n.casefold() for n in names}) == 119
             and archive.testzip() is None, "ZIP CRC, count or duplicate")
        return {name: archive.read(name) for name in names}


def notifier_usage(source):
    """Check which notifier functions the exact contract source can reach."""
    checker = ast.parse(source[CONTRACT])
    notifier = ast.parse(source["scripts/indexnow_notify.py"])
    entries = {c.func.attr for c in ast.walk(checker) if isinstance(c, ast.Call)
               and isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name)
               and c.func.value.id == "mod"}
    need(entries == {"sitemap_urls", "urls_for_changes"}, "unexpected notifier calls in contract")
    functions = {node.name: node for node in notifier.body if isinstance(node, ast.FunctionDef)}
    remaining, visited = list(entries), set()
    while remaining:
        name = remaining.pop()
        if name in visited:
            continue
        visited.add(name)
        calls = [n.func for n in ast.walk(functions[name]) if isinstance(n, ast.Call)]
        remaining.extend(c.id for c in calls if isinstance(c, ast.Name) and c.id in functions)
    need(visited == entries | {"route_url_from_html"}, "unexpected reachable notifier function")
    need(isinstance(notifier.body[-1], ast.If)
         and ast.unparse(notifier.body[-1].test) == "__name__ == '__main__'", "notifier CLI guard changed")
    return {"contract_notifier_calls": sorted(entries), "reachable_notifier_functions": sorted(visited)}


def materialize(root, files):
    for name, data in files.items():
        dest = root / checked_path(name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as fresh:
            fresh.write(data)


def inspect(live, manifest_sha, count, routes):
    files = {}
    for path in live.rglob("*"):
        need(not path.is_symlink(), "unexpected symlink in positive input")
        if path.is_file():
            files[path.relative_to(live).as_posix()] = path.read_bytes()
    raw = files.pop("_release.json")
    need(sha(raw) == manifest_sha, "wrong physical manifest")
    manifest = json.loads(raw)
    entries = [{"path": n, "size": len(b), "sha256": sha(b)} for n, b in sorted(files.items())]
    need(manifest["file_count"] == len(entries) == count and
         sorted(manifest["files"], key=lambda e: e["path"]) == entries, "physical file/index mismatch")
    payload = sha("".join(f"{e['path']}\t{e['size']}\t{e['sha256']}\n" for e in entries).encode())
    need(payload == manifest["payload_sha256"], "physical payload digest")
    if count == 118:
        need(payload == PAYLOAD and manifest["release_id"] == "AISL_R2_NOJS_P2P3_LOCAL_REVIEW_" + PAYLOAD
             and manifest["parent_manifest_sha256"] == "767936df52b6b4dc6c7420e00530afa91ddd9485ee696c3f45dc16522858855a",
             "wrong reviewed lineage")
    xml = ElementTree.fromstring(files["sitemap.xml"])
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = [element.text for element in xml.findall(ns + "url/" + ns + "loc")]
    links = re.findall(r"\]\(([^)]+)\)", files["llms.txt"].decode())
    pages = {ORIGIN + ("/" if name == "index.html" else "/" + name[:-5])
             for name in files if name.endswith(".html") and name != "404.html"}
    need(len(urls) == len(links) == len(pages) == routes and set(urls) == set(links) == pages,
         "sitemap, llms and physical HTML differ or contain duplicates")
    return {"id": manifest["release_id"], "manifest_sha256": sha(raw), "payload_sha256": payload,
            "verified_payload_files": count, "sitemap": len(urls), "llms": len(links),
            "public_html": len(pages), "route_set_sha256": sha(("\n".join(sorted(pages)) + "\n").encode()),
            "urls": sorted(pages)}


def probe(log, work, label, argv, *, markers, exit_code):
    # -E and -s keep ambient user-site/PYTHONPATH outside policy resolution.
    command = [sys.executable, "-B", "-E", "-s", "-X", "utf8", *argv]
    cp = subprocess.run(command, cwd=work, capture_output=True, timeout=90)
    output = (cp.stdout + cp.stderr).decode("utf-8", errors="replace")
    record = {"case": label, "argv": command[1:], "exit": cp.returncode,
              "stdout_sha256": sha(cp.stdout), "stderr_sha256": sha(cp.stderr),
              "expect": markers, "tail": output.strip().splitlines()[-6:]}
    log.append(record)
    record["matched"] = cp.returncode == exit_code and all(token in output for token in markers)
    need(record["matched"], f"{label}: unexpected subprocess outcome\n{output[-1600:]}")


def mutate_once(live, name, prior, changed, callback):
    target = live / name
    need((target.read_bytes() if target.exists() else None) == prior, "wrong negative input " + name)
    if changed is None:
        target.unlink()
    else:
        target.write_bytes(changed)
    try:
        callback()
    finally:
        if prior is None:
            target.unlink()
        else:
            target.write_bytes(prior)


def route_negatives(log, work, snapshot, sealed):
    """A 52 fixture reaches semantic guards; sealed 60 edits must hit the manifest first."""
    live = work / "deploy/live"
    xml = snapshot["sitemap.xml"]
    element = re.search(rb"<url><loc>https://aiskillab\.work/business</loc>.*?</url>", xml, re.S).group()
    link = b"](https://aiskillab.work/business)"
    llms = snapshot["llms.txt"]
    need(llms.count(link) == xml.count(element) == 1, "fixture route locator")
    business = "https://aiskillab.work/business"
    extra = "https://aiskillab.work/ci60-extra"
    llms_unit = [TEST, "RouteAdmissionTest.test_existing_llms_exact"]
    html_unit = [TEST, "RouteAdmissionTest.test_existing_static_html"]
    cases = [
        ("sitemap_duplicate", "sitemap.xml", xml.replace(element, element * 2), [CONTRACT], "duplicate URLs"),
        ("sitemap_missing", "sitemap.xml", xml.replace(element, b""), [CONTRACT], f"missing=['{business}']"),
        ("sitemap_extra", "sitemap.xml", xml.replace(element, element + element.replace(b"/business", b"/ci60-extra")),
         [CONTRACT], f"unexpected=['{extra}']"),
        ("llms_duplicate", "llms.txt", llms + b"\n[Fixture" + link, llms_unit, "duplicate URLs"),
        ("llms_missing", "llms.txt", llms.replace(link, b"]"), llms_unit, f"missing=['{business}']"),
        ("llms_extra", "llms.txt", llms + b"\n[Fixture](" + extra.encode() + b")", llms_unit, f"unexpected=['{extra}']"),
        ("html_missing", "business.html", None, html_unit, "missing=['/business']"),
        ("html_extra", "ci60-extra.html", b"<!doctype html><title>CI</title>", html_unit, "unexpected=['/ci60-extra']"),
    ]
    for name, rel, changed, argv, semantic in cases:
        expected = semantic
        if sealed:
            expected = "Manifest count mismatch" if rel.endswith(".html") else "Payload bytes differ from manifest"
        def run():
            probe(log, work, name, argv, markers=[expected], exit_code=1)
        mutate_once(live, rel, snapshot.get(rel), changed, run)


def seal_negatives(log, work, snapshot, report):
    live = work / "deploy/live"
    for name, rel, value, expected in (
        ("same_id_wrong_manifest", "_release.json", snapshot["_release.json"] + b"\n", "manifest digest mismatch"),
        ("payload_changed", "business.html", snapshot["business.html"] + b"\n", "Payload bytes differ from manifest"),
    ):
        mutate_once(live, rel, snapshot[rel], value,
                    lambda: probe(log, work, name, [CONTRACT], markers=[expected], exit_code=1))
    manifest = json.loads(snapshot["_release.json"])
    manifest["release_id"] = "UNKNOWN_CI_FIXTURE"
    def try_unregistered():
        probe(log, work, "unregistered_id", [CONTRACT],
              markers=["missing=[] unexpected=[", "phuket-universe", "ai-first-tasks-for-adults"], exit_code=1)
    mutate_once(live, "_release.json", snapshot["_release.json"], json.dumps(manifest).encode(), try_unregistered)
    path = live / "ci60-link.html"
    try:
        path.symlink_to("business.html")
    except OSError as exc:
        if sys.platform == "win32" and getattr(exc, "winerror", None) == 1314:
            log.append({"case": "symlink", "exit": None, "diagnostic": "WinError 1314; policy not executed"})
            report["incomplete"].append("symlink")
            return
        raise
    try:
        probe(log, work, "symlink", [CONTRACT], markers=["symlink in pilot snapshot"], exit_code=1)
    finally:
        path.unlink()


def run(args, report):
    repo = args.policy.resolve(strict=True)
    tmp = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir())).resolve(strict=True)
    need(tmp != repo and repo not in tmp.parents, "scratch inside source checkout")
    drives = [tmp] + ([Path("C:/"), Path("D:/")] if os.name == "nt" else [])
    need(all(shutil.disk_usage(p).free > 4 * 1024**3 + 32 * 1024**2 for p in drives), "scratch space threshold")
    def verify_checkout():
        need(Path(git(repo, "rev-parse", "--show-toplevel").decode().strip()).resolve() == repo
             and args.policy_sha == POLICY_SHA
             and git(repo, "rev-parse", "HEAD").decode().strip() == args.policy_sha
             and not git(repo, "status", "--porcelain=v1", "--untracked-files=all"), "wrong or dirty policy checkout")
    verify_checkout()
    need(sys.dont_write_bytecode and __debug__, "run this module with python -B and without -O")
    need(git(repo, "rev-parse", args.policy_sha + ":scripts").decode().strip() == SCRIPTS_TREE, "unreviewed scripts tree")
    need(git(repo, "rev-parse", BASE + ":deploy/live").decode().strip() == BASE_LIVE_TREE, "wrong baseline tree")
    git(repo, "merge-base", "--is-ancestor", BASE, args.policy_sha)
    source = git_files(repo, args.policy_sha, "scripts", ".github/workflows/indexnow.yml", "public/" + KEY_FILE)
    historical = {name.removeprefix("deploy/live/"): value
                  for name, value in git_files(repo, BASE, "deploy/live").items()}
    exact = target_files(args.zip)
    report.update(notifier_usage=notifier_usage(source), policy_commit=args.policy_sha, scripts_tree=SCRIPTS_TREE, zip_sha256=ZIP_SHA,
                  historical_commit=BASE, historical_live_tree=BASE_LIVE_TREE,
                  source_sha256={n: sha(source[n]) for n in
                                 (CONTRACT, TEST, HELPER, "scripts/indexnow_notify.py", ".github/workflows/indexnow.yml")})
    with tempfile.TemporaryDirectory(prefix="ci60-native-", dir=tmp) as scratch:
        for label, snapshot, pin, count, routes in (
            ("baseline52", historical, BASE_MANIFEST, 96, 52), ("candidate60", exact, MANIFEST, 118, 60),
        ):
            work = Path(scratch) / label
            live = work / "deploy/live"
            materialize(work, source)
            materialize(live, snapshot)
            physical = inspect(live, pin, count, routes)
            profile = report["profiles"][label] = {"physical": physical, "cases": []}
            logs = profile["cases"]
            probe(logs, work, "stock_indexnow", [CONTRACT], exit_code=0,
                  markers=[f"INDEXNOW_CONTRACT_CHECKS=34 sitemap_urls={routes}", "INDEXNOW_CONTRACT_PASS"])
            probe(logs, work, "stock_route_units", [TEST], exit_code=0,
                  markers=["test_existing_llms_exact", "test_existing_static_html", "Ran 16 tests", "OK"])
            route_negatives(logs, work, snapshot, routes == 60)
            if routes == 60:
                seal_negatives(logs, work, snapshot, report)
            need(inspect(live, pin, count, routes) == physical, "fixture not restored")
            need(all((work / n).read_bytes() == raw for n, raw in source.items()), "canonical input changed")
    sets = [set(report["profiles"][n]["physical"]["urls"]) for n in ("baseline52", "candidate60")]
    extra = {ORIGIN + prefix + slug for prefix in ("", "/en") for slug in
             ("/phuket-universe", "/guides/ai-first-tasks-for-adults",
              "/guides/ai-start-for-adults", "/guides/ai-pilot-for-small-business")}
    need(sets[1] == sets[0] | extra and len(sets[1] - sets[0]) == 8, "wrong eight route delta")
    report["eight_additions"] = sorted(extra)
    verify_checkout()
    need(sha(args.zip.read_bytes()) == ZIP_SHA, "input archive changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--policy-sha", required=True)
    parser.add_argument("--zip", type=Path, required=True)
    args = parser.parse_args()
    report = {"platform": sys.platform, "profiles": {}, "incomplete": []}
    try:
        run(args, report)
    except Exception as exc:
        report.update(status="FAIL", reason=f"{type(exc).__name__}: {exc}")
    else:
        report["status"] = "INCOMPLETE" if report["incomplete"] else "PASS"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
