# AI Skill Lab R27 — Static client runtime repair

- Branch: `agent/r27-static-client-runtime`
- Scope: repair broken inline JavaScript in RU/EN static Program Matcher and add a dependency-free inline-script syntax gate.
- Root cause: deployable static matcher serialized `join("\n")` with a literal newline inside the JS string, producing `SyntaxError: Invalid or unexpected token`. Next `ProgramMatcher.tsx` was already correct.
- Fixed surfaces: `deploy/live/matcher.html`, `deploy/live/en/matcher.html`.
- New gate: `scripts/check_inline_scripts.py`, wired into GitHub Actions workflow.

QA:
- inline scripts: 6 total; 4 JavaScript blocks checked; `INLINE_SCRIPT_SYNTAX_PASS`
- static release: 37 HTML / 36 public routes / 1144 internal links / 0 broken / 0 forms / `STATIC_RELEASE_QA_PASS`
- commercial parity: 388 checks / PASS
- contact funnel: 109 checks / PASS
- navigation parity: 793 checks / PASS
- static accessibility: 1381 checks / PASS
- client privacy: 36 checks / PASS
- launch gate: PASS with expected contact-only/legal-operator warnings
- TypeScript syntax-class diagnostics: TS1xxx = 0
- `git diff --check`: PASS

Browser rendering could not be executed in this sandbox because Chromium navigation to localhost/file URLs is administratively blocked; no visual PASS is claimed from that path.
