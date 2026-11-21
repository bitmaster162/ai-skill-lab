# SEO method R1 — static release CANDIDATE (review only)

Status: **DRAFT / PREPARED_NOT_ADMITTED**, 2026-11-21.
Not approved for merge, production deployment, IndexNow or live publication.
Source: AI Skill Lab PR #241, head `8f122d15e7a88b4ce926cc0f27f122cfbd6c1638`.
Parent static release manifest SHA-256: `79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889`.
Candidate manifest SHA-256: `ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0`.
Candidate payload SHA-256: `f2678f7fb3ff5381e421795f83bd8115fa7365613806443cfeea9802efacdf88`.

- `review.zip`: 108 public static payload files plus candidate `_release.json`.
- `review.sha256`: separate SHA-256 of the exact archive.
- `manifest.json`: complete new 108-file manifest with parent pointer and new patch/release IDs.
- `method.html`, `en/method.html`, `sitemap.xml`: the only three changes against the archived parent payload.
- `build_receipt.json`, `independent_validation.json`: local build and independent exact-byte verification.

Verification performed: pinned parent bytes, 108 candidate files, source checkout HEAD, no tracked source drift, exact three-file diff, Next.js-rendered main content, no additional scripts or forms, unchanged canonical and outer HTML, two sitemap lastmods. Full historical Static Release QA still FAILS at D5 until a separately approved versioned successor is integrated. This candidate must **not** be treated as the currently deployed `deploy/live` archive.
