# AI Skill Lab

Bilingual Next.js website for practical one-to-one AI education: adults, AI builders, teams, kids 8–13 and teens 14–18.

## Operating modes

The repository contains two operating capabilities, but the current public routes are contact-only:

1. **Contact-only (current public mode)** — the site does not collect lead data. Primary contact CTAs route through `/start` / `/en/start`; only those Start pages expose the configured Telegram exit. This mode does not require a webhook.
2. **Lead-form capability (dormant on current public routes)** — `NEXT_PUBLIC_LEAD_FORM_ENABLED=true` is not a release approval. Before any form-enabled deployment, separately provision and verify the real operator identity, legal/privacy email, jurisdiction, HTTPS webhook and webhook signing secret. Required `static-release` and the local read-only preflight do not validate deployment-specific ENV values.

This keeps the live site useful without silently exposing a broken form or treating static QA as ENV/deployment approval.

## Routes

- RU: `/`, `/about`, `/build`, `/business`, `/challenge`, `/curriculum`, `/faq`, `/kids`, `/matcher`, `/method`, `/parents`, `/personal`, `/phuket`, `/pricing`, `/privacy`, `/projects`, `/proof`, `/safety`, `/start`, `/studio`, `/teens`, `/terms`
- EN: `/en`, `/en/about`, `/en/build`, `/en/business`, `/en/challenge`, `/en/curriculum`, `/en/faq`, `/en/kids`, `/en/matcher`, `/en/method`, `/en/parents`, `/en/personal`, `/en/phuket`, `/en/pricing`, `/en/privacy`, `/en/projects`, `/en/proof`, `/en/safety`, `/en/start`, `/en/studio`, `/en/teens`, `/en/terms`

## Environment

```bash
NEXT_PUBLIC_SITE_URL=https://ai-skill-lab.vercel.app
NEXT_PUBLIC_TELEGRAM_URL=https://t.me/BiTFormer
NEXT_PUBLIC_WHATSAPP_URL=
NEXT_PUBLIC_LEAD_FORM_ENABLED=false
```

Only when enabling the internal lead form:

```bash
NEXT_PUBLIC_LEGAL_OPERATOR_NAME=<real operator>
NEXT_PUBLIC_LEGAL_CONTACT_EMAIL=<real legal/privacy email>
NEXT_PUBLIC_LEGAL_JURISDICTION=<real jurisdiction>
LEAD_WEBHOOK_URL=https://...
LEAD_WEBHOOK_SECRET=<24+ chars secret>
```

The lead payload schema is `ai-skill-lab.lead.v2`. When a secret is configured, the exact JSON body is signed in `X-AI-Skill-Lab-Signature` as `sha256=<hex>`.

## Release QA

Required repository release QA is the `static-release` workflow. The local read-only equivalent is:

```bash
python scripts/preflight_release.py --release <receipt-label>
```

R87 intentionally quarantines the ENV-bound launch checker from required and operator release surfaces. It remains repository evidence only and is not an operator release command. Lead-form mode still requires real operator/legal/webhook configuration before deployment; those deployment-specific values are not part of static release QA.

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

- `/start` and `/en/start` provide a no-form lead brief before Telegram contact.
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

The public Next.js pages now mirror the contact-only operating model used by the static release: buyer and youth CTAs route through `/start` / `/en/start`, and no public page renders the dormant first-party `LeadForm`. The form/API implementation remains available for a future explicit form-enabled launch after legal and webhook configuration.

## R11 discoverability layer

- Added `/faq` and `/en/faq` with visible buyer questions/answers.
- Added minimal `WebSite` + `EducationalOrganization` JSON-LD to the root home page without inventing legal/address details.
- Kept structured data limited to claims visible on the site; no fake reviews, ratings or FAQ rich-result promises.
