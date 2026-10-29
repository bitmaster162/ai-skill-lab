"""Exact SITE-A1/A2 performance successor; no changes to historical budgets."""
import hashlib
import json
from pathlib import Path

MANIFEST_SHA = "79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889"
ADMISSION_SHA = "fb4a04354f1a99a2d2d0cc7b5364403b2b520406660cdeb9d4ce3eaf865c7034"
PAYLOAD_SHA = "9c5bcc257f49e53172abddd1b9f366e560adbbd00f269950cc408c555536efe3"
PATCH = "SITE_A1_A2_R2_20261026_DRAFT_REVIEW"
EXACT_NON_FONT_BYTES = 1249771

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
