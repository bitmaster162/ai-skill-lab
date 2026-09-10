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
- no request-body, contact, goal, secret, or downstream payload logging is implemented
- no automatic retry is performed, avoiding duplicate lead creation
- downstream timeout: 8 seconds

Successful downstream payloads retain schema `ai-skill-lab.lead.v2` and add `requestId`, `receivedAt`, plus optional `sourcePath`.

## Downstream signature

The ingress sends:

- `X-AI-Skill-Lab-Timestamp: <unix-seconds>`
- `X-AI-Skill-Lab-Request-Id: <uuid>`
- `X-AI-Skill-Lab-Signature: v1=<hex>`

The signature is:

`HMAC-SHA256(secret, timestamp + "." + requestId + "." + raw_json_body)`

The receiver must recompute the HMAC over the exact raw body, compare it in constant time, reject stale timestamps, and deduplicate by request ID before accepting the lead.

## Rate limiting

This function deliberately does not use an in-memory counter because serverless instances are not a reliable shared rate-limit store. Public activation is blocked until provider-level rate limiting for `/api/lead` is configured and verified. The exact threshold is an activation-gate decision based on fresh provider capability and expected traffic.

## Public activation is separate

This hardening service does not authorize or perform public form activation. The later activation release must separately verify legal operator/jurisdiction, receiver ownership, HMAC readback, rate limiting, the public `/api/lead` rewrite, `connect-src 'self'`, Start/Privacy/Proof content, source/static parity, manifest regeneration, and live delivery.
