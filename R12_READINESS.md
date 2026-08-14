# AI Skill Lab R12 Readiness

## Baseline

- R11 local HEAD: `858e461af98212d390079bf4fc3cc83ee7a4e012`
- R11 tree: `ac7b16e466dc354e726b80ab1c49a6def384ce5d`
- GitHub `main` remains R8 and draft PR #1 remains the isolated R9 release candidate.
- Vercel production remains on the previously verified R5 deployment until the API deployment quota resets and an exact R9 preview is verified.

## R12 scope

- Added RU/EN `/curriculum` pages as a buyer decision layer.
- Compares Adult, Kids 8–13 and Teens 14–18 trajectories without inventing outcomes or testimonials.
- Added an example 10-session adult core and a 10-session youth progression model.
- Progress is framed as artifact + explanation + verification, not prompt count.
- Fixed Next Header FAQ links to use dedicated `/faq` routes instead of `/#faq`.
- Added Curriculum links to the Next footer.
- Added curriculum routes to Next and static sitemaps.
- Added discoverable static curriculum links from home and pricing pages only; avoided mass rewriting all older static footers.
- Contact-only operating model preserved: no public LeadForm and no checkout.

## QA

- Static HTML pages including 404: **35**.
- Public static routes: **34**.
- Links inspected: **766**.
- Broken internal routes/anchors: **0**.
- Static forms: **0**.
- Static sitemap URLs: **34**, all unique and exact-match to public routes.
- New RU/EN curriculum canonical/hreflang checks: **PASS**.
- Secret-pattern hits: **0**.
- Next page routes: **34**.
- Public LeadForm references: **0**.
- TypeScript syntax-class diagnostics (`TS1xxx`): **0**.
- `check:launch` contact-only configuration: **PASS**.
- `git diff --check`: **PASS**.

## External release policy

R12 is a local continuation checkpoint only. Do not mix it into R9 PR #1. The next external release operation remains: exact R9 artifact → Vercel preview → live route QA → merge PR #1 → production.
