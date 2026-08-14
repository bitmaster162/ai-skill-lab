# AI Academy

Premium Russian-language website for practical AI education.

## Current scope

- Home page with adult, builder, business and kids tracks.
- Dedicated `/kids` page for ages 8–14.
- Responsive layout, pricing, FAQ and conversion sections.
- Parent-only contact guidance for the kids program.
- Lead endpoint at `POST /api/lead` with honeypot filtering and optional webhook delivery.
- No child accounts and no direct collection of a child's contact details.

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Lead delivery

Set an HTTPS webhook you control:

```bash
cp .env.example .env.local
# then set LEAD_WEBHOOK_URL in .env.local
```

The endpoint sends a compact JSON payload with name, audience, adult contact, goal, source and timestamp.

## Production checklist

1. Replace `https://example.com` in `app/layout.tsx` with the final domain.
2. Confirm brand name, prices and contact channel.
3. Configure `LEAD_WEBHOOK_URL` in Vercel.
4. Add final privacy/terms pages for the operating jurisdiction.
5. Run `npm run build` and `npm run lint` in a network-enabled environment.
6. Deploy only after the final content and form destination are approved.

## Local review preview

A dependency-free HTML preview can be generated/kept outside the production Git payload under `preview/` for quick visual review.
