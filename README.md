# AI Skill Lab

Bilingual Next.js website for practical one-to-one AI education: adults, AI builders, teams, kids 8–13 and teens 14–18.

## Operating modes

The repository contains two operating capabilities, but the current public routes are contact-only:

1. **Contact-only (current public mode)** — the site does not collect lead data. Primary contact CTAs route through `/start` / `/en/start`; only those Start pages expose the configured direct contact exits. This mode does not require a webhook.
2. **Lead-form capability (dormant on current public routes)** — `NEXT_PUBLIC_LEAD_FORM_ENABLED=true` is not a release approval. The browser form remains dormant until a separate activation release. Server-side intake is isolated under `services/lead-ingress/**`, defaults disabled, and is not part of the current static public release. Before any form-enabled deployment, separately provision and verify the real operator identity, legal/privacy email, jurisdiction, dedicated ingress project, HTTPS downstream receiver, mandatory signing secret, allowed origins, and provider-level rate limiting. Required `static-release` and the local read-only preflight do not validate deployment-specific ENV values.

This keeps the live site useful without silently exposing a broken form or treating static QA as ENV/deployment approval.

## Routes

- RU: `/`, `/about`, `/build`, `/business`, `/challenge`, `/curriculum`, `/family`, `/faq`, `/kids`, `/matcher`, `/method`, `/parents`, `/personal`, `/phuket`, `/pricing`, `/privacy`, `/projects`, `/proof`, `/safety`, `/start`, `/studio`, `/teens`, `/terms`
- EN: `/en`, `/en/about`, `/en/build`, `/en/business`, `/en/challenge`, `/en/curriculum`, `/en/family`, `/en/faq`, `/en/kids`, `/en/matcher`, `/en/method`, `/en/parents`, `/en/personal`, `/en/phuket`, `/en/pricing`, `/en/privacy`, `/en/projects`, `/en/proof`, `/en/safety`, `/en/start`, `/en/studio`, `/en/teens`, `/en/terms`

## Environment

Public static project:

```bash
NEXT_PUBLIC_SITE_URL=https://ai-skill-lab.vercel.app
NEXT_PUBLIC_TELEGRAM_URL=https://t.me/BiTFormer
NEXT_PUBLIC_WHATSAPP_URL=
NEXT_PUBLIC_LEAD_FORM_ENABLED=false
```

Public legal/privacy values remain blank until the activation facts are frozen:

```bash
NEXT_PUBLIC_LEGAL_OPERATOR_NAME=<real operator>
NEXT_PUBLIC_LEGAL_CONTACT_EMAIL=<real legal/privacy email>
NEXT_PUBLIC_LEGAL_JURISDICTION=<real jurisdiction>
```

Private receiver/signing configuration is not a public-project ENV contract. It lives only in `services/lead-ingress/.env.example` and the future dedicated ingress Vercel project. The ingress additionally requires an explicit server-side enable flag, allowed HTTPS origins, the exact legal operator/jurisdiction/privacy contact, the frozen retention value, and verified provider-level rate limiting before forwarding can become available.

The lead payload schema remains `ai-skill-lab.lead.v2`. The isolated ingress adds `requestId`, `receivedAt`, and optional `sourcePath`. It signs the exact JSON body using `X-AI-Skill-Lab-Timestamp`, `X-AI-Skill-Lab-Request-Id`, and `X-AI-Skill-Lab-Signature: v1=<hex>`, where the HMAC input is `timestamp + "." + requestId + "." + raw_json_body`.

## Release QA

Required repository release QA is the `static-release` workflow. The local read-only equivalent is:

```bash
python scripts/preflight_release.py --release <receipt-label>
```

R87 intentionally quarantines the ENV-bound launch checker from required and operator release surfaces. It remains repository evidence only and is not an operator release command. Lead-form activation still requires real operator/legal/receiver/rate-limit configuration before deployment; those deployment-specific values are not part of static release QA.

### Historical readiness archive

Root-level `R*_READINESS.md` files are historical evidence snapshots from earlier release epochs. They are not current operator instructions, release authority, production-state authority, or approval to run legacy commands. Do not execute commands or rely on deployment/status claims from those files as current truth. Current repository release authority is the required `static-release` workflow and the local read-only preflight above.

## Youth safety

- Youth applications/communication use an adult contact.
- The site does not request a child’s own phone/email/messenger contact.
- For educational use with a child under 13, ChatGPT interaction is adult-conducted.
- Users under 18 require parent/guardian permission for ChatGPT, and provider age rules are rechecked before use.

## Claims discipline

No fabricated testimonials, student counts, income claims or unverified instructor biography are included.

## R7 conversion layer

- `/start` and `/en/start` provide a no-form lead brief before direct contact.
- `/about` and `/en/about` make the teaching method and claims discipline explicit.
- Static release adds skip navigation, focus-visible treatment, reduced-motion handling and a real 404 page.
- No testimonials, student counts or outcome guarantees were added.

## R8 proof layer

- `/projects` and `/en/projects`: example outcome formats, explicitly not client case studies.
- `/parents` and `/en/parents`: buyer-facing progress rubric, age/safety framing and family decision support.
- Public youth age wording remains aligned with current OpenAI guidance and is linked to the official Help Center from the static parent page.

## R9 buyer-intent layer

- `/pricing` and `/en/pricing`: transparent package comparison without checkout.
- `/method` and `/en/method`: transferable learning method and verification loop.
- `/phuket` and `/en/phuket`: honest Phuket-by-arrangement + online worldwide positioning without claiming a permanent venue.
- Header pricing links now use dedicated routes; footer links expose pricing, method and location pages.

## R10 contact-flow cleanup

The public Next.js pages mirror the contact-only operating model used by the static release: buyer and youth CTAs route through `/start` / `/en/start`, and no public page renders the dormant first-party `LeadForm`. The old in-app `app/api/lead/route.ts` intake is intentionally retired by the R101 hardening candidate in favor of the isolated disabled ingress service. Public form activation remains a separate release after legal, receiver, rate-limit, privacy, Proof, CSP, rewrite, and delivery verification.

## R11 discoverability layer

- Added `/faq` and `/en/faq` with visible buyer questions/answers.
- Added minimal `WebSite` + `EducationalOrganization` JSON-LD to the root home page without inventing legal/address details.
- Kept structured data limited to claims visible on the site; no fake reviews, ratings or FAQ rich-result promises.
