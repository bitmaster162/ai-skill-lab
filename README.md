# AI Skill Lab

Bilingual Next.js website for practical one-to-one AI education: adults, AI builders, teams, kids 8–13 and teens 14–18.

## Operating mode

The current public static release exposes two deliberate contact paths on `/start` / `/en/start`:

1. **First-party application form (current public mode)** — the browser submits JSON only to same-origin `/api/lead`. `deploy/live/vercel.json` proxies that path to the separately deployed `ai-skill-lab-ingress` service. The public static project owns no webhook/signing secret.
2. **Direct-contact fallback** — Telegram, email, WhatsApp and LINE remain available if the form cannot be used. Youth applications and organizational communication use an adult contact only.
3. **Isolated ingress authority** — operator identity, privacy contact, jurisdiction, allowlisted origins, 30-day retention, rate-limit readiness, webhook URL and signing secret are provisioned and verified on the ingress project, not the public static project.

`NEXT_PUBLIC_LEAD_FORM_ENABLED=true` remains an ENV-bound Next-runtime capability and is not public static-release authority. The public form is activated only by the committed static release plus required `static-release` QA and a separately approved production release.

The canonical production host is `https://aiskillab.work`. The legacy public Vercel hostname `https://ai-skill-lab.vercel.app` is routing compatibility only and must permanently redirect to the canonical host while preserving the requested path.

## Routes

- RU: `/`, `/about`, `/build`, `/business`, `/challenge`, `/curriculum`, `/family`, `/faq`, `/kids`, `/matcher`, `/method`, `/parents`, `/personal`, `/phuket`, `/pricing`, `/privacy`, `/projects`, `/proof`, `/safety`, `/start`, `/studio`, `/teens`, `/terms`
- EN: `/en`, `/en/about`, `/en/build`, `/en/business`, `/en/challenge`, `/en/curriculum`, `/en/family`, `/en/faq`, `/en/kids`, `/en/matcher`, `/en/method`, `/en/parents`, `/en/personal`, `/en/phuket`, `/en/pricing`, `/en/privacy`, `/en/projects`, `/en/proof`, `/en/safety`, `/en/start`, `/en/studio`, `/en/teens`, `/en/terms`

## Environment

```bash
NEXT_PUBLIC_SITE_URL=https://aiskillab.work
NEXT_PUBLIC_TELEGRAM_URL=https://t.me/BiTFormer
NEXT_PUBLIC_WHATSAPP_URL=
NEXT_PUBLIC_LEAD_FORM_ENABLED=false
```

The `.env.example` block above is for the optional Next.js runtime and defaults its form flag to false. The committed public static release does not require public-project ENV values for the form. Private receiver/signing configuration belongs only to `services/lead-ingress/.env.example` and the isolated ingress project.

The lead payload schema is `ai-skill-lab.lead.v2`. The ingress signs the exact downstream JSON body with its private signing secret; that secret is never shipped in the public static release.

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

- Historical R7 state used a no-form lead brief; the current D6 release adds the first-party form while preserving the brief and direct-contact fallback.
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

Historical R10 removed the first-party form from public routes. The current D6 static release supersedes that contact-only state after the isolated ingress, legal/privacy configuration, rate limit and enabled-branch E2E were separately verified.

## R11 discoverability layer

- Added `/faq` and `/en/faq` with visible buyer questions/answers.
- Added minimal `WebSite` + `EducationalOrganization` JSON-LD to the root home page without inventing legal/address details.
- Kept structured data limited to claims visible on the site; no fake reviews, ratings or FAQ rich-result promises.
