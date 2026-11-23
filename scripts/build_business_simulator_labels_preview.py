"""Build a review-only successor for the Russian business simulator on joint R4."""
import argparse
from base64 import b64encode
from hashlib import sha256
import json
from pathlib import Path
import re

from build_business_pilot_audience_preview import MANIFEST, digest, require, write_preview
from prepare_phuket_universe_static_r1 import file_index, payload_digest
from rehearse_pilot_audience_release import JOINT_MANIFEST, ROOT, snapshot
from restored_guides_release import manifest_bytes


def build(parent: Path, output: Path) -> None:
    files = snapshot(parent, JOINT_MANIFEST)
    page = files["business.html"].decode("utf-8")
    source = (ROOT / "components/PilotSimulator.tsx").read_text(encoding="utf-8")
    ru = source.split("ru:{\n", 1)[1].split("\nen:{", 1)[0]
    scripts = re.findall(r"<script>(.*?)</script>", page, re.DOTALL)
    original, = [s for s in scripts if s.startswith("(()=>{const D=")]
    match = re.search(r"const D=(\{.*?\}),keys=", original)
    data = json.loads(match[1])
    # Keep authored static wording everywhere else. Restore the four status
    # badges from React and the first success criterion shown before JavaScript.
    for key, scenario in data.items():
        row, = [line for line in ru.splitlines() if line.startswith(key + ":{")]
        for field in (("signal", "success") if key == "knowledge" else ("signal",)):
            value = re.search(r'\b' + field + r':("(?:[^"\\]|\\.)*")', row)
            require(value is not None, f"missing source field {key}.{field}")
            scenario[field] = json.loads(value[1])
    for field in ("signal", "success"):
        require(f'id="pilot-{field}">{data["knowledge"][field]}<' in page,
                f"source and initial HTML disagree for {field}")
    # The default scenario already exists in the server-rendered DOM. Capture it
    # before the first click so returning to it restores exactly the same words.
    # Button labels are static markup; this runtime only renders scenario fields.
    del data["knowledge"]
    for scenario in data.values():
        del scenario["label"]
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    updated = original[:match.start(1)] + body + original[match.end(1):]
    hook = "buttons.forEach(b=>b.addEventListener"
    require(updated.count(hook) == 1, "unexpected simulator initialization")
    capture = ("D.knowledge={};for(const k of Object.keys(D.documents))"
               "D.knowledge[k]=document.getElementById('pilot-'+k).textContent;")
    updated = updated.replace(hook, capture + hook)
    files["business.html"] = page.replace(original, updated, 1).encode("utf-8")
    policy = files["vercel.json"]
    old_hash, new_hash = [b64encode(sha256(s.encode("utf-8")).digest()) for s in (original, updated)]
    require(policy.count(old_hash) == 3 and new_hash not in policy, "unexpected CSP pins")
    files["vercel.json"] = policy.replace(old_hash, new_hash)
    rows = file_index(files)
    payload = payload_digest(rows)
    version = "AISL_BUSINESS_SIMULATOR_LABELS_R2_REVIEW_" + payload
    files[MANIFEST] = manifest_bytes({"schema": "ai-skill-lab.static-release.v1", "files": rows,
        "file_count": len(rows), "release_id": version, "patch_id": version,
        "parent_manifest_sha256": JOINT_MANIFEST, "payload_sha256": payload})
    write_preview(output, files)
    print(digest(files[MANIFEST]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.parent.resolve(), args.output.resolve())
