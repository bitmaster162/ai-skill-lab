"""Build the bilingual business-pilot preview from the sealed static source."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
ADAPTER = ROOT / "scripts" / "static-adapters" / "pilot-business-audience.js"
PARENT_SHA256 = "66c02d9bda23b0424330596b6e74a14576be0259d31f4e1b5a5f8ba07cb251d5"
R2_MANIFEST_SHA256 = "6c721edc6a40aa16080180db847e3ad2d18128358b62db7cce988791a693245c"
GUIDE = "guides/ai-pilot-for-small-business.html"
RUNTIME = "lead-form-runtime.js"
MANIFEST = "_release.json"


def digest(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def record(name: str, raw: bytes) -> dict:
    return {"path": name, "size": len(raw), "sha256": digest(raw)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_parent(parent_root: Path) -> tuple[dict, dict[str, bytes]]:
    raw = (parent_root / MANIFEST).read_bytes()
    require(digest(raw) == PARENT_SHA256, "unexpected parent manifest")
    parent = json.loads(raw)
    files = {}
    for row in parent["files"]:
        name = row["path"]
        contents = (parent_root / name).read_bytes()
        require(record(name, contents) == row, f"parent asset mismatch: {name}")
        files[name] = contents
    return parent, files


def article_links(raw: bytes, start: str) -> bytes:
    """Confine all replacements to the three existing links inside this article."""
    articles = list(re.finditer(rb"<article\b[^>]*>.*?</article>", raw, flags=re.DOTALL))
    require(len(articles) == 1, f"expected one pilot article: {start}")
    match = articles[0]
    article = match.group()
    base = start.encode()
    href = re.compile(rb'(<a\b[^>]*?\shref=")' + re.escape(base) + rb'(#application-form)?"')
    before = [a.group(2) for a in href.finditer(article)]
    require(before.count(None) == 2 and before.count(b"#application-form") == 1,
            f"expected two body links and one application link: {start}")
    after = href.sub(lambda a: a.group(1) + base + b'?audience=business#application-form"', article)
    return raw[:match.start()] + after + raw[match.end():]


def business_guide_link(raw: bytes, prefix: str, label: str) -> bytes:
    """Place the reviewed guide link after the four implementation steps."""
    target = f'/{prefix}guides/ai-pilot-for-small-business'
    marker = b'</section><section class="section panelSection" id="pilot-simulator">'
    require(raw.count(marker) == 1 and f'href="{target}"'.encode() not in raw,
            f"unexpected business page layout: {target}")
    link = (f'<div class="heroActions"><a class="workshopButton workshopButtonSecondary" '
            f'href="{target}">{label}</a></div>').encode()
    return raw.replace(marker, link + marker, 1)


def build_files(parent_root: Path = LIVE) -> tuple[dict[str, bytes], dict]:
    parent, files = load_parent(parent_root)
    for locale, label in (("", "Как выбрать первую задачу для ИИ-пилота"),
                          ("en/", "How to choose the first task for an AI pilot")):
        start = "/" + locale + "start"
        name = locale + GUIDE
        files[name] = article_links(files[name], start)
        business = locale + "business.html"
        files[business] = business_guide_link(files[business], locale, label)

    adapter = ADAPTER.read_bytes()
    require(bool(adapter.strip()), "empty business-audience adapter")
    files[RUNTIME] += b"\n" + adapter
    rows = [record(name, files[name]) for name in sorted(files)]
    original = {row["path"]: row for row in parent["files"]}
    changed = {row["path"] for row in rows if row != original[row["path"]]}
    require(changed == {GUIDE, "en/" + GUIDE, "business.html", "en/business.html", RUNTIME}, "unexpected preview delta")
    listing = "".join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows)
    payload = digest(listing.encode())
    release_id = "AISL_FORM_LANGUAGE_AUDIENCE_REVIEW_R3_" + payload
    manifest = dict(parent, release_id=release_id, patch_id=release_id, files=rows,
                    file_count=len(rows), parent_manifest_sha256=R2_MANIFEST_SHA256, payload_sha256=payload)
    files[MANIFEST] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    return files, manifest


def write_preview(output: Path, files: dict[str, bytes]) -> None:
    if output.exists():
        actual = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
        require(output.is_dir() and actual == files.keys(), "output already exists with a different inventory")
        for name, expected in files.items():
            require((output / name).read_bytes() == expected, f"existing output differs: {name}")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".pilot-preview-", dir=output.parent) as tmp:
        staging = Path(tmp) / "site"
        for name, contents in files.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(contents)
        staging.rename(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="separate directory for the complete static preview")
    parser.add_argument("--parent-root", type=Path, default=LIVE,
                        help="Directory containing the original 116-asset parent release")
    args = parser.parse_args()
    output = args.output.resolve()
    require(not output.is_relative_to(LIVE.resolve()), "choose an output outside deploy/live")
    files, manifest = build_files(args.parent_root)
    write_preview(output, files)
    print(json.dumps({"directory": str(output), "assets": manifest["file_count"],
                      "changed_assets_from_source": 5, "manifest_sha256": digest(files[MANIFEST]),
                      "payload_sha256": manifest["payload_sha256"]}))


if __name__ == "__main__":
    main()
