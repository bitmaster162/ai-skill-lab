# Phuket Universe U3 + E3.8 — isolated local R7 candidate

**Status:** local preview, not an approved release. No push, PR, merge, deploy, Cloudflare provisioning, D1 migration, Google Sheets edits or Scheduler writes.

## Provenance

- Parent Git main: `3d58999a382b2c11eae7da3d97e9e650c1326f46`
- Parent tree: `34fc913502977cf7a825791725fd8fa97ac93e86`
- Exact parent release: `PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014`
- Parent manifest SHA-256: `5d07745a1220b1da82e224409210635ae83511f6184101671ea24987468b5966`
- Local branch: `agent/phuket-universe-u3-e38-local-r1`

## Scope

U3 adds the orbit-icon **Phuket Universe** footer destination to 54 Workshop pages and the two Universe pages. RU and EN `/phuket` gain one local discovery block with a direct same-locale link. `Footer.tsx` is legacy/unused; the active 54 pages use `WorkshopShell`, and two Universe pages use their own footer markup.

Three new types are identified in the local client: `universe_click` (footer), `project_click` (five approved friends' cards), `listing_click` (future approved property card). **No listing is published or invented**; empty R6 remains empty. The future card marker is applied only by `mark_listing_links`, which fails on missing/duplicate/malformed anchors.

The new external script `public/phuket-universe-events.js` is **hard-disabled** with `const ENABLED = false`. It must not be toggled before a separately approved receiver/ingress/schema release. The mock-only tests enable it in isolated VM memory, not in the shipped file. The only wire body is `{event, page, locale}`; URLs, agency names, prices, listing identifiers, cookies and personal data are excluded. The seven existing contact/lead event names remain unchanged.

## Offline-only database model

`e3_8_sqlite_candidate.sql` is a **reference SQLite migration**, not a Cloudflare D1-ready change. The original D1 schema has a restrictive seven-name `CHECK` clause; adding new names requires a table rebuild and exact preservation of existing counts. Local SQLite tests prove preservation and rejection of unknown events. Actual Cloudflare D1 migration must be separately qualified for D1 transaction behavior, migration ordering, backup/witness strategy, locking, rollback/compensation and live restrictions. Do **not** run the file against production.

Required release sequence: (1) independent migration design and approval; (2) migrate and verify D1 in approved change window; (3) update/test worker and ingress allowlists and deploy with explicit approval; (4) only then build a new approved site release with the client enabled and verify production end-to-end. A failure in any step means HOLD, not partial activation.

## Reproduction and tests

Run from repo root:

```powershell
python -B tools/phuket_universe_u3/test_preview.py
node tools/phuket_universe_u3/test_event_runtime.mjs
python -B tools/phuket_universe_u3/test_browser.py
python -B tools/phuket_universe_u3/preview.py --out deploy/preview/PHUKET_UNIVERSE_U3_E38_LOCAL_R7_20261015
```

The preview is **create-only** and must not overwrite an existing directory. It reproduces all parent R6 file hashes, adds a single disabled client JS asset and modifies exactly the 56 public HTML documents, preserving other inherited bytes and CSP. The preview is not written into `deploy/live`.

Targeted acceptance concerns only this task; full release profile, exact performance and source/static gates, updated manifests and approvals will be required before any PR or production publication.

## Non-goals

No U2 real inventory sync, no automatic update cadence, no new analytics API call in production, no D1 writes, no customer data storage, no third-party SDKs, no fees or claims about agency legal verification. Production remains R6 until a separate approved release.
