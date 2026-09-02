#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    ("static_release", ["python", "scripts/check_static_release.py"]),
    ("search_metadata", ["python", "scripts/check_search_metadata.py"]),
    ("llms_txt", ["python", "scripts/check_llms_txt.py"]),
    ("structured_data", ["python", "scripts/check_structured_data.py"]),
    ("security_headers", ["python", "scripts/check_security_headers.py"]),
    ("static_performance", ["python", "scripts/check_static_performance.py"]),
    ("transfer_performance", ["node", "scripts/check_transfer_performance.mjs"]),
    ("contrast_tokens", ["python", "scripts/check_contrast_tokens.py"]),
    ("motion_policy", ["python", "scripts/check_motion_policy.py"]),
    ("static_accessibility", ["python", "scripts/check_static_accessibility.py"]),
    ("attention_hierarchy", ["python", "scripts/check_attention_hierarchy.py"]),
    ("client_privacy", ["python", "scripts/check_client_privacy.py"]),
    ("inline_scripts", ["python", "scripts/check_inline_scripts.py"]),
    ("matcher_runtime", ["node", "scripts/check_matcher_runtime.mjs"]),
    ("start_runtime", ["node", "scripts/check_start_runtime.mjs"]),
    ("commercial_parity", ["python", "scripts/check_commercial_parity.py"]),
    ("contact_funnel", ["python", "scripts/check_contact_funnel.py"]),
    ("cta_semantics", ["python", "scripts/check_cta_semantics.py"]),
    ("studio_offer", ["python", "scripts/check_studio_offer.py"]),
    ("build_story", ["python", "scripts/check_build_story.py"]),
    ("preflight_safety", ["python", "scripts/check_preflight_safety.py"]),
    ("live_verifier_safety", ["python", "scripts/check_live_verifier_safety.py"]),
    ("faq_parity", ["python", "scripts/check_faq_parity.py"]),
    ("parent_route_parity", ["python", "scripts/check_parent_route_parity.py"]),
    ("brief_compiler", ["python", "scripts/check_brief_compiler.py"]),
    ("brief_compiler_runtime", ["node", "scripts/check_brief_compiler_runtime.mjs"]),
    ("business_decision_gate", ["python", "scripts/check_business_decision_gate.py"]),
    ("trust_route_parity", ["python", "scripts/check_trust_route_parity.py"]),
    ("proof_route", ["python", "scripts/check_proof_route.py"]),
    ("youth_route_parity", ["python", "scripts/check_youth_route_parity.py"]),
    ("youth_policy_freshness", ["python", "scripts/check_youth_policy_freshness.py"]),
    ("navigation_parity", ["python", "scripts/check_navigation_parity.py"]),
    ("lab_command", ["python", "scripts/check_lab_command.py"]),
    ("lab_discoverability", ["python", "scripts/check_lab_discoverability.py"]),
    ("project_studio", ["python", "scripts/check_project_studio.py"]),
    ("project_studio_runtime", ["node", "scripts/check_project_studio_runtime.mjs"]),
    ("pilot_simulator", ["python", "scripts/check_pilot_simulator.py"]),
    ("pilot_simulator_runtime", ["node", "scripts/check_pilot_simulator_runtime.mjs"]),
    ("business_calculator", ["node", "scripts/check_r70_business_calculator.mjs"]),
    ("curriculum_package_mapping", ["python", "scripts/check_curriculum_package_mapping.py"]),
    ("session_scope", ["python", "scripts/check_session_scope.py"]),
    ("proof_runtime", ["node", "scripts/check_proof_runtime.mjs"]),
    ("skill_graph", ["python", "scripts/check_skill_graph.py"]),
    ("skill_graph_runtime", ["node", "scripts/check_skill_graph_runtime.mjs"]),
    ("system_challenge", ["python", "scripts/check_system_challenge.py"]),
    ("system_challenge_runtime", ["node", "scripts/check_system_challenge_runtime.mjs"]),
    ("lab_hub", ["python", "scripts/check_lab_hub.py"]),
    ("lab_command_runtime", ["node", "scripts/check_lab_command_runtime.mjs"]),
]


def run(name: str, cmd: list[str]) -> dict[str, object]:
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"[{name}] {status}")
    if output:
        print(output)
    return {
        "name": name,
        "status": status,
        "returncode": result.returncode,
        "output": output[-8000:],
    }


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the repository's read-only release QA without building or deploying."
    )
    parser.add_argument("--release", required=True, help="Receipt label only; no files are written.")
    args = parser.parse_args()

    gates = []
    for name, cmd in CHECKS:
        gate = run(name, cmd)
        gates.append(gate)
        if gate["status"] == "FAIL":
            break

    if all(gate["status"] == "PASS" for gate in gates):
        gates.append(run("git_diff_check", ["git", "diff", "--check"]))

    status = "PASS" if all(gate["status"] == "PASS" for gate in gates) else "FAIL"
    receipt = {
        "schema": "ai-skill-lab.preflight.v2",
        "release": args.release,
        "status": status,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git": {
            "head": git("rev-parse", "HEAD"),
            "tree": git("rev-parse", "HEAD^{tree}"),
            "branch": git("branch", "--show-current"),
        },
        "gates": gates,
    }
    print("PREFLIGHT_RECEIPT=" + json.dumps(receipt, ensure_ascii=False, separators=(",", ":")))
    print(f"RELEASE_PREFLIGHT_{status} release={args.release} gates={len(gates)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
