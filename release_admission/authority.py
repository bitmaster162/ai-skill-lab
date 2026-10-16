"""R4E candidate historical profile identity library (NOT independent owner trust).

This entire module is candidate-controlled. Its pinned historical profiles only
prove self-consistency relative to audited GitHub source, never merge/publish
approval. A dedicated independently controlled issuer and protected branch rule
remain absent. Unknown releases must fail closed.
"""
from __future__ import annotations
from types import MappingProxyType

BASELINE_ROUTE_SHA256 = "c0f963323acdf475e97877320d982446c3d790b95fdbebfb2e7c7d443d95cd34"
APPROVED_HISTORICAL_PINS = MappingProxyType({
    "E3_6_WORKSHOP_HERO_PANEL_R1": "82c98a646122a695b68257d763ce8e0b5488f232d69b11351cb8d5c01220e721",
    "T1_6F2_ADULT_FIRST_TASKS_R1": "601eac430fe1e341ef40329b239d169cb3ced86f0ceda7678a8e94119d250506",
})
# Literal serialized historical fixtures; not a profile directory scanned at runtime.
_ARCHIVE = MappingProxyType({
    'E3_6_WORKSHOP_HERO_PANEL_R1': b'{\n  "asset_pins": {\n    "workshop.css": {\n      "sha256": "a666815eb37b12ab643de504fd17e0a12255d25989c63b364ea5c58693a3da06",\n      "size": 41174\n    }\n  },\n  "baseline_route_set_sha256": "c0f963323acdf475e97877320d982446c3d790b95fdbebfb2e7c7d443d95cd34",\n  "expected_nonfont_bytes": 1080718,\n  "expected_payload_bytes": 1162770,\n  "file_count": 96,\n  "guide_slugs": [],\n  "html_count": 53,\n  "manifest_sha256": "3b762726614a3a0cf292abf23501be4f68d49df857f72bed26065e6515103c81",\n  "max_nonfont_bytes": 1146880,\n  "max_payload_bytes": 1228800,\n  "mode": "historical",\n  "origin": "https://aiskillab.work",\n  "payload_sha256": "cd18e15cdea7996b5164778983f413616309222fac323cc64966887ad1712bad",\n  "release_id": "E3_6_WORKSHOP_HERO_PANEL_R1",\n  "route_count": 52,\n  "schema": "ai-skill-lab.release-profile.v1",\n  "source_pins": {\n    "components/workshop/WorkshopShell.module.css": "8d85d9d61e84cc178af370b7faa840b8dd73b5318ce0eb1ccd07b63c80924109"\n  }\n}\n',
    'T1_6F2_ADULT_FIRST_TASKS_R1': b'{\n  "asset_pins": {\n    "en/guides/ai-first-tasks-for-adults.html": {\n      "sha256": "dd43b529fac595d4ac5ea2d848de54db8dd11be761bf873b109593476f2c58aa",\n      "size": 20480\n    },\n    "guides/ai-first-tasks-for-adults.html": {\n      "sha256": "f3cecb6ea3f46ab64ac3d3ab16db955ab8776d5edeb0c87b3b9b46bcaae2af91",\n      "size": 27314\n    }\n  },\n  "baseline_route_set_sha256": "c0f963323acdf475e97877320d982446c3d790b95fdbebfb2e7c7d443d95cd34",\n  "expected_nonfont_bytes": 1130043,\n  "expected_payload_bytes": 1212095,\n  "file_count": 98,\n  "guide_slugs": [\n    "ai-first-tasks-for-adults"\n  ],\n  "html_count": 55,\n  "manifest_sha256": "1c0486827cac8fceab7c2a395d3c12a47edaac56af0ecf72459cce256429e74f",\n  "max_nonfont_bytes": 1146880,\n  "max_payload_bytes": 1228800,\n  "mode": "historical",\n  "origin": "https://aiskillab.work",\n  "payload_sha256": "188c0b7c3204dd4c1366a51facafeb09421c929e58913e34c7500d9fdf2ea30e",\n  "release_id": "T1_6F2_ADULT_FIRST_TASKS_R1",\n  "route_count": 54,\n  "schema": "ai-skill-lab.release-profile.v1",\n  "source_pins": {\n    "guides/aiskillab/ai-first-tasks-for-adults.en.md": "b0bcd0a6b545d2d8d4b190e55ab9d3c76350a9a30a8e1c745fb23e04b48df671",\n    "guides/aiskillab/ai-first-tasks-for-adults.ru.md": "5c5f8d8da100a8657aeefbe5d9044462095e92db341e240a37bdebae57bba61b"\n  }\n}\n',
})

def load_archived_profile(release_id: str) -> bytes:
    if type(release_id) is not str or release_id not in APPROVED_HISTORICAL_PINS:
        raise ValueError("UNKNOWN_RELEASE_DENIED")
    return _ARCHIVE[release_id]
