# AI Skill Lab lead ingress

This directory is the isolated server-side ingress for the future AI Skill Lab first-party application form. It is intentionally separate from the deterministic static public release in `deploy/live/**`.

## Safety boundary

The service is fail-closed. `LEAD_INGRESS_ENABLED` defaults to `false`. Even when enabled, forwarding remains unavailable unless all required server-only configuration is present: an HTTPS receiver, a HMAC secret of at least 32 UTF-8 bytes, one or more HTTPS allowed origins, the exact legal operator and jurisdiction, a monitored privacy contact, the frozen 30-day unconverted-lead retention value, and an explicit `LEAD_RATE_LIMIT_READY=true` attestation after provider-level rate limiting has been verified.

Production origin trust is canonical-only: `LEAD_ALLOWED_ORIGINS=https://aiskillab.work`. The legacy `https://ai-skill-lab.vercel.app` hostname is redirect-only compatibility and must not be trusted by the ingress.

Do not store production secrets in Git. Configure runtime values only in the dedicated ingress project. The public static project must not receive `LEAD_WEBHOOK_SECRET`.

## Request contract

Endpoint: `POST /api/lead`

- `Content-Type: application/json`
- maximum actual request body: 20,000 bytes
- audiences: `adult`, `parent`, `teen`, `business`
- locales: `ru`, `en`
- privacy consent is mandatory
- youth submissions require adult confirmation; a `kids-*` program requires `audience=parent`
- the honeypot field `website` returns success without forwarding
- direct requests without an allowed `Origin` are rejected
- structured operational events are limited to correlation/outcome metadata (`requestId`, status, downstream status); request body, name, contact, goal, Origin, webhook URL, signatures, and secrets are never emitted by custom logs
- no automatic retry is performed, avoiding duplicate lead creation
- downstream timeout: 8 seconds

Successful downstream payloads retain schema `ai-skill-lab.lead.v2` and add `requestId`, `receivedAt`, a privacy-safe `ipToken`, plus optional `sourcePath`. `ipToken` is `HMAC-SHA256(LEAD_WEBHOOK_SECRET, "lead-ip-v1:" + client_ip)`: it is signed as part of the exact downstream JSON body, used only as the receiver rate-limit key, and is not written to the lead table or custom logs.

## Downstream signature

The ingress sends:

- `X-AI-Skill-Lab-Timestamp: <unix-seconds>`
- `X-AI-Skill-Lab-Request-Id: <uuid>`
- `X-AI-Skill-Lab-Signature: v1=<hex>`

The signature is:

`HMAC-SHA256(secret, timestamp + "." + requestId + "." + raw_json_body)`

The receiver must recompute the HMAC over the exact raw body, compare it in constant time, reject stale timestamps, and deduplicate by request ID before accepting the lead.

## Rate limiting

This function deliberately does not use an in-memory counter because serverless instances are not a reliable shared rate-limit store. For a real lead, the ingress requires a valid first address from `X-Forwarded-For`, converts it immediately to the domain-separated HMAC `ipToken`, and never forwards, stores, or custom-logs the raw IP. The signed receiver validates the token shape and calls the existing provider `LEAD_RATE_LIMITER` with `lead:<ipToken>`, so unrelated visitors no longer share one global `lead-intake` bucket. `LEAD_RATE_LIMIT_READY=true` remains the fail-closed attestation that the provider binding has been configured and verified.

## Public activation is separate

This hardening service does not authorize or perform public form activation. The later activation release must separately verify legal operator/jurisdiction, receiver ownership, HMAC readback, rate limiting, the public `/api/lead` rewrite, `connect-src 'self'`, Start/Privacy/Proof content, source/static parity, manifest regeneration, and live delivery.


## F1.5 Telegram FAQ bot

The Telegram FAQ bot is a separate fail-closed webhook route at `POST /api/telegram-faq`. It is disabled unless `TELEGRAM_FAQ_ENABLED=true` and both server-only values are present:

- `TELEGRAM_FAQ_BOT_TOKEN`
- `TELEGRAM_FAQ_WEBHOOK_SECRET` (at least 32 UTF-8 bytes)

The webhook must be registered directly against the dedicated ingress deployment, not the static site. Telegram must send the configured webhook secret in `X-Telegram-Bot-Api-Secret-Token`.

Behavior is deterministic:

- FAQ replies come only from `faq_facts.json`, which is contract-checked against the published RU/EN `/faq` sources.
- `/book` returns the approved AI Skill Lab Start path for the free 15-minute intro.
- `/brief` explains the one-message brief format.
- A brief is forwarded only with explicit `CONSENT`; `parent` and `teen` additionally require `ADULT`.
- The bot reuses the existing lead handler and downstream HMAC/D1/notification pipeline. Telegram retries derive the same UUIDv4 request ID from `update_id`; the receiver's existing request-ID dedupe therefore prevents duplicate lead rows.
- Telegram user ID is transformed with `HMAC-SHA256(LEAD_WEBHOOK_SECRET, "telegram-user-v1:" + user_id)` before it becomes the receiver rate-limit token. The raw Telegram user ID is not written to D1 or custom logs.
- Secret-like text is rejected before FAQ matching or lead forwarding.
- Custom bot logs contain only `updateId`, `status`, and action class; message text, username, chat ID, bot token, webhook secret, lead secret, and brief content are excluded.

Activation is separate from code merge. Creating the BotFather token, setting Vercel production secrets, registering the webhook, enabling `TELEGRAM_FAQ_ENABLED`, and sending a live canary each require an explicit production approval.
