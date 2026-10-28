"""Exact SITE-A1/A2 performance successor; no changes to historical budgets."""
import hashlib
import json
from pathlib import Path

MANIFEST_SHA = "11d341f50a1ed97b4c1335f27524a2383b2db92a52a19d44a33674e4013dd727"
ADMISSION_SHA = "9102807cee2df87332543e53f83d8b645d81876d9cf6bd1ad26745df0f83eadd"
PAYLOAD_SHA = "10c21322ee0fdfecf3f841b4f286f12494325d70440b7057482ebd807f821d82"
PATCH = "SITE_A1_A2_R2_20261026_DRAFT_REVIEW"
EXACT_NON_FONT_BYTES = 1249812

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
