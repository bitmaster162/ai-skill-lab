# AI Skill Lab R36 — Microcopy contrast hardening

- Branch: `agent/r36-microcopy-contrast`
- Added `--micro` / `--micro-dark` contrast tokens to static and Next CSS.
- Light microcopy contrast: 5.04–5.42:1 on paper/white.
- Dark microcopy contrast: 5.42–5.84:1 on dark cards.
- Existing muted body token: 4.67:1 on paper.
- Acid microcopy: 5.45:1.
- Contrast token gate: PASS.
- Static release QA: PASS — 37 pages / 36 routes / 1148 links / 0 broken / 0 forms.
- Static performance: 223 PASS — 312,781 bytes payload, 21,351-byte CSS.
- Search metadata PASS; security/CSP PASS; inline JS PASS.
- Matcher runtime 16/16 PASS; Start runtime 44/44 PASS.
- Commercial parity 388 PASS; contact funnel 109 PASS; navigation 793 PASS.
- Accessibility 1397 PASS; client privacy 36 PASS; launch gate PASS.
- R36 static payload SHA-256: `c2a8fa233e58f4b1216d0643db2301c8fc62ea9f09de81787fd4023589080fe6`.
