# AI Skill Lab R57 — Global Lab Command Readiness

Date: 2026-08-15
Status: LOCAL RELEASE CANDIDATE — NOT DEPLOYED

## Scope
R57 adds a global native-dialog Lab Command layer to all 38 public routes.

Open paths:
- click the `⌘K` control in the global header;
- press `Ctrl+K` or `⌘K` from anywhere on the page.

The palette links directly to:
- Proof Lab
- Project Studio
- AI Pilot Simulator
- Program Matcher
- Pricing
- Start

The implementation is local-only, same-origin, and performs no fetch, analytics, browser storage, cookies, WebSocket, or model call.

## Accessibility / interaction
- native `<dialog>` top layer
- native focus containment
- native Escape close behavior
- explicit close control
- `aria-haspopup=dialog`
- `aria-controls`
- `aria-keyshortcuts`
- RU/EN locale-aware destinations

## QA
Pre-commit R57 preflight: **41/41 PASS**.

Selected evidence:
- Lab Command parity: 470 PASS across 38 public pages
- Lab Command runtime: 8/8 PASS
- 39 HTML pages including 404
- 38 public routes
- 1,512 internal links
- broken links: 0
- forms: 0
- accessibility: 1,885 PASS
- CTA semantics: 209 PASS
- navigation parity: 837 PASS
- total static payload: 451,629 bytes (< 512 KiB budget)
- CSS: 32,603 bytes (< 32 KiB budget)
- security/CSP/privacy: PASS
- release transport self-test: 47/47 served files byte-for-byte

Pre-commit payload SHA-256:
`f4bef0136d4b58ad290ad3dd8ccbacca2f9c0705ccb2b345a7709452ea8362cf`

Pre-commit archive SHA-256:
`bdfbbc1e501f51e1d58cbe05e8656fd5ae4bae9fe4fab6a470280a565f225f5a`

## Deployment boundary
R57 has NOT been deployed to Vercel.
Last known production remains older R5 deployment `dpl_Gduv8Jv2cvVWBDEht9K1jYPwNtwG`.
Do not deploy before the known Vercel API quota reset at 2026-08-16 17:49:21 Asia/Bangkok.
