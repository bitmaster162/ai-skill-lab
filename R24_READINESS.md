# AI Skill Lab R24 Readiness

## Purpose

R24 is the final local pre-preview commercial-parity checkpoint. It closes home-page pricing drift without changing the external R9 release candidate.

## Baseline

- Parent R23 HEAD: `007a25e577488cc281c6a84e40253c4c7bd04742`
- Parent R23 tree: `fd2524ed08c136225093ce7d6d74b4571028fd38`
- Local branch: `agent/r24-home-commercial-parity`
- GitHub `main` remains R8 at `5ef428429a4d010b70686c1018004d9e84696d06`.
- GitHub PR #1 remains the isolated R9 release candidate at head `998a6d2a9ab48f77967ffcf8322499ea026f789f`.
- Vercel production remains R5 deployment `dpl_Gduv8Jv2cvVWBDEht9K1jYPwNtwG`.

## R24 scope

- Added RU/EN home pages to the commercial-facts parity gate.
- Fixed static home Intensive session text to the canonical registry wording:
  - RU: `12 занятий + проект`
  - EN: `12 sessions + project`
- Added visible Family Concierge block to RU/EN static home pages with canonical facts:
  - `$1,490`
  - RU: `12 занятий + 2 сессии родителю`
  - EN: `12 learner sessions + 2 parent sessions`
- Added the same combined Family session phrase to RU/EN Next home surfaces so the parity gate checks a single unambiguous commercial fact.
- External contact remains routed through `/start` and `/en/start`.

## QA

- Commercial parity: **388 checks / 9 packages / 24 surfaces / PASS**.
- Static HTML pages including 404: **37**.
- Public routes: **36**.
- Internal links checked: **780**.
- Broken routes/anchors: **0**.
- Static forms: **0**.
- JSON-LD parse: **PASS**.
- Contact funnel: **109 checks / PASS**.
- Launch gate with production public env: **PASS**.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- TypeScript dependency-resolution diagnostics (`TS2307`): **86** because local Next/React type dependencies remain unavailable; full framework typecheck/build is not claimed.
- `git diff --check`: **PASS**.
- Local clean-URL byte readback: **43 files checked / PASS**.
- Security-header readback: **PASS**.
- 404 sentinel: **PASS**.

## Release fingerprint

- Static payload files in manifest: **44**.
- `payload_sha256`: `21607205afe2db6c7129d6348cabb036939e0b3d8b71423425614530892dc0bd`.

## External gates unchanged on fresh manual read

### GitHub

PR #1 remains open/draft on head `998a6d2a9ab48f77967ffcf8322499ea026f789f`. The existing workflow run remains blocked before execution by GitHub account billing/spending state. Do not rerun until that blocker changes.

### Vercel

No new AI Skill Lab deployment was present on the fresh deployment list. Production remains the previously verified R5 deployment. R9 preview remains the next deployment candidate after API quota availability returns.

## Release boundary

Do not substitute R24 for R9 in the next external deployment. The next promotion sequence remains:

`exact R9 artifact -> Vercel preview -> machine byte/header/404 readback -> PR #1 merge gate -> production -> production readback`

R10-R24 remain a later stacked improvement line until R9 is independently verified and promoted.
