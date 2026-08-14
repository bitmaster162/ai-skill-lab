# AI Skill Lab R3 — readiness receipt

Date: 2026-08-14 (Asia/Bangkok)

## Baseline

- Pre-R3 HEAD: `7e5144f52ac5e7d11e3bc9f17541554de4b25931`
- Pre-R3 tree: `1800285a3224cd6f4400b4f2113587a58fce2a2e`
- Baseline restored clean before R3 implementation.
- A stale externally-mounted README regression was restored from the verified R2 HEAD before any R3 material changes.

## R3 scope

- Privacy, learning terms and youth AI safety in RU/EN.
- Adult-only organizational contact rules for minors.
- Privacy consent and adult-confirmation gates in the form.
- Server-side enforcement for youth leads; kids program requires parent/guardian audience.
- Lead payload schema `ai-skill-lab.lead.v2`.
- Optional HMAC-SHA256 webhook signing.
- Production launch configuration checker.
- Public operator/legal configuration fields.
- Sitemap expansion to 12 public routes.
- App icon and generated Open Graph image.
- Canonical/language alternates for core commercial routes.
- Removed unfinished R2 instructor placeholder copy from the public page.

## Verification

- `git diff --check`: PASS.
- TS/TSX syntax parse via TypeScript compiler API: 27 files, PASS.
- Static CSS class coverage: 147 classes, 0 missing, PASS.
- Static internal route/link check: 12 routes, 0 missing, PASS.
- Lead policy source assertions: 8/8 PASS.
- Launch checker negative case (empty environment): expected FAIL, PASS behavior.
- Launch checker positive case (synthetic valid environment): PASS.
- Secret-pattern scan: no detected API keys/private keys in source payload.

## External dependency limitation

A full `npm install`/`next build` could not be completed in the current sandbox because access to the external npm registry did not complete. Global TypeScript reports missing Next/React/Node package types because `node_modules` is absent; this is an environment/dependency state, not a verified application type error.

Therefore R3 status is **PASS WITH CONDITIONS** until a dependency-enabled environment runs:

```bash
npm install
npm run check:launch
npm run build
npm run lint
```

The launch checker intentionally requires final domain, operator identity/contact/jurisdiction, webhook URL and webhook secret before production promotion.

## Youth safety source check

As checked on 2026-08-14, OpenAI Terms require users to be at least 13 (or the applicable local minimum age), with parent/legal-guardian permission for users under 18. OpenAI's education safety guidance additionally states that for children under 13, actual ChatGPT interaction in an education context must be conducted by an adult.

Sources:
- https://openai.com/policies/terms-of-use/
- https://help.openai.com/en/articles/8313401

## Deployment

No public deployment, Vercel promotion, domain change or external webhook write was performed in R3.
