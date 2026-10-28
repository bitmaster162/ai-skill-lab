"""Exact SITE-A1/A2 performance successor; no changes to historical budgets."""
import hashlib
import json
from pathlib import Path

MANIFEST_SHA = "f8cdc7b27aca6ea5815c8237a97acf53a5c7ef9f9db24d4ff19e6c5ae9c5ec53"
ADMISSION_SHA = "279ee064f8a93f25af5ca6b64362bd6f16d6a048a74fd611977c8585f76ff1ef"
PAYLOAD_SHA = "1393d778de86ba69b0a187f545d1aa606ef3ccf0d89f189cc0be75ec21e9fcca"
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
