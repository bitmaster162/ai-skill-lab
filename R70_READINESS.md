# AI Skill Lab R70 — Antigravity Synthesis

## Status

**SOURCE_PROTOTYPE_ONLY / NOT RELEASE-READY**

R70 is a separate development epoch. It does not mutate the validated R69 static payload, Vercel Preview, production deployment, `main`, or the merged R69 release branch.

## Verified baseline

- baseline commit: `921681389ed8c372d86f19954c4eb11b8f43edff`
- baseline tree: `2f6fa268ddafbb3c091334e095994a6f9568e112`
- baseline meaning: GitHub merge commit for PR #3 containing the exact validated R69 candidate tree
- R70 branch: `agent/r70-antigravity-synthesis`

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
   - evidence remains bounded to the verified R69 release chain

4. **Progressive typography**
   - `text-wrap: balance` for editorial headings
   - `text-wrap: pretty` for selected prose surfaces
   - no global `color-scheme: dark`

## Accepted R70 P1 source scope

5. **Bounded business capacity scenario**
   - bilingual local-only interactive calculator on RU/EN `/business`
   - user controls team size, routine hours, hourly value and assumed recoverable share
   - formula uses `people × routine hours/week × 52/12 × recoverable share × hourly value`
   - output is explicitly a sensitivity scenario, not a forecast, ROI guarantee or payroll-savings claim
   - no hard-coded assumption that AI automates 50% of work
   - no invented model/API-cost estimate
   - Telegram deep link contains only the user's selected assumptions and scenario result; nothing is sent automatically
   - styles are isolated in `app/r70.css`

## Second Antigravity package — accepted for later static projection

### Full bilingual hreflang sitemap

**ACCEPT, but not the supplied eight-URL sample.**

The validated R69 static sitemap already contains the full current route set. R70 release projection should preserve all current indexable routes and add reciprocal `xhtml:link rel="alternate" hreflang="ru|en"` entries for every real RU/EN pair, including self-references. Do not add fake or incomplete pairs.

- add the `xhtml` sitemap namespace
- emit both RU and EN URL entries
- each paired entry lists both alternatives including itself
- do not rely on `<priority>` or `<changefreq>` as ranking controls
- sitemap generation must remain deterministic and covered by a gate

### AI-search crawler policy

**REVISE, no current robots mutation in source-prototype stage.**

Current R69 `robots.txt` already allows `User-agent: *`, so search crawlers are not intentionally blocked. If R70 later makes crawler-specific groups explicit, distinguish search/retrieval bots from training crawlers:

- OpenAI search: `OAI-SearchBot`
- Anthropic search: `Claude-SearchBot`
- Anthropic user retrieval: `Claude-User`
- Perplexity search: `PerplexityBot`

Do not describe `GPTBot` or `ClaudeBot` as search-index bots. They have different model-development/training purposes. If any crawler-specific group is introduced, duplicate intended path restrictions inside that specific group instead of assuming it inherits the wildcard group.

## Explicitly rejected / deferred from Antigravity proposals

- no service worker / offline cache in R70 P0/P1
- no claim that Lighthouse will be `100/100`
- no claim that structured data guarantees rich snippets
- no Course/FAQ/address/Offer JSON-LD mutation in this slice
- no invented testimonials, ratings, founder metadata, employee counts, or other unsupported schema claims
- no pricing, route, commercial-fact, proof-authority, analytics, cookie, or tracking changes
- no copy-paste of the proposed security `vercel.json`
  - existing static release already has strict CSP, frame blocking, no cross-origin connections and explicit cache policy
  - Vercel supplies HSTS at the platform layer
  - do not add deprecated `X-XSS-Protection`
  - do not mark mutable unhashed CSS/JS as one-year `immutable`
- no `LocalBusiness` schema until a real public business location, postal address, coordinates, business hours and intended public local-business identity are independently verified
- no invented Phuket office hours, coordinates or `priceRange`

## Scope audit after source edits

Compared with baseline `921681389ed8c372d86f19954c4eb11b8f43edff`, R70 source-prototype work is intentionally limited to source/UI/readiness files. The current source delta includes:

- `R70_READINESS.md`
- `app/layout.tsx`
- `app/r69.css`
- `app/r70.css`
- `app/business/page.tsx`
- `app/en/business/page.tsx`
- `components/BriefCompiler.tsx`
- `components/BusinessValueCalculator.tsx`
- `components/ProgramMatcher.tsx`
- `components/ProofLab.tsx`

`deploy/live/**` must remain byte-identical to R69 until the controlled source→static projection gate.

## Gates still required before R70 can become a release candidate

- source TypeScript/build validation
- source behavioral tests for Matcher, Brief Compiler and Business Capacity Telegram URLs
- source accessibility validation of added external links and range controls
- source visual regression for `text-wrap` and Business Capacity UI at desktop and 390px
- decide and implement deterministic full-route hreflang sitemap generation during static projection
- regenerate or deliberately patch static RU/EN surfaces from the approved source delta
- update static CSP hashes if inline scripts change
- update static release manifest and payload SHA
- run full static release gate set
- run browser/visual QA on exact static candidate
- only then create a non-production Preview

No merge, production promotion, Actions rerun, `main` write, or Vercel mutation is authorized by this R70 source-prototype work.
