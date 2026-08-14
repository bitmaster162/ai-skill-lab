# AI Skill Lab

Bilingual Next.js website for practical one-to-one AI education: adults, AI builders, teams, kids 8–13 and teens 14–18.

## R4 launch mode

R4 supports two explicit operating modes:

1. **Contact-only (default / current public launch)** — the site does not collect lead data. All primary contact CTAs open the configured Telegram URL. This mode can launch without a webhook.
2. **Lead-form mode** — set `NEXT_PUBLIC_LEAD_FORM_ENABLED=true`. The launch gate then requires the real operator identity, legal/privacy email, jurisdiction, HTTPS webhook and a webhook signing secret.

This keeps the live site useful without silently exposing a broken form or inventing legal/operator details.

## Routes

- RU: `/`, `/kids`, `/teens`, `/privacy`, `/terms`, `/safety`
- EN: `/en`, `/en/kids`, `/en/teens`, `/en/privacy`, `/en/terms`, `/en/safety`

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
