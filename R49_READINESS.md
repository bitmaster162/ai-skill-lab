# AI Skill Lab R49 Readiness

Status: **LOCAL RELEASE READY / VERCEL QUOTA HOLD**

## Authority
- Branch: `agent/r49-release-builder`
- Parent release: R48 trust-route parity
- Release payload: `1e6d56fcd605a717e264fb6c2a4b89915e9809966b4c0114ca3a4f3ae483aade`

## R45–R49 delta
- R45: explicit Kids/Teens package-to-curriculum mapping for 4/6/10/12-session offers.
- R46: Parents route now covers ages 8–18 across RU/EN source + static and participates in commercial parity.
- R47: CTA labels now match their real destination; Telegram wording is reserved for actual Telegram links.
- R48: Projects/About trust content is aligned across source + static; examples remain explicitly non-testimonials/non-client claims.
- R49: deterministic release artifact builder and wrapper self-test remove manual packaging drift.

## Preflight
`python scripts/preflight_release.py --release R49`

Result: **28/28 PASS**.

Key evidence:
- 37 HTML pages / 36 public routes
- 1,152 internal links / 0 broken
- 0 forms
- 472 commercial parity checks
- 163 CTA semantics checks
- 1,405 accessibility checks
- Matcher runtime 16/16 PASS
- Start runtime 44/44 PASS
- CSP/security/privacy/performance/structured-data/search metadata PASS
- Release builder reconstructs 44/44 served files byte-for-byte
- Wrapper verifies archive SHA + size, all 45 stage file hashes, release id and payload SHA before publishing output

## External release boundary
Vercel production is still the previously verified R5 until a fresh read proves otherwise.
Last known API deployment quota: 100/100 used; reset expected 2026-08-16 17:49:21 Asia/Bangkok.
Do not issue deployment calls before reset. After reset: one R49 preview -> exact readback -> R49 production -> public readback.
