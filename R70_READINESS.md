# AI Skill Lab R70 — Antigravity Synthesis

## Status

**SOURCE_PROTOTYPE_ONLY / NOT RELEASE-READY**

R70 is a separate development epoch. It does not mutate the validated R69 static payload, Vercel Preview, production deployment, `main`, or the merged R69 release branch.

## Verified baseline

- baseline commit: `921681389ed8c372d86f19954c4eb11b8f43edff`
- baseline tree: `2f6fa268ddafbb3c091334e095994a6f9568e112`
- baseline meaning: GitHub merge commit for PR #3 containing the exact validated R69 candidate tree
- R70 branch: `agent/r70-antigravity-synthesis`
- evidence-hardening authority base: `a38eeaa7c79084b9ac2a5079d16336863255417f`

## Accepted R70 P0 scope

1. **Program Matcher Telegram dispatcher**
   - reuses the existing deterministic local brief
   - creates a `https://t.me/BiTFormer?text=...` deep link only after a recommendation exists
   - no automatic send, analytics, cookies, first-party form, or server-side storage
   - copy brief and program/start routes remain available

2. **Brief Compiler Telegram dispatcher**
   - reuses the existing local human-gated brief
   - opens Telegram with the current compiled brief prefilled
   - no automatic send or remote persistence

3. **Real R69 Evidence Diff in Proof Lab**
   - no fabricated API or synthetic customer case
   - records the actual R69 dark-price contrast defect, human release gate, repaired CSS identity, final payload SHA, and merge tree
   - evidence remains bounded to the verified R69 candidate chain
   - public wording uses `validated candidate`, not a false R69 production claim

4. **Progressive typography**
   - `text-wrap: balance` for editorial headings
   - `text-wrap: pretty` for selected prose surfaces
   - no global `color-scheme: dark`
   - R70 typography remains isolated from frozen `app/r69.css`

## Accepted R70 P1 source scope

5. **Bounded business capacity scenario**
   - bilingual local-only interactive calculator on RU/EN `/business`
   - user controls team size, routine hours, hourly value and assumed recoverable share
   - formula uses `people × routine hours/week × 52/12 × recoverable share × hourly value`
   - output is explicitly a sensitivity scenario, not a forecast, ROI guarantee or payroll-savings claim
   - no hard-coded assumption that AI automates 50% of work
   - no invented model/API-cost estimate
   - Telegram deep link contains only the user's selected assumptions, scenario result, and a short status line; the long on-page disclaimer is not inserted into the Telegram payload
   - nothing is sent automatically
   - styles are isolated in `app/r70.css`

## Evidence hardening after multi-agent adjudication

The R70 source review used Antigravity A1, Claude C1, direct canonical-source readback and independent arithmetic adjudication. Neither external report is treated as authority by itself.

### Corrected calculator determinism gate

Added `scripts/check_r70_business_calculator.mjs`.

The gate:

- binds itself to the current `BusinessValueCalculator.tsx` formula and slider-bound source contracts
- uses 20 reachable UI vectors
- checks UI bounds and step alignment
- checks finite arithmetic outputs
- uses corrected expected values for the three vectors that were wrong in the earlier Antigravity proposal:
  - `(18,14,75,45) -> 36855`
  - `(7,9,55,25) -> 3753.75`
  - `(11,22,65,35) -> 23857.166666666668`
- prints `R70_BUSINESS_CALCULATOR_DETERMINISM_PASS` only if all checks actually execute successfully

**Important evidence boundary:** the new gate is now present in canonical source, but its PASS token must not be claimed until raw execution output and exit code `0` are retained.

### Runtime-harness portability

The following inherited test harnesses used filesystem roots derived from `new URL(import.meta.url).pathname`, which is unsafe for Windows drive-letter paths and URL-percent-encoded checkout paths:

- `scripts/check_matcher_runtime.mjs`
- `scripts/check_brief_compiler_runtime.mjs`
- `scripts/check_pilot_simulator_runtime.mjs`

They now use `fileURLToPath(import.meta.url)` before converting to a filesystem path.

Classification:

- inherited verification-tool debt, not an R70 product regression
- no shipped static/runtime behavior changed by this repair
- the repaired gates still require actual execution evidence before being called green

### Adjudication corrections retained

- no `2000` percent-encoded Telegram URL gate is adopted
- no hard-coded Telegram protocol budget is introduced into repository truth
- no 320px padding change is made without measured overflow evidence
- no accessibility failure is inferred merely from absence of a custom range `:focus-visible` rule; actual visible-focus behavior remains a browser/AT verification item
- `aria-live` behavior remains a browser/AT verification item rather than a source-only PASS
- no service worker / PWA is introduced
- no security header is weakened

## Search / crawler conclusions

### Hreflang sitemap

