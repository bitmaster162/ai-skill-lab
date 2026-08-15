# AI Skill Lab R32 — Search metadata integrity

- Branch: `agent/r32-search-metadata-integrity`
- Scope: deterministic search/share metadata parity for the deployable static release and matching Next metadata on Business, Matcher and Start RU/EN.
- New gate: `scripts/check_search_metadata.py`
- Fixes: missing page-specific Twitter title/description/image on 6 routes.
- Search metadata: PASS — 37 HTML pages, 36 public routes, sitemap 36 exact.
- Static release QA: PASS — 37 pages, 36 routes, 1148 internal links, 0 broken, 0 forms.
- Inline script syntax: PASS.
- Matcher runtime smoke: 16/16 PASS.
- Start runtime smoke: 24/24 PASS.
- Commercial parity: 388 PASS.
- Contact funnel: 109 PASS.
- Navigation parity: 793 PASS.
- Accessibility: 1389 PASS.
- Client privacy: 36 PASS.
- Launch gate: PASS with expected contact-only/legal-operator warnings.
- R32 static payload SHA-256: `1d3ad42d9462a6985a929aeef81849b0bd358f49eee0d514f79932c974ac529e`.
