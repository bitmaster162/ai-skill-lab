# AI Skill Lab /method SEO — D5 candidate evidence (PREPARED_NOT_ADMITTED)

Status: **PREPARED_NOT_ADMITTED**, 2026-11-21. This document is an evidence handoff, **not** a new release manifest, permission grant, replacement D5 rule or assertion of release readiness.

## Source of truth and baseline

- Repository: `bitmaster162/ai-skill-lab`
- Verifiable Git baseline: `main@b40470c884715ec580edd0beefb175d50ea0e660`.
- SEO candidate source at `7a8048b1846e9d4fad319971b0a6fb60ff741880`, PR #241 (DRAFT).
- Existing sealed static release: `PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015`; patch ID `SITE_A1_A2_R2_20261026_DRAFT_REVIEW`.
- Existing 108-asset manifest SHA-256: `79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889`; `payload_sha256`: `9c5bcc257f49e53172abddd1b9f366e560adbbd00f269950cc408c555536efe3`.
- Historical manifest and all `deploy/live/**` bytes are unchanged in this PR.

## Exact UTF-8 source evidence

Hashes were calculated over bytes of the exact GitHub-returned UTF-8 files. Main-content SHA is SHA-256 of the first `<main id="main" ... </main>` block using the inherited D5 regex.

| Source | Original full-file SHA-256 (main) | Candidate full-file SHA-256 | Original main-block SHA-256 | Candidate main-block SHA-256 |
| --- | --- | --- | --- | --- |
| `app/(ru)/method/page.tsx` | `9446e1e700e37e04dea1e7806a7193edfb2c2c0716253a26a952d39992678f5e` | `ada13cf8a2f95e8443b2a55039c36a9732378b4643d68f15115d9ef8a6ba345c` | `e67270d66ceee1f4f1ab6902007fdc61bf90287a3faf39b1ad402e853c536689` | `14a38b3578fb6d8e94d5fb32e8e929d2e51371b3f4e58aa1bf38dc13adc79eea` |
| `app/(en)/en/method/page.tsx` | `3958f8d073bc9618546337d29b80ad9db3b0eeccdc1ff2018d2a5768120e2bce` | `67aa5fa4440a398bf43c50829fe8e3693b29b76af81e6d490c82b5289919fc59` | `d882f035b5d3beb55ce9d25645113c1a4d902863fcbca27bb19a3eb2862ddb44` | `f978d0c01795cc8527e2939e9ed3b072569a4730b6cedace02c70deb94fe6296` |

The two original main-block hashes match the historical D5 expectations. The changed values intentionally do not.

## Existing release static preimage (NOT updated)

- `deploy/live/method.html`: 9,232 bytes, SHA-256 `f375edcdef29367f97c6a45ebeaf4abac2af632bf9ae89ca9fc2b58d42563992`.
- `deploy/live/en/method.html`: 7,934 bytes, SHA-256 `416fcd5b3849786227584a4aedfd4bc8903451f6eafcea24923fcdb48ceb0a8e`.

These are the **old** release files. They do **not** prove the new method text is present in a publishable static artifact.

## Observed CI facts

- `Next renderer language parity`: PASS, including Next.js build (run `44869260353`).
- `Static release QA`: FAIL, at `scripts/check_workshop_d5.py` with **two exact source main drift** findings (run `44869260324`). ESLint and earlier static steps passed.
- Vercel preview status success is not a static release acceptance.
- No accepted new static manifest, full-asset delta, total payload hash, independent D5 successor verifier, production equivalence or approval exists yet.

## Gate for a future versioned successor (NOT APPROVED)

1. Build candidate isolated from the old `deploy/live`; capture the exact commit, toolchain, source blob hashes and rendered page bytes. Never overwrite the accepted old archive.
2. Identify **every** changed static asset against the parent 108-file manifest; verify canonical/hreflang, five original teaching steps, safe links, CTA, privacy and safety disclosures, no fabricated results.
3. Generate a **new release ID and patch ID**, a complete file list (byte sizes and SHA-256), and a new parent-manifest hash link. Preserve the original SHA-256 manifest and immutable source.
4. Add a separate, explicit, deterministic successor verifier with negative tests, exact allowlisted deltas, proof of no unrelated source/asset changes, and independent CI. Do not weaken or skip D5, D6, source pins, manifest verification or current release checks.
5. Obtain **separate Robert approval** before any merge or production deploy. Until then, CI failure is not overridden, and PR #241 stays DRAFT.

## Security and execution

`NO_BLIND_ENABLE`, `ZERO_DELETION`, `can_trade=false`, `capital_permission=DENY`. No credentials, OAuth, sales events, paid SEO research, publishing, merge or production deployment were required.
