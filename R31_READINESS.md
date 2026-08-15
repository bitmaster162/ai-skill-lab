# AI Skill Lab R31 — Start progressive fallback

- Branch: `agent/r31-start-progressive-fallback`
- Parent: R30 Start runtime smoke.
- Adds explicit no-JavaScript fallback on RU/EN Start pages in both Next source and deployable static release.
- If client JavaScript is unavailable, copy buttons are explained as unavailable and the user still has a direct Telegram path plus readable brief fields.

QA:
- Start runtime smoke: 24/24 PASS
- Matcher runtime smoke: 16/16 PASS
- Inline JavaScript syntax: PASS
- Static release: 37 HTML / 36 public routes / 1148 internal links / 0 broken / 0 forms / PASS
- Commercial parity: 388 PASS
- Contact funnel: 109 PASS
- Navigation parity: 793 PASS
- Accessibility: 1389 PASS
- Client privacy: 36 PASS
- Launch gate: PASS with expected contact-only/legal-operator warnings
- TS1xxx: 0
- git diff check: PASS
- static payload SHA-256: `b0c98d6a51ea55f548edf6257f971ffad1a3f5ef23a7b7c71c0d6a2d338a7ecf`

Visual Chromium navigation could not be executed in this sandbox because localhost/file navigation is administratively blocked; no browser-rendering PASS is claimed.
