"""Exact SITE-A1/A2 performance successor; no changes to historical budgets."""
import hashlib
import json
from pathlib import Path

MANIFEST_SHA = "d03a2e227bae748dfb03d4d35bf2b619c500e8d73802ab60e58c1fa221914606"
ADMISSION_SHA = "4ff3e62bcacc46aa299e7225a32d765a537bd936e8b6aa3232e14994121283ea"
PAYLOAD_SHA = "cbac82a237c62c416f2ef6163ac2c276a3d2674283626df9d3f2988f3effd324"
PATCH = "SITE_A1_A2_R2_20261026_DRAFT_REVIEW"
EXACT_NON_FONT_BYTES = 1249775

def approved(manifest_raw: bytes, admission_raw: bytes, measured_nonfont: int) -> int:
    digest = lambda data: hashlib.sha256(data).hexdigest()
    if digest(manifest_raw) != MANIFEST_SHA:
        raise ValueError("SITE_A2_PERFORMANCE_DENY manifest_SHA")
    if digest(admission_raw) != ADMISSION_SHA:
        raise ValueError("SITE_A2_PERFORMANCE_DENY admission_SHA")
    manifest, admission = json.loads(manifest_raw), json.loads(admission_raw)
    if (manifest.get("patch_id") != PATCH
        or manifest.get("payload_sha256") != PAYLOAD_SHA
        or manifest.get("file_count") != 108
        or admission.get("candidate_manifest_sha256") != MANIFEST_SHA
        or admission.get("candidate_payload_sha256") != PAYLOAD_SHA):
        raise ValueError("SITE_A2_PERFORMANCE_DENY identity")
    rows = manifest["files"]
    expected = sum(item["size"] for item in rows if not item["path"].endswith(".woff2"))
    if expected != EXACT_NON_FONT_BYTES or measured_nonfont != EXACT_NON_FONT_BYTES:
        raise ValueError("SITE_A2_PERFORMANCE_DENY measured_nonfont")
    return EXACT_NON_FONT_BYTES

def verify_live(root: Path, measured_nonfont: int) -> int:
    manifest = (root / "deploy/live/_release.json").read_bytes()
    admission = (root / "data/SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json").read_bytes()
    return approved(manifest, admission, measured_nonfont)
