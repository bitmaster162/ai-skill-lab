# Phuket Universe U2 — local catalogue prototype

## Scope and baseline

Owner continuation: `дальше`, after PR #230 R5 publication. Local implementation and item acceptance only. No push, PR, merge, deploy, scheduler, D1, outreach or Google Sheet writes.

Verified baseline: `e61387d816bff7d0b8c9de3317f25914dab88c06`; tree `10a75780ef0a6e6e3a6d138af0ac34a0dc15becf`. Worktree branch: `agent/phuket-universe-u2-local-r1`.

All implementation is isolated in this directory. Existing Next components, published `deploy/live`, release profile, CSP, R5 agency terms, dependency locks and external services stay unchanged. Generated local previews are NOT a release-qualified deployment and are not integrated into Next or release workflows yet.

## Source and import

Read-only source: Google Sheet `Phuket Universe — жильё`, ID `11iA3xEUH8_VKBHeNKb-6ZDTao2uVfpCLgiBun21oZeQ`, tab `Untitled`. A bounded read of `A1:J1000` on 2026-10-14 returned the header only. No real listings or agency consents have been obtained or invented.

Exact columns: `deal,area,type,bedrooms,price_thb,title,source_name,source_url,updated_at,partner_ok`.

`catalog.py` consumes a local snapshot of Sheets values (`{"values":[...]}`) or UTF-8 CSV. It makes no Google or agency requests. Snapshot acquisition is a separate authenticated connector read; continuous synchronization and daily deployment are NOT implemented.

Formats: rent/sale (also their Russian labels); seven district keys or exact RU/EN map names; condo/apartment, villa, house; non-negative integer bedrooms (0 = studio); positive plain THB amount with at most two decimals; ISO calendar date `YYYY-MM-DD`. Ambiguous formatted prices, date serials, unknown districts/types and future dates are excluded, not guessed.

Rental rows lack a billing-period field. The card displays THB and explicitly directs readers to the source for the period; it does not invent monthly/nightly rates. Supporting period-specific filtering later requires an explicit source contract.

## Consent and freshness boundaries

`partner_ok` must be the exact string `yes`; it alone is insufficient. A private operator-controlled registry must also bind exact agency name and domain to confirmed consent, its evidence SHA-256, permitted fields, terms-copy hash and validity dates. Subdomains are not implicitly allowed. Revoked, missing, expired or out-of-scope records cannot appear.

The registry is an input assertion by the operator, NOT a cryptographic proof that the real agency consented and NOT a legal opinion. Verify and retain original evidence privately before marking a record confirmed. This prototype neither creates nor verifies original consent documents. Its input is pinned using `--policy-sha` to prevent unnoticed policy edits during the local build.

The checked-in template intentionally contains no consents and `max_listing_age_days: null`. Without an explicit freshness setting, nonempty inventory is excluded. No 30/45-day SLA, 90-day pilot, agency quota, listing cap, paid plan or short-term eligibility has been adopted from the research recommendations. The 1 MiB / 1000-row bounds are technical ingestion limits, not commercial entitlements. Rental duration is unresolved; no short-stay eligibility claim is made.

Registry entries require `domain`, `source_name`, `status: confirmed`, `evidence_sha256`, `terms_sha256`, `fields` (the nine publishable source columns), `granted_on`, and `valid_through`. Keep the original evidence, representatives and contacts out of the repository and public output. The compiler emits neither consent details nor rejected raw rows.

HTTPS URLs require a normal DNS hostname, no credentials, private/IP host, nonstandard port, fragments or controls. Only the query keys `id`, `listing_id`, `property_id`, `lang` are admitted initially. Unknown URL formats are quarantined for review, not followed. This is not a live reachability verifier.

Exact duplicate source records collapse. Conflicting duplicates from the same agency/source/deal are all excluded. Different agencies remain separate; no speculative property matching. Order is deterministic by update date and an opaque record key.

## UI

Static cards contain only escaped text, the existing island outline with the district marker, price, source date and a direct `rel="noopener"` link. No photos, enquiry forms, personal-data payload or inline script/style.

Without JavaScript all admitted cards are readable, with disabled filter controls and a visible explanation. JavaScript enables local rent/sale, district, property type, bedrooms and price filtering; zero results and invalid-price states are accessible. No browser fetch, URL/query change, storage, new analytics event or Google request. The R5 hero SVG and agency terms remain unchanged. The old illustrative listing card is removed from the local candidate, including its bracketed placeholders.

## Reproducible local use

Run from the repository root:

```sh
python -B tools/phuket_housing_u2/test_catalog.py
node --check tools/phuket_housing_u2/filters.js
python -B tools/phuket_housing_u2/test_browser.py
```

The browser test uses the installed Python Playwright and an isolated Edge process, with every request intercepted. All nonempty rows and consents in tests are synthetic and remain in memory. Screenshots, when produced, are labelled synthetic in their filenames under ignored `review/u2_housing/`.

A preview build requires committed clean local source, private input and policy, explicit as-of date, the canonical policy SHA-256 and a new directory under `deploy/preview`. Example argument layout (substitute the independently verified policy digest):

```sh
python -B tools/phuket_housing_u2/preview.py --input review/u2_housing/sheet-values.json --policy tools/phuket_housing_u2/policy-template.json --policy-sha DIGEST --as-of 2026-10-14 --out deploy/preview/PHUKET_UNIVERSE_U2_LOCAL_R1_20261014
```

The policy digest is SHA-256 of UTF-8 JSON with sorted keys, no ASCII escaping and compact separators (see `canonical`). Output is create-only with the manifest last. It cannot write `deploy/live` or an existing preview. Error logs contain categorical exclusion reasons, not raw rejected data.

## Still required before production

Next/source/static integration and a new explicitly reviewed release; actual consent evidence and an approved freshness policy for real inventory; source-link verification; remote CI and publication approvals. U3 global navigation and the new Universe event types are not part of this item.
