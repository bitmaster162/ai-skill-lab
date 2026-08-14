# AI Skill Lab R21 Readiness

## Baseline
- R20 HEAD: `a93deb053d0b6516aad83f1c0f42c431a9d0ac98`.
- R20 tree: `1e511032d82fb74c0bd22daeea2698a9500b74cc`.
- R9 remains the isolated external release candidate.

## R21 scope
- Added plain-language pre-payment commercial clarity to RU/EN pricing pages.
- Clarifies that website pricing is a reference for the stated package.
- Before payment, exact scope, currency/payment method, schedule, rescheduling, cancellation and refund terms are confirmed with the adult customer.
- Agreed written individual terms take priority if they differ from the website.
- Added direct links to Terms and Start from the pricing clarification block.
- No new refund guarantee, cancellation promise or legal claim was invented.

## QA
- Static HTML pages including 404: **37**.
- Public routes: **36**.
- Internal links checked: **754**.
- Broken routes/anchors: **0**.
- Static forms: **0**.
- JSON-LD: **PASS**.
- Sitemap exact-match: **PASS**.
- Static payload files: **44**.
- Payload SHA-256: `78dddd16fe6e2c81964be0010f12bb53ac0f652ad24252f751c72a0cdb8ed314`.
- Contact-only launch gate: **PASS** with release env.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- Local clean-URL live readback: **43 deployable files checked**, byte equality/security headers/404 **PASS**.
- `git diff --check`: **PASS**.

## Release boundary
R21 is local-only continuation and does not replace the R9 external release candidate without a separate preview/readback gate.
