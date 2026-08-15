# AI Skill Lab R30 — Start brief runtime smoke

- Branch: `agent/r30-start-runtime-smoke`
- Adds `scripts/check_start_runtime.mjs` and CI coverage for RU/EN Start copy-brief behavior.
- All four Start cards are exercised per locale, including copied heading, route title, all brief fields and line count.

QA:
- Start runtime smoke: 24/24 PASS across RU/EN
- Matcher runtime smoke: 16/16 PASS
- Inline JS syntax: PASS
- Static release: 37 HTML / 36 routes / 1148 links / 0 broken / 0 forms / PASS
- Commercial parity: 388 PASS
- Contact funnel: 109 PASS
- Navigation parity: 793 PASS
- Accessibility: 1385 PASS
- Client privacy: 36 PASS
- Launch gate: PASS with expected warnings
- git diff check: PASS
