# AI Skill Lab

Bilingual Next.js website for practical one-to-one AI education: adults, AI builders, teams, kids 8–13 and teens 14–18.

## R9 launch mode

R4 supports two explicit operating modes:

1. **Contact-only (default / current public launch)** — the site does not collect lead data. All primary contact CTAs open the configured Telegram URL. This mode can launch without a webhook.
2. **Lead-form mode** — set `NEXT_PUBLIC_LEAD_FORM_ENABLED=true`. The launch gate then requires the real operator identity, legal/privacy email, jurisdiction, HTTPS webhook and a webhook signing secret.

This keeps the live site useful without silently exposing a broken form or inventing legal/operator details.

## Routes

- RU: `/`, `/personal`, `/business`, `/kids`, `/teens`, `/about`, `/pricing`, `/method`, `/phuket`, `/projects`, `/parents`, `/faq`, `/start`, `/privacy`, `/terms`, `/safety`
- EN: `/en`, `/en/personal`, `/en/business`, `/en/kids`, `/en/teens`, `/en/about`, `/en/pricing`, `/en/method`, `/en/phuket`, `/en/projects`, `/en/parents`, `/en/faq`, `/en/start`, `/en/privacy`, `/en/terms`, `/en/safety`

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

## Launch gate

```bash
npm run check:launch
npm run build
npm run lint
```

The gate validates the public site/contact in contact-only mode. If lead collection is enabled it becomes stricter and blocks missing operator/privacy/webhook configuration.

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
