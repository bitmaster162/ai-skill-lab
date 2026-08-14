# AI Skill Lab R20 Readiness

## Baseline

- R19 HEAD: `3aaf1760718519586cc2b1b04b0a7ff4960df8f8`.
- R19 tree: `85517bb7ad00083151cf4eb94b354015902f871c`.
- R9 remains the isolated external release candidate. R20 is local-only continuation.

## R20 scope

- Added local-only safe brief generation to RU/EN program matcher.
- Copy action uses browser clipboard only, with a local textarea fallback; no network request is introduced.
- Generated brief contains route, goal, depth, starting recommendation and a non-sensitive context placeholder.
- Youth routes explicitly add parent/legal-guardian organizational contact.
- No personal information is requested or persisted by the matcher.

## QA

- Static HTML pages including 404: **37**.
- Public routes: **36**.
- Internal links checked: **750**.
- Broken routes/anchors: **0**.
- Static forms: **0**.
- JSON-LD: **PASS**.
- Sitemap exact-match: **PASS**.
- Static release payload files: **44**.
- Static release payload SHA-256: `182666c9d74f08ed6b936d5b5391f7ab37318700c479fc874263131f38fabb01`.
- Matcher privacy scan: **PASS** for network/storage/cookie/external-script patterns.
- Contact-only launch gate with release env: **PASS**.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- R20-specific non-environment TypeScript errors: **0**.
- Local clean-URL live readback: **43 deployable files checked**, byte equality/security headers/404 **PASS**.
- `git diff --check`: **PASS**.

## Release boundary

R20 must not replace R9 as the external release candidate without a separate preview/readback gate. No merge or production deploy is included.
