# AI Skill Lab

Premium bilingual website for practical, one-to-one AI education.

## R2 scope

- Russian home page with 5 tracks: adults, AI Builder, business, kids 8–13, teens 14–18.
- Dedicated `/kids` and `/teens` commercial pages.
- English versions at `/en`, `/en/kids`, `/en/teens`.
- Premium Family Concierge offer with parent sessions and a learner project.
- Project-based outcomes without fabricated testimonials, income claims or unverifiable student counts.
- Responsive desktop/mobile navigation and RU/EN switches.
- Telegram CTA with configurable WhatsApp link.
- Lead endpoint at `POST /api/lead` with honeypot filtering, input limits and optional webhook delivery.
- For minors, contact details are collected from an adult only; no child accounts are created by this site.

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

Set:

- `NEXT_PUBLIC_SITE_URL` — final production domain.
- `NEXT_PUBLIC_TELEGRAM_URL` — public Telegram contact.
- `NEXT_PUBLIC_WHATSAPP_URL` — optional `https://wa.me/...` contact.
- `LEAD_WEBHOOK_URL` — private HTTPS endpoint that receives lead JSON.

The lead payload contains adult name/contact, audience, requested program, goal, locale, source and timestamp.

## Production checklist

1. Confirm final brand/domain and replace `https://example.com`.
2. Confirm Telegram/WhatsApp destinations.
3. Add only source-backed teacher biography, photo, case studies and testimonials.
4. Configure `LEAD_WEBHOOK_URL` in Vercel.
5. Add privacy/terms pages appropriate to the operating jurisdiction.
6. Check age requirements for each third-party AI service used in youth lessons.
7. Run `npm run build` and `npm run lint` in a network-enabled environment.
8. Deploy only after final content and form destination are approved.

## Local dependency-free preview

The `preview/` directory contains static pages for visual review when npm dependencies cannot be installed. Preview and review artifacts are intentionally ignored by Git.
