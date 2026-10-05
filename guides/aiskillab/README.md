# AI Skill Lab guide translation contract · T1.4

AI Skill Lab guides are authored and fact-checked in Russian first. GPT produces the English pair from the reviewed Russian source. Do not retranslate guide pairs that were already supplied in both languages, including the E2 `ai-safety-for-kids` pair.

## File pair and frontmatter

For a reviewed source `<slug>.ru.md`, place the translation beside it as `<slug>.en.md`.

RU template:

```yaml
---
site: aiskillab.work
path: /guides/<slug>
alternate: /en/guides/<slug>
lang: ru
title: "..."
seo_title: "..."
description: "..."
reviewed: YYYY-MM-DD
next_review: YYYY-MM-DD
sources: [...]
schema: [...]
---
```

EN pair:

```yaml
---
site: aiskillab.work
path: /en/guides/<slug>
alternate: /guides/<slug>
lang: en
title: "..."
seo_title: "..."
description: "..."
reviewed: YYYY-MM-DD
next_review: YYYY-MM-DD
sources: [...]
schema: [...]
---
```

If a field exists in the source, keep `reviewed`, `next_review`, `sources` and `schema` unchanged. Translate `title`, `seo_title` and `description`; keep `seo_title` at 60 characters or fewer and `description` at 160 characters or fewer.

## Translation rules · T1.2

- Do not add or remove facts, numbers, dates, examples, sources, caveats or disclaimers. Do not add new advice.
- A paraphrase of an English-language source must not become a quotation unless the wording was checked verbatim against that source.
- Keep product and protocol terminology as documented: API key, IP allowlist, sub-account, Ed25519, HMAC, `countdownCancelAll`, DCP.
- Keep BitEvo terms unchanged when they appear: Authority Budget, Evidence Before Effect, False Green.
- Use plain English and short sentences. Use British spelling, for example `summarised` and `behaviour`.
- Render prose dates as `2 October 2026`.
- Replace links to RU pages with their EN pairs when an EN pair exists. External source URLs must remain the same.
- Keep the same Markdown structure: H2 count, H3 count, table-row count and list-item count.
- The translated pair must contain the same URL set after RU/EN internal route normalisation.
- The translated pair must contain the same number set after dates are normalised to `YYYY-MM-DD`.

## Acceptance

Run:

```powershell
python guides/aiskillab/check_translation_parity.py
```

A passing report prints one line per RU/EN pair with the structural counts and ends with:

```text
T1_4_TRANSLATION_PARITY_PASS pairs=<n> mismatches=0
```

Any mismatch is a release blocker. The checker is structural: it does not certify factual accuracy or translation quality; those remain properties of the reviewed source and the translation workflow.
