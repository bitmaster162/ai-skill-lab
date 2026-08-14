# AI Skill Lab R22 Readiness

## Baseline
- R21 HEAD: `7f24dabdf2c538630a0c9e9300e726cc91d50d20`.
- R21 tree: `012d542a291ca4d6a96cee591e44b9c073110213`.
- R9 remains the isolated external release candidate.

## R22 scope
- Added `data/commercial_facts.json` as the explicit commercial facts registry for public package identity, price and session count.
- Added dependency-free `scripts/check_commercial_parity.py`.
- Added commercial parity validation to GitHub Actions static QA workflow.
- Reconciled deployable static pricing with Next/matcher commercial facts: all 9 Adult/Kids/Teens packages are now represented.
- Reconciled Adult Intensive session wording across Next/static RU/EN.
- Business remains `Custom scope`; Family Concierge remains `$1,490`.

## QA
- Commercial parity: **340 checks**, **9 packages**, **20 surfaces**, `COMMERCIAL_PARITY_PASS`.
- Static HTML pages including 404: **37**.
- Public routes: **36**.
- Internal links checked: **754**.
- Broken routes/anchors: **0**.
- Static forms: **0**.
- JSON-LD: **PASS**.
- Sitemap exact-match: **PASS**.
- Static payload files: **44**.
- Payload SHA-256: `ba97495aacaf113f468c8ac610acca516ad41f56d49ce4602008c9a43c8cdc80`.
- Contact-only launch gate: **PASS** with release env.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- Local clean-URL readback: **43 deployable files checked**, byte equality/security headers/404 **PASS**.
- `git diff --check`: **PASS**.

## Release boundary
R22 is local-only continuation and does not replace R9 as the external release candidate without a separate preview/readback gate.