**REJECT AS REDUNDANT FOR CURRENT ARCHITECTURE.**

The validated static pages already carry reciprocal RU/EN/`x-default` `<link rel="alternate" hreflang="…">` tags and `scripts/check_search_metadata.py` enforces them for every public page. Google treats HTML hreflang, HTTP-header hreflang and sitemap hreflang as equivalent methods and states that implementing multiple methods provides no Search benefit while increasing maintenance complexity.

Therefore R70 keeps:

- full sitemap route coverage through `sitemap.xml`
- HTML `<head>` hreflang as the single localization authority
- deterministic parity checks between actual public HTML routes and sitemap URLs
- no `<priority>` / `<changefreq>` ranking claims

Do not add a second hreflang implementation unless a concrete operational reason appears later.

### AI-search crawler policy

**REVISE, no current robots mutation in source-prototype stage.**

Current R69 `robots.txt` already allows `User-agent: *`, so search crawlers are not intentionally blocked. If R70 later makes crawler-specific groups explicit, distinguish search/retrieval bots from training crawlers and re-verify current official owner documentation at that time.

Do not introduce crawler-specific groups unless they solve a concrete operational problem. If any specific group is introduced, duplicate intended path restrictions inside that group instead of assuming inheritance from the wildcard group.

## Explicitly rejected / deferred from external proposals

- no service worker / offline cache in R70 P0/P1
- no claim that Lighthouse will be `100/100`
- no claim that structured data guarantees rich snippets
- no Course/FAQ/address/Offer JSON-LD mutation in this slice
- no invented testimonials, ratings, founder metadata, employee counts, or other unsupported schema claims
- no pricing, route, proof-authority, analytics, cookie, or tracking changes
- no copy-paste of the proposed security `vercel.json`
  - existing static release already has strict CSP, frame blocking, no cross-origin connections and explicit cache policy
  - do not add deprecated `X-XSS-Protection`
  - do not mark mutable unhashed CSS/JS as one-year `immutable`
- no `LocalBusiness` schema until a real public business location, postal address, coordinates, business hours and intended public local-business identity are independently verified
- no invented Phuket office hours, coordinates or `priceRange`

## Current R70 delta scope

Compared with baseline `921681389ed8c372d86f19954c4eb11b8f43edff`, the intended R70 source/tooling delta is bounded to:

### Product/source/readiness

- `R70_READINESS.md`
- `app/layout.tsx`
- `app/r70.css`
- `app/business/page.tsx`
- `app/en/business/page.tsx`
- `components/BriefCompiler.tsx`
- `components/BusinessValueCalculator.tsx`
- `components/ProgramMatcher.tsx`
- `components/ProofLab.tsx`

### Evidence/test hardening

- `scripts/check_r70_business_calculator.mjs`
- `scripts/check_matcher_runtime.mjs`
- `scripts/check_brief_compiler_runtime.mjs`
- `scripts/check_pilot_simulator_runtime.mjs`

`app/r69.css` is expected to remain byte-identical to the R69 baseline and is not part of the intended R70 delta.

`deploy/live/**` must remain byte-identical to R69 until the controlled source→static projection gate.

## Gates still required before source→static projection

- fresh source authority receipt for the exact projection input HEAD/tree
- raw `npm run build` output, environment versions, and exit code `0`
- execute `scripts/check_r70_business_calculator.mjs` and retain raw PASS output + exit code `0`
- re-run relevant source/runtime verification gates after the portability repair and retain raw output
- source behavioral verification for Matcher, Brief Compiler and Business Capacity Telegram URLs
- source accessibility/browser verification for external links, native range focus, live-region behavior, reduced motion, zoom/reflow and horizontal overflow
- source visual regression for `text-wrap` and Business Capacity UI across desktop and narrow mobile viewports
- complete the independent Manus/Gemini/Claude/tournament adjudication lane before freezing the design direction

## Future controlled source→static projection gate

Projection is a later, separately evidenced phase. When authorized:

1. freeze the exact source HEAD/tree
2. regenerate or deliberately patch static RU/EN surfaces from the approved source delta
3. rebuild CSP hashes from the actual inline scripts present in `deploy/live/**/*.html`
4. preserve `connect-src 'none'`, `form-action 'none'`, `worker-src 'none'`, `frame-ancestors 'none'` and absence of `unsafe-inline`
5. regenerate static release manifest, file sizes and payload SHA
6. run the full static release gate set
7. run exact browser/visual QA on the static candidate
8. only then create an isolated non-production Preview
9. perform served-byte/readback verification against that exact Preview

CSP hash rotation is mandatory during projection if projected inline-script bytes change; it is not a reason to mutate the still-frozen R69 static layer during source hardening.

No merge, production promotion, Actions rerun, `main` write, static projection, Preview creation, or Vercel mutation is authorized by this evidence-hardening batch.
