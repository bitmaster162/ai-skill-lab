# AI Skill Lab R18 Readiness

## Baseline

- R17 HEAD: `3c39c3dd4c12281ca63375f2b2539c45aff6fff4`
- R17 tree: `3d837f3ff29f95d8eb7636313e3690b9b4610970`

## Scope

- Added dependency-free `scripts/verify_live_static.py` for byte-level live deployment readback.
- The verifier maps static `.html` files to clean URLs, compares live response bytes to local release bytes, checks a 404 sentinel, and can validate the expected security headers.
- Optional release-id checking supports R17+ `_release.json` fingerprints without requiring it for the exact R9 artifact.

## Self-test

R17 current static release was served through a local clean-URL HTTP fixture mirroring the relevant Vercel behavior:
- publicly addressable files checked: **41**;
- byte mismatches: **0**;
- security-header mismatches: **0**;
- 404 sentinel: **PASS**;
- result: `LIVE_STATIC_READBACK_PASS`.

The exact preserved R9 Vercel artifact `/mnt/data/AI_SKILL_LAB_R9_VERCEL_READY.zip` was independently extracted and checked through the same verifier:
- ZIP entries: **38**;
- publicly addressable files checked: **36**;
- byte mismatches: **0**;
- security-header mismatches: **0**;
- 404 sentinel: **PASS**;
- result: `LIVE_STATIC_READBACK_PASS`.

## Release boundary

R18 is post-R9 tooling only. It does not change GitHub PR #1, `main`, the exact R9 deployment payload, Vercel production, billing, domains or DNS.
