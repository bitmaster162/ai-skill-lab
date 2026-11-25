"""Rebuild the exact public review ZIP from a clean Linux checkout and pinned recipes."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import runpy
import shlex
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory, gettempdir
from zipfile import ZipFile


SOURCE = "a1b776f59d609a99b1ca162ade3aabdf72745a1b"
PUBLISHED = "2444bd77f7616ba916c37b2b3bcba11898926be0"
EXERCISE = "0c87e0795f8e898ef06bacd4840579a1af5dac7b"
CARD = "5ca166f7a905c6887ae872fc6931b71ca76ac17a"
RECIPES = {
    "rebuild_and_verify.py": "030e794a72df7715cb5757a83fea525bd9d12e3a9c976d375a9c60cb07f7b8c7",
    "review_delta.json": "97c31d18e7f35dad28d7517189b08238069512c50021adcfc5911e0ef4945aa6",
}
ZIP_SHA = "a679d18882b161a12afd410369e68f042e893153198146d03696f5741f32937b"
MANIFEST_SHA = "01b68a85993c20f34614816df735e33af3c0636f4a787386a037fa453e671926"
PAYLOAD_SHA = "9b5e13d9441e8716cd9306e4ab10d77c35ddfe303b17bb1aba70997624f26425"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def inspect_zip(data):
    require(len(data) == 685589 and digest(data) == ZIP_SHA, "unexpected physical ZIP")
    with ZipFile(BytesIO(data)) as archive:
        raw = archive.read("_release.json")
        require(digest(raw) == MANIFEST_SHA, "unexpected manifest")
        manifest = json.loads(raw)
        entries = manifest["files"]
        names = [row["path"] for row in entries]
        require(len(entries) == len(set(names)) == manifest["file_count"] == 118, "payload file count")
        require(sorted(archive.namelist()) == sorted([*names, "_release.json"]), "archive entry set")
        lines = []
        for row in sorted(entries, key=lambda item: item["path"]):
            body = archive.read(row["path"])
            actual = digest(body)
            require(len(body) == row["size"] and actual == row["sha256"], "bad payload " + row["path"])
            lines.append(f"{row['path']}\t{len(body)}\t{actual}\n")
        require(digest("".join(lines).encode()) == manifest["payload_sha256"] == PAYLOAD_SHA, "payload SHA")
        print(json.dumps({"zip_sha256": ZIP_SHA, "zip_bytes": len(data), "manifest_sha256": MANIFEST_SHA,
                          "release_id": manifest["release_id"], "payload_sha256": PAYLOAD_SHA,
                          "payload_files_verified": len(entries), "zip_entries": len(archive.namelist())}), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(sys.platform == "linux" and sys.dont_write_bytecode and __debug__, "Linux python -B is required")
    source = args.source.resolve(strict=True)
    temp = Path(os.environ.get("RUNNER_TEMP", gettempdir())).resolve(strict=True)
    output_parent = args.output.parent.resolve(strict=True)
    output = output_parent / args.output.name
    require(not temp.is_relative_to(source) and not output_parent.is_relative_to(source),
            "use a temporary directory and output path outside the source checkout")
    require(not output.exists() and not output.is_symlink(), "output must be new")
    require(shutil.disk_usage(temp).free > 4 * 1024**3 + 512 * 1024**2 and
            shutil.disk_usage(output_parent).free > 4 * 1024**3 + 1024**2, "insufficient working space")
    os.environ.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", GIT_ALLOW_PROTOCOL="file",
                      GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1")

    def git(*argv):
        return subprocess.check_output(["git", "--no-optional-locks", "-C", str(source), *argv])

    require(Path(os.fsdecode(git("rev-parse", "--show-toplevel").strip())).resolve() == source, "source root")
    require(git("rev-parse", "HEAD").decode().strip() == SOURCE, "source HEAD")
    require(not git("status", "--porcelain=v1", "--untracked-files=all"), "source checkout is dirty")
    for commit in (SOURCE, PUBLISHED, EXERCISE, CARD):
        git("cat-file", "-e", commit + "^{commit}")
        print(f"source_commit={commit} tree={git('rev-parse', commit + '^{tree}').decode().strip()}", flush=True)
    here = Path(__file__).resolve().parent
    for name, expected in RECIPES.items():
        require(digest((here / name).read_bytes()) == expected, "wrong QA recipe " + name)
        print(f"recipe_sha256={expected} file={name}", flush=True)

    with TemporaryDirectory(prefix="ci60-build-", dir=temp) as scratch:
        work = Path(scratch)
        env = {**os.environ, "TMPDIR": scratch, "TEMP": scratch, "TMP": scratch}
        with ZipFile(BytesIO(git("archive", "--format=zip", PUBLISHED, "deploy/live"))) as archive:
            for member in archive.infolist():
                if member.is_dir():
                    continue
                name = PurePosixPath(member.filename)
                require(name.parts[:2] == ("deploy", "live") and ".." not in name.parts, "unexpected source member")
                path = work.joinpath(*name.parts)
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as handle:
                    handle.write(archive.read(member))

        def build(script, *arguments):
            command = [sys.executable, "-B", "-X", "utf8", "scripts/" + script, *map(str, arguments)]
            print("+ " + shlex.join(command), flush=True)
            subprocess.run(command, cwd=source, env=env, check=True)
            print("exit=0 " + script, flush=True)

        build("build_business_pilot_audience_preview.py", work / "r4", "--parent-root", work / "deploy/live")
        build("rebuild_joint_pilot_review.py", work / "r4", work / "joint")
        print("upstream_joint_fixture=PASS including test_snapshot symlink rejection", flush=True)
        build("build_business_simulator_labels_preview.py", work / "joint", work / "labels")
        # Loading under a module name leaves the old verifier's command-line entry point uncalled.
        review = runpy.run_path(str(here / "rebuild_and_verify.py"), run_name="ci60_build_recipe")["review"]
        data = review(source, work / "labels")
        inspect_zip(data)
        require(not git("status", "--porcelain=v1", "--untracked-files=all"), "source was modified")
        with output.open("xb") as handle:
            handle.write(data)
        require(digest(output.read_bytes()) == ZIP_SHA, "ZIP readback mismatch")
        print(f"written={output} readback_sha256={ZIP_SHA}", flush=True)


if __name__ == "__main__":
    main()
