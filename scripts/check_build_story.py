#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
checks = 0

build_surfaces = [
    ("app/build/page.tsx", False, "source RU"),
    ("app/en/build/page.tsx", True, "source EN"),
    ("deploy/live/build.html", False, "static RU"),
    ("deploy/live/en/build.html", True, "static EN"),
]
common = [
    "BUILD STORY / OPEN PROVENANCE",
    "R8",
    "R24",
    "R31",
    "R38",
    "R49",
    "R60",
    "R65",
    "R66",
    "R68",
    "TRANSFER",
    "CHATGPT",
    "WEB RESEARCH",
    "LOCAL TEST STACK",
    "GIT / BUNDLES",
    "VERCEL",
    "HUMAN REVIEW",
    "STATIC JS BROKE",
    "METADATA DRIFT",
    "WRAPPER CORRUPTED",
    "SANDBOX DISAPPEARED",
    "DEPLOYMENT BLOCKED",
    "/_release.json",
]
for rel, en, label in build_surfaces:
    text = (ROOT / rel).read_text(encoding="utf-8")
    for marker in common:
        checks += 1
        if marker not in text:
            errors.append(f"{label}: missing {marker}")
    locale_markers = (
        ["AI did", "Human owned", "We can govern an AI build."]
        if en
        else ["AI did", "Human owned", "Мы умеем управлять AI-сборкой."]
    )
    for marker in locale_markers:
        checks += 1
        if marker not in text:
            errors.append(f"{label}: missing {marker}")
    for forbidden in [
        "client revenue guaranteed",
        "guaranteed ROI",
        "Manus used",
        "Antigravity used",
    ]:
        checks += 1
        if forbidden.casefold() in text.casefold():
            errors.append(f"{label}: forbidden unsupported claim {forbidden}")

mounts = {
    "app/page.tsx": '<R77CommercialHome locale="ru" />',
    "app/en/page.tsx": '<R77CommercialHome locale="en" />',
}
for rel, marker in mounts.items():
    checks += 1
    if marker not in (ROOT / rel).read_text(encoding="utf-8"):
        errors.append(f"{rel}: R77 home mount missing")

home_component = (ROOT / "components/R77CommercialHome.tsx").read_text(encoding="utf-8")
for marker in ['p("/proof")', "Открыть Proof Lab →", "Open Proof Lab →"]:
    checks += 1
    if marker not in home_component:
        errors.append(f"components/R77CommercialHome.tsx: missing proof route {marker!r}")

proof_discovery = {
    "app/proof/page.tsx": ["/build", "Build Log", "PROVENANCE"],
    "app/en/proof/page.tsx": ["/en/build", "Build Log", "PROVENANCE"],
    "deploy/live/proof.html": ["/build", "Build Log", "PROVENANCE"],
    "deploy/live/en/proof.html": ["/en/build", "Build Log", "PROVENANCE"],
}
for rel, markers in proof_discovery.items():
    text = (ROOT / rel).read_text(encoding="utf-8")
    for marker in markers:
        checks += 1
        if marker not in text:
            errors.append(f"{rel}: missing Build Log discovery {marker!r}")

lab_command = (ROOT / "components/LabCommand.tsx").read_text(encoding="utf-8")
for marker in ["Build Log", "/build", "/en/build", "PROVENANCE"]:
    checks += 1
    if marker not in lab_command:
        errors.append(f"components/LabCommand.tsx: missing {marker!r}")

static_command = (ROOT / "deploy/live/lab-command.js").read_text(encoding="utf-8")
for marker in ["Build Log", "b+'/build'", "PROVENANCE"]:
    checks += 1
    if marker not in static_command:
        errors.append(f"deploy/live/lab-command.js: missing {marker!r}")

print(
    f"build_story_checks={checks} build_surfaces={len(build_surfaces)} "
    "discovery_surfaces=9"
)
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("BUILD_STORY_PROVENANCE_PASS")
