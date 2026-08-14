# AI Skill Lab R23 Readiness

## Baseline
- R22 HEAD: `09cb6725d64caebb6d1754344ca87b8577a392c7`.
- R22 tree: `ef8e191505373991f4467a983503a7d2e11e726a`.
- R9 remains the isolated external release candidate.

## R23 scope
- Unified the public contact funnel: external Telegram exits are allowed only on RU/EN Start pages.
- Replaced direct Telegram CTAs in deployable static home/adult/kids/teens/legal/safety pages with internal Start routes.
- Refactored shared Next `ContactButtons` to internal Start + Matcher links instead of direct messenger exits.
- Fixed EN home CTAs that incorrectly linked to bare RU `/start`; they now preserve `/en/start`.
- Added dependency-free `scripts/check_contact_funnel.py` and CI workflow step.
- Language-switch links remain allowed to cross locale intentionally.

## QA
- Contact funnel: **109 checks**, `CONTACT_FUNNEL_PASS`.
- Commercial parity: **340 checks**, `COMMERCIAL_PARITY_PASS`.
- Static HTML pages including 404: **37**.
- Public routes: **36**.
- Internal links checked: **778**.
- Broken routes/anchors: **0**.
- Static forms: **0**.
- JSON-LD: **PASS**.
- Sitemap exact-match: **PASS**.
- Static payload files: **44**.
- Payload SHA-256: `ab3c3a85fa90c49c3e6e8018ec82858b0879269735748d98c9ee5bad1f329194`.
- Contact-only launch gate: **PASS** with release env.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- Local clean-URL readback: **43 deployable files checked**, byte equality/security headers/404 **PASS**.
- `git diff --check`: **PASS**.

## Release boundary
R23 is local-only continuation and does not replace R9 as the external release candidate without its own preview/readback gate.
