# AI Skill Lab R16 Readiness

## Baseline

- R15 HEAD: `14629c971e28c609ab066731ab8e708479eb5305`
- R15 tree: `b3072c569732688188d795b8845ffa1bc27338f4`

## Scope

- Removed the `https://example.com` fallback from Next `robots()` and `sitemap()`.
- Bound both generators to the existing single canonical source `site.url` in `lib/site.ts`.
- Extended dependency-free static release QA to reject release-critical source URLs pointing at `example.com` or `localhost`.
- Static release bytes/content were otherwise unchanged.

## QA

- Static HTML pages including 404: **35**.
- Public routes: **34**.
- Internal links inspected: **722**.
- Public static forms: **0**.
- JSON-LD parse: **PASS**.
- Sitemap exact-match: **PASS**.
- Source placeholder URL hits: **0**.
- `git diff --check`: **PASS**.

## External state at R16 preparation

- GitHub PR #1 remains open/draft on exact head `998a6d2a9ab48f77967ffcf8322499ea026f789f`; its only observed Actions run remains blocked before execution by GitHub account billing/spending state.
- Vercel has no newer AI Skill Lab deployment; production remains R5 deployment `dpl_Gduv8Jv2cvVWBDEht9K1jYPwNtwG`.
- No merge, production promotion, billing mutation or domain purchase is part of R16.
