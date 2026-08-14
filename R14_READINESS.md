# AI Skill Lab R14 Readiness

## Baseline

- R13 HEAD: `08cb13fc289f6053ff6ba81ec8cef24e88361fb7`
- R13 tree: `2298c56898d6df00662f62f9c74e446f14c8224a`
- GitHub `main` remains R8; draft PR #1 remains the isolated R9 release candidate.
- R10–R14 remain local continuation checkpoints and are not mixed into PR #1.

## R14 scope

- Reworked RU/EN `/start` into a no-form conversion brief page.
- Added four explicit brief templates: Adult, Kids 8–13, Teens 14–18 and Business workflow pilot.
- Added data-minimization guidance: no identity documents, child school/home address, passwords, API keys, payment data or sensitive corporate data are required to start.
- Added transparent next-step flow: fit → package → scope/schedule/payment terms → start.
- Preserved direct Telegram contact-only mode and adult-led youth coordination.

## QA

- Static HTML pages including 404: **35**.
- Public static routes: **34**.
- Static links inspected: **756**.
- Broken internal routes/anchors: **0**.
- Static forms: **0**.
- RU/EN start canonical/hreflang checks: **PASS**.
- Public LeadForm references: **0**.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- `check:launch` contact-only configuration: **PASS**.
- `git diff --check`: **PASS**.

## Release policy

R14 is local-only. Do not add it to current R9 PR #1. External release order remains exact R9 artifact → Vercel preview → live route QA → merge PR #1 → production. Subsequent local checkpoints can then be promoted in a separate reviewed stack.
