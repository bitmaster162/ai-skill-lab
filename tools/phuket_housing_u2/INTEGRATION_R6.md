# U2 R6 integration: empty inventory only

Owner continuation: `погнали`, following the local U2 prototype. This iteration is local implementation and acceptance only: no push, pull request, merge, deployment, Google Sheet writes, scheduler, agency outreach or D1 changes.

## Verified baseline and source

Remote main: `e61387d816bff7d0b8c9de3317f25914dab88c06`, tree `10a75780ef0a6e6e3a6d138af0ac34a0dc15becf`. Local prototype baseline: `a3354ed2ae57eb95f70d526f67a9c554915e5869`, tree `bbbc01c89e39d2374984da966a6047f976922e07`.

The bounded read of `Untitled!A1:J1000` in the already identified Google Sheet returned the ten-column header and no listings on 2026-10-14. `data/phuket_housing_r6_snapshot.json` records that header-only input; the compiler pins its canonical values hash. No private consent records are committed or served. The empty consent template still has `max_listing_age_days: null`.

This release explicitly refuses a nonempty snapshot, nonempty consent policy or unapproved date. Importing real inventory needs separate consent/freshness decisions, link validation, a new reviewed snapshot and release. The synthetic test rows never become production input. This is not an active agency pilot or a legal approval.

## Integration

The existing offline compiler generates the RU/EN housing sections, a same-origin CSS file and an idempotent external filter script. `PhuketUniverse.tsx` inserts the generated section after applying the unchanged pilot terms. The Next client component loads the local script and requests reinitialization on route mounting; it does not fetch catalogue data, write storage or send analytics.

The static builder independently reproduces R5 from its pinned Git commit, replaces only the two housing sections and adds `phuket-housing-u2.css` and `phuket-housing-u2.js`. R5 CSS, terms, hero/orbit SVG, CSP, existing events, sitemap, llms.txt and all other parent assets remain unchanged. There are still 56 public routes. Removing the obsolete example card leaves seven SVG elements on each empty Universe page rather than eight.

R6 has its own manifest and profile. Old R3/R5 profile JSON files remain byte-identical. Existing release checks explicitly recognize R6 and delegate to its exact inventory and source checks; unknown releases, routes and modified pins are not admitted.

## Offline reproduction and acceptance

From the repository root:

```sh
python -B scripts/build_phuket_housing_release_r6.py
python -B scripts/test_phuket_housing_release_r6.py
python -B scripts/test_phuket_housing_release_r6.py --browser
npm run build
python -B scripts/test_phuket_housing_release_r6.py --next
python -B scripts/preflight_release.py --release PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014
```

Build dependencies must come from the unchanged lockfile. Browser acceptance intercepts requests and blocks real network access; nonempty fixtures are explicitly synthetic. Without JavaScript the page remains readable and filtering is visibly unavailable. With JavaScript rent/sale, district, type, bedrooms, maximum price, empty results and invalid-price states are tested.

Default build/check commands are read-only. Preparation switches only accept the isolated Draft branch and an intact R5 payload; an existing R6 release is not resealed. Generated screenshots, receipts, node_modules and .next output remain ignored.

## Publication boundary

This local integration does not authorize or perform publishing. Public/production acceptance, GitHub CI and any push/PR/merge/deployment require their own explicit step. U3 global navigation, new Universe analytics event types, scheduling and live inventory are outside R6.
