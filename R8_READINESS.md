# AI Skill Lab R8 Readiness

## Baseline

- R7 HEAD: `d79ec89d70b6c8563c2d6f5e96d8896fe9a56d4c`
- R7 tree: `18c40c6f9c82ed1910ed68836aeee27dab8a2077`
- Public production remains the previously verified R5 while Vercel API deploy quota is exhausted.

## R8 scope

- Added RU/EN `/projects`: example outcome formats, explicitly not testimonials or client case studies.
- Added RU/EN `/parents`: parent-facing buying logic, visible progress rubric, youth safety framing and direct links to official OpenAI age guidance.
- Added proof-library links on RU/EN home pages.
- Added parent decision bridge on RU/EN kids pages.
- Expanded RU/EN sitemap and footer navigation.
- Kept the public operating model contact-only: no first-party lead forms and no checkout.

## Current official ChatGPT age framing checked on 2026-08-14

- ChatGPT is not meant for children under 13.
- Users ages 13–18 require parent/legal-guardian permission.
- In an educational context for children under 13, the actual interaction with ChatGPT must be conducted by an adult.
- Source linked from parent pages: OpenAI Help Center article `Is ChatGPT safe for all ages?`.

## QA

- Static HTML pages including 404: **25**.
- Sitemap URLs: **24**.
- Links inspected: **520**.
- Broken internal routes/anchors: **0**.
- Static forms: **0**.
- Secret-pattern hits: **0**.
- `git diff --check`: **PASS**.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- Full Next typecheck/build: **NOT CLAIMED** because npm package resolution remains unavailable in this sandbox (`EAI_AGAIN`); current `TS2307` diagnostics are dependency-resolution failures.
- `check:launch` contact-only configuration: **PASS**.

## External gates

- GitHub repository creation is delegated to the supplied Manus task because the available GitHub connector does not expose repository creation.
- Vercel R8 preview/production is not attempted while the API deployment quota is exhausted.
- R5 production remains untouched and serves as live rollback authority.
