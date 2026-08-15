# AI Skill Lab R25 — navigation + accessibility readiness

Date: 2026-08-15 (Asia/Bangkok)

## Scope
- unify all deployable RU/EN static headers into one navigation model;
- preserve locale on navigation and language switching;
- add accessible mobile `<details>` navigation to every non-404 static page;
- keep public contact flow internal (`/start` / `/en/start`) except direct Telegram on the Start pages;
- add 44px/48px touch-target floors and mobile spacing improvements;
- add persistent navigation-parity and static-accessibility gates;
- mirror touch-target improvements into Next source CSS.

## Exact QA
- static HTML pages including 404: 37
- public routes: 36
- internal links checked: 1144
- broken internal routes/anchors: 0
- forms: 0
- JSON-LD blocks parsed: 2
- navigation parity: 793 checks — PASS
- static accessibility: 1373 checks across 37 pages — PASS
- commercial parity: 388 checks — PASS
- contact funnel: 109 checks — PASS
- contact-only launch gate: PASS
- release manifest: 44 payload files
- release payload SHA-256: `c57ca64e224c092188edd404242825cc98f773702d498cc9b820351b75718e77`
- TypeScript syntax-class diagnostics (TS1xxx): 0
- full Next typecheck: NOT CLAIMED; sandbox lacks installed Next/React typings and reports expected module-resolution diagnostics
- browser screenshot QA: NOT CLAIMED; sandbox Chromium navigation is blocked by administrator policy (`ERR_BLOCKED_BY_ADMINISTRATOR`)
- `git diff --check`: PASS

## Vercel state
A fresh Vercel deployment probe on 2026-08-15 returned `api-deployments-free-per-day` quota exhausted (`100/100`, remaining `0`). Reset: `2026-08-16 17:49:21 Asia/Bangkok` (timestamp `1786877361642`).

R25 is therefore LOCAL-READY / NOT DEPLOYED. Production must not be described as R25 until a fresh Vercel deployment and public readback prove it.
