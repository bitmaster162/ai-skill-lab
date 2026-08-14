# AI Skill Lab R15 Readiness

## Baseline

- R14 HEAD: `fdebfa8947fdd6b0db01746376ab98170bdc04c8`
- R14 tree: `50fe5efa0dbddde013c658c5578ee8678e548913`
- GitHub PR #1 remains the isolated R9 release candidate.
- Vercel production remains unchanged pending deployment quota reset.

## R15 scope

- Added dependency-free `scripts/check_static_release.py`.
- Added `.github/workflows/static-qa.yml` using only Python 3.12 and standard library.
- Validator checks static routes, internal links/anchors, first-party forms, sitemap exact match, JSON-LD syntax and secret-like patterns.
- The same validator was separately run against the exact R9 content tree before it was added to PR #1.

## Local QA on R15 content

- Static HTML pages including 404: **35**.
- Public static routes: **34**.
- Internal links checked by validator: **722**.
- Static forms: **0**.
- JSON-LD parse errors: **0**.
- `STATIC_RELEASE_QA_PASS`.
- Python compile: **PASS**.
- `git diff --check`: **PASS**.

## Exact R9 CI evidence

The validator was run locally against R9 content tree `41e4ba89ae9b241c405b73701bfb39dc3f7b5a7b` and returned:

- pages: **31**
- public routes: **30**
- internal links: **624**
- forms: **0**
- JSON-LD parse: **PASS**
- sitemap exact match: **PASS**
- `STATIC_RELEASE_QA_PASS`

GitHub PR #1 now contains the validator + workflow at head `998a6d2a9ab48f77967ffcf8322499ea026f789f`.

GitHub Actions created run `31797813054`, but the job did not execute. The GitHub check annotation states that recent account payments failed or the spending limit needs to be increased. This is an account billing/spending blocker, not a validator failure. Do not rerun until billing is resolved.

## Release policy

- Do not merge PR #1 until the chosen external gate is satisfied.
- Do not treat the failed GitHub Actions run as a code/test failure.
- Exact R9 Vercel artifact remains the release candidate for preview after Vercel quota reset.
