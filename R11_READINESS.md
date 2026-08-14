# AI Skill Lab R11 Readiness

## Baseline
- R10 local HEAD: `d8416bc643a3ab2ae16514e51cafe1d4791ce704`
- R10 tree: `d2c406d45884b543f5b3d77582367ad45d3dc91c`
- GitHub PR #1 / R9 remains untouched; Vercel production remains on the prior verified release while deploy quota is unavailable.

## Scope
- Added visible RU/EN `/faq` buyer-clarity routes.
- Added minimal `WebSite` + `EducationalOrganization` JSON-LD to the root home page.
- Structured data intentionally omits legal name, physical address, ratings, reviews, student counts and other facts that are not verified.
- Expanded Next/static sitemap coverage for FAQ.
- Added FAQ to the Next footer.
- Preserved contact-only public mode: no first-party lead form or checkout.

## Policy
- No claim that structured data guarantees rich results.
- No FAQ rich-result markup is used merely for SERP decoration.
- Structured data describes content that is visible on the public site.

## QA
- Static HTML pages including 404: **33**.
- Public static routes: **32**.
- Internal links/anchors checked: **670**.
- Broken internal routes/anchors: **0**.
- Static forms: **0**.
- JSON-LD blocks parsed: **2**; parse errors: **0**.
- Restricted schema residue (`FAQPage`, founder, ratings/reviews): **0**.
- Static sitemap URLs: **32**, all unique.
- Secret-pattern hits: **0**.
- Next page routes: **32**.
- TypeScript source files checked: **48**.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- Dependency-resolution diagnostics (`TS2307`): expected in this sandbox because dependencies are not installed.
- `check:launch` contact-only mode: **PASS**.
- `git diff --check`: **PASS**.
