# AI Skill Lab R17 Readiness

## Baseline

- R16 HEAD: `e03467167114e27f1a34a1e1dbc5b2ba9ea269a0`
- R16 tree: `e8a7edd0aaf5eaaff5c7c0105f29189332043087`

## Scope

- Extended static QA to validate exact canonical URL and `ru` / `en` / `x-default` hreflang pairs on every public static route.
- Added deterministic `scripts/build_static_manifest.py`.
- Added public readback marker `deploy/live/_release.json` containing a deterministic file map and aggregate payload SHA-256; `_release.json` excludes itself from the fingerprint.
- Added `Cache-Control: no-store, max-age=0` for `/_release.json` so future deployment readback is not satisfied by stale cache.

## QA

- Static HTML pages including 404: **35**.
- Public routes: **34**.
- Internal links inspected: **722**.
- Public static forms: **0**.
- JSON-LD parse: **PASS**.
- Canonical/hreflang route parity: **PASS** for all 34 public routes.
- Sitemap exact-match: **PASS**.
- Source placeholder URLs: **0**.
- Release manifest file count: **42**.
- Release manifest payload SHA-256: `909fc2fd15d0b7c50869d340afcbdb51e0edc604a3528714372b5ce8d8d4380d`.
- Release manifest self-verification: **PASS**.
- `git diff --check`: **PASS**.

## Release boundary

R17 is local/post-R9 work. It does not change GitHub PR #1, GitHub `main`, the exact R9 Vercel artifact, or Vercel production.
