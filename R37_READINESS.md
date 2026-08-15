# AI Skill Lab R37 — One-command release preflight

- Branch: `agent/r37-release-preflight`
- Added `scripts/preflight_release.py` to rebuild CSP + release manifest and execute the complete static release gate in one command.
- Preflight gates: 17/17 PASS.
- Static release: 37 HTML / 36 public routes / 1148 internal links / 0 broken / 0 forms.
- Search metadata: PASS.
- CSP/security: PASS.
- Performance: 223 PASS; total deploy payload 312,781 bytes; CSS 21,351 bytes.
- Contrast: PASS (light micro 5.04–5.42:1; dark micro 5.42–5.84:1).
- Inline JS syntax: PASS.
- Matcher runtime: 16/16 PASS.
- Start runtime: 44/44 PASS.
- Commercial parity: 388 PASS.
- Contact funnel: 109 PASS.
- Navigation parity: 793 PASS.
- Accessibility: 1397 PASS.
- Client privacy: 36 PASS.
- Launch gate: PASS with expected contact-only/legal-operator warnings.
- Static payload SHA-256: `c2a8fa233e58f4b1216d0643db2301c8fc62ea9f09de81787fd4023589080fe6`.
