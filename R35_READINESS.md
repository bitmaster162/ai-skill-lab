# AI Skill Lab R35 — Static performance budget

- Branch: `agent/r35-static-performance-budget`
- New gate: `scripts/check_static_performance.py`.
- Deployable payload excluding `_release.json`: 312,476 bytes.
- `style.css`: 21,046 bytes.
- Budget: total <= 512 KiB, CSS <= 32 KiB, each HTML <= 24 KiB, each raster image <= 128 KiB, inline script bytes/page <= 24 KiB.
- Third-party stylesheet/script/font/image/frame subresources: 0.
- Performance checks: 223 PASS.
- Static release QA: PASS — 37 pages / 36 routes / 1148 links / 0 broken / 0 forms.
- Search metadata PASS; security/CSP PASS; inline JS PASS.
- Matcher runtime 16/16 PASS; Start runtime 44/44 PASS.
- Commercial parity 388 PASS; contact funnel 109 PASS; navigation 793 PASS.
- Accessibility 1397 PASS; client privacy 36 PASS; launch gate PASS.
- Deployable payload is unchanged from R34: `c1035bb7d3207ff2fcab1bfb385000f888e6d6f31391c66c9fe652dd5456fe6b`.
