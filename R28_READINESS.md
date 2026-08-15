# AI Skill Lab R28 — Matcher runtime smoke

- Branch: `agent/r28-matcher-runtime-smoke`
- Parent: R27 static client runtime repair.
- Adds `scripts/check_matcher_runtime.mjs`, a dependency-free VM/DOM smoke harness for the deployable RU/EN matcher scripts.
- CI now checks inline JavaScript syntax and matcher behavior, not only HTML/link integrity.

Runtime smoke scenarios on both RU and EN static matcher pages:
- adult + research + core -> `Personal` / `$890`
- copied brief contains recommendation, price and line breaks
- reset restores empty recommendation state
- business + team + deep -> `Business workflow pilot` / `Custom scope`

QA:
- matcher runtime: 16 checks / 2 pages / `MATCHER_RUNTIME_SMOKE_PASS`
- inline JavaScript syntax: PASS
- static release: 37 HTML / 36 routes / 1144 links / 0 broken / 0 forms / PASS
- commercial parity: 388 PASS
- contact funnel: 109 PASS
- navigation parity: 793 PASS
- accessibility: 1381 PASS
- client privacy: 36 PASS
- launch gate: PASS with expected warnings
- git diff check: PASS
