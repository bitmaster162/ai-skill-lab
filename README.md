# AI Skill Lab

Bilingual Next.js website for practical one-to-one AI education: adults, AI builders, teams, kids 8–13 and teens 14–18.

## R3 scope

- Russian and English commercial site with dedicated youth tracks.
- `/kids` and `/teens` programs plus English equivalents.
- `/privacy`, `/terms`, `/safety` plus English equivalents.
- Youth applications require an adult confirmation; kids 8–13 leads are server-enforced as parent/guardian submissions.
- Privacy consent is required client-side and server-side.
- Lead delivery through a private HTTPS webhook with optional HMAC-SHA256 signing (recommended and required by the launch checker).
- Telegram CTA and configurable WhatsApp CTA.
- Metadata, sitemap, robots, app icon and generated Open Graph image.
- No fabricated testimonials, student counts, income claims or unverified instructor biography.

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Environment

```bash
cp .env.example .env.local
```

Public configuration:

- `NEXT_PUBLIC_SITE_URL` — final production domain.
- `NEXT_PUBLIC_TELEGRAM_URL` — public Telegram contact.
- `NEXT_PUBLIC_WHATSAPP_URL` — optional `https://wa.me/...` contact.
- `NEXT_PUBLIC_LEGAL_OPERATOR_NAME` — real person/company operating the service.
- `NEXT_PUBLIC_LEGAL_CONTACT_EMAIL` — privacy/legal contact.
- `NEXT_PUBLIC_LEGAL_JURISDICTION` — operator jurisdiction/place of operation.

Private configuration:

- `LEAD_WEBHOOK_URL` — HTTPS endpoint that receives lead JSON.
- `LEAD_WEBHOOK_SECRET` — secret used to sign the exact request body in `X-AI-Skill-Lab-Signature` as `sha256=<hex>`.

The lead payload schema is `ai-skill-lab.lead.v2` and contains adult contact information, program/audience, goal, locale, consent flags, source and timestamp.

## Launch gate

Before any public deployment, configure production environment values and run:

```bash
npm run check:launch
npm run build
npm run lint
```

`check:launch` fails on missing legal/operator data, missing webhook configuration, a short webhook secret, non-HTTPS URLs or `example.com` as the site URL.

## Youth safety

The site does not require an independent ChatGPT account for children under 13. The youth-safety page records the current operating rule used by the program: for educational use with a child under 13, actual ChatGPT interaction is adult-conducted; users under 18 require parent/guardian permission. Provider rules must be rechecked before use because third-party terms can change.

## Deployment status

R3 is source-ready but **not publicly deployed**. Final legal operator details, domain, webhook destination, webhook secret and any instructor biography/photo must be approved before production promotion.
