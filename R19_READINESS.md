# AI Skill Lab R19 Readiness

## Baseline

- R18 HEAD: `18d846b2074bbb94cd7009c33bc018ef2cf627da`.
- R18 tree: `7a505033683963b3610baa7ff0daa1d185a6f22b`.
- R9 remains the isolated external release candidate; R19 is local-only continuation and is not merged/deployed.

## R19 scope

- Added RU/EN `/matcher` program matcher.
- Matcher uses only in-page state and local calculation; no form submission, analytics, cookies, browser storage, fetch/XHR/WebSocket/sendBeacon, or external script.
- Added starting recommendations for Adult, Kids 8–13, Teens 14–18 and Business pilot paths.
- Fixed package mapping remains bounded to already-published pricing; business remains custom scope rather than invented fixed pricing.
- Added matcher links from RU/EN start pages and source footer navigation.
- Added RU/EN matcher routes to Next sitemap and static sitemap.
- Updated static release manifest/fingerprint.

## QA

- Static HTML pages including 404: **37**.
- Public static routes: **36**.
- Internal links checked: **750**.
- Broken internal routes/anchors: **0**.
- Static forms: **0**.
- JSON-LD parse: **PASS**.
- Static sitemap exact-match: **PASS**.
- Release manifest: **PASS**, 44 payload files, payload SHA-256 `373eea9373621c987107972fcaeb4c6cb6e99038807c8f58a13e59eab585c493`.
- Matcher privacy scan: **PASS** for network/storage/cookie/external-script patterns.
- Contact-only launch gate: **PASS** with release env (`NEXT_PUBLIC_SITE_URL`, Telegram URL, lead form disabled).
- Live clean-URL local fixture: **43 deployable files checked**, byte equality/security headers/404 **PASS** (`LIVE_STATIC_READBACK_PASS`).
- Next page routes: **36**.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- R19-specific non-environment TypeScript errors: **0** after explicit matcher key narrowing.
- Full Next typecheck/build: **NOT CLAIMED** because local project dependencies are not installed; remaining TypeScript output is dominated by missing Next/React/Node typings.
- `git diff --check`: **PASS**.

## Release boundary

Do not replace the R9 external release candidate with R19 without a separate preview/readback gate. No merge or Vercel production promotion is part of R19.
