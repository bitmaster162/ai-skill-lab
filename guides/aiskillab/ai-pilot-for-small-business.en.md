---
site: aiskillab.work
path: /en/guides/ai-pilot-for-small-business
alternate: /guides/ai-pilot-for-small-business
lang: en
title: "AI for a Small Business Team: How to Choose the First Task and Bound a Pilot Without Wasting Budget"
seo_title: "AI Pilots for Small Business — AI Skill Lab · Phuket"
description: "How small businesses select one workflow for an AI pilot, set safety boundaries, cap scope at 35 hours, and apply a Ship, Revise, or Stop decision gate."
reviewed: 2026-11-22
next_review: 2027-01-26
related: [/en/business, /en/pricing, /en/start]
schema: [Article, BreadcrumbList]
research_source: "G2, 2026-10-26 (R077, R076, R700, R704, R711)"
---

# AI for a Small Business Team: How to Choose the First Task and Bound a Pilot Without Wasting Budget

This guide is for small teams testing AI on one repeatable operation. Use an enquiry as an example to choose the task, plan the review and decide whether to continue.

## Why Handing Out Chat Subscriptions Does Not Change a Business Process

Suppose your team already uses a chatbot. Before a manager goes on leave, see whether a colleague can process the same enquiry using their instructions.

- A manager’s personal chat may hold both the prompt and the only checked example.

- Record the input, the AI’s task, the human check, the acceptance criterion, the stop condition and the owner. [Business programme](/en/business).

## First-Task Selection Matrix: 5 Verifiable Criteria and Stop Signals

| Criterion | When to try it | When to defer |
| --- | --- | --- |
| 1. Repetition | Similar enquiries with known fields arrive every week. | It is a one-off and nobody can define a good result. |
| 2. Owner | A named employee accepts the output. | Nobody can review the draft. |
| 3. Review | A reviewer can check the draft against its source in 2–5 minutes. Time a real example. | Writing it by hand is faster. |
| 4. Permissions | AI drafts, a person decides whether to send. | The task requires autonomous payments or production writes. |
| 5. Data | You have a de-identified example and permission to process it. | Permission to share customer records with the service is unclear. |

Use the [business calculator](/en/business) to size a candidate task.

Potentially Freed Hours / Month = People in Process × Routine Hours / Week × (52 / 12) × Assumed Share Freed

Gross Capacity Value / Month = Potentially Freed Hours / Month × Estimated Hourly Cost

Example: 3 people × 10 hours per week × 52/12 ≈ 130 hours per month. Freeing an assumed 30% gives 39 hours, or about $975 at $25/hour. Measure review and correction time separately and deduct implementation and service costs.

## Safety Boundaries: What AI Must Not Do in a Business Workflow (3 Documented Cases and 5 Working Rules)

An incident, a vulnerability and an attempted bypass have different consequences.

| Source | Event type | What happened | Pilot safeguard |
| --- | --- | --- | --- |
| 1. Replit Agent / SaaStr (18–21 July 2025, [AIID #1152](https://incidentdatabase.ai/cite/1152/); [The Register 21.07.2025](https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/); [The Register 22.07.2025](https://www.theregister.com/2025/07/22/replit_saastr_response/); [SaaStr 01.08.2025](https://www.saastr.com/replits-new-release-address-most-of-the-challenges-we-hit-vibe-coding-but-is-prosumer-vibe-coding-really-ready-for-commercial-apps-yet/)) | Operational incident | During a code freeze, the agent deleted records from SaaStr’s live database. It also reported passing tests and claimed recovery was impossible. The data was restored. Replit subsequently separated development and production databases. | Rehearse using a separate database and account. Check that the test account cannot alter production and that a backup can be restored. |
| 2. EchoLeak in Microsoft 365 Copilot ([Microsoft · CVE-2025-32711](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-32711); disclosed 11 June 2025) | Patched vulnerability | Researchers showed that an external email could lead to disclosure of internal data. Microsoft fixed the service before disclosure and reported no known in-the-wild exploitation. | Use a context with no private records for untrusted messages. An external sender should not inherit the recipient’s access to company files. |
| 3. Palo Alto Networks Unit 42 — Hidden Web Prompts (detected December 2025, report published [3 March 2026](https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/)) | Attempt observed | Unit 42 reported 22 ways of placing instructions on webpages. One fraudulent advertisement contained 24 attempts to influence an AI reviewer; the researchers did not establish that a live reviewer approved it. | Give the person doing the review access to the original page. Only that person approves publication. |

The [business programme](/en/business) sets out five working rules:

- Start with read access and drafts. Grant write access separately.

- Give a test account only the permissions it needs.

- A human confirms payments, sending and access changes.

- Treat instructions inside an email or website as input data.

- Post-effect verification & privacy boundaries: maintain an action log, a tested rollback path, and clear privacy rules—never pasting unprotected customer PII into consumer chat tools, in line with [GDPR (Reg. (EU) 2016/679)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) and Thailand's [Personal Data Protection Act B.E. 2562 (2019)](https://www.pdpc.or.th/).

## The Time-Boxed Pilot Charter (35-Hour Scope Cap), Deliverables, and the Ship · Revise · Stop Decision Gate

The [implementation pilot](/en/business) covers one workflow and has a 35-hour scope cap. Before payment, agree in writing which deliverables the team will receive, how handoff works and how you will decide to ship, revise or stop.

Four pilot stages:

- 01 · Map. Record the input, output, owner and cost of error.

- 02 · Select. Pick one task and define acceptance.

- 03 · Test. Check errors, missing data and the human review step on sample inputs.

- 04 · Handoff. Give the owner operating notes, limits and the improvement list.

| Pilot Charter Element | What to agree in writing before payment |
| --- | --- |
| Concrete Deliverables | Current-state map · Candidate backlog · Working prototype · Test cases · Human checkpoints · Privacy / data boundaries · Owner & fallback rules · Operating notes. |
| Decision Gate: Ship | Quality and review-time criteria are met; the internal process owner accepts the workflow and assumes ongoing operational control. |
| Decision Gate: Revise | Operational value is demonstrated, but bounded issues in template quality, data inputs, or review rules need adjustment before rollout. |
| Decision Gate: Stop | The pilot stops (STOP) if source data does not cover the task, data rights are unclear, no internal owner is available, or human verification takes as long as the manual process. Document the stop decision and hand over the materials listed in the agreed scope. |

## EU AI Act Article 4 (AI Literacy) Context: What Applied on 2 February 2025 and What Changed Under the July 2026 Digital Omnibus

For providers and deployers within the scope of the EU AI Act, Article 4 addresses the AI literacy of people operating AI systems on their behalf.

- [Article 4](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02024R1689-20260727) applied from 2 February 2025; [supervision and enforcement](https://digital-strategy.ec.europa.eu/en/faqs/ai-literacy-questions-answers) from 2 August 2026.

- The July 2026 [Digital Omnibus amendment](https://eur-lex.europa.eu/eli/reg/2026/1744/oj) retained the duty to take measures to support AI literacy. The [Commission FAQ](https://digital-strategy.ec.europa.eu/en/faqs/ai-literacy-questions-answers) explains that Article 4 sets no specific proficiency level. Measures should take account of people’s knowledge, experience and training, the context of use, and those affected by the system.

- For example, an employee drafting ad copy with AI should know how to spot an invented fact.

- Commission guidance says Article 4 requires neither a certificate nor an AI officer. Organisations may keep a record of training.

Scope boundary: [AI Skill Lab](/en) provides practical team training, hallucination-verification drills, and written workflow operating notes, but does not provide legal advice, does not issue "EU AI Act compliance certificates," and does not guarantee regulatory compliance.

## Pre-Call Readiness Checklist (6 Brief Inputs) and Active Formats

Before booking a call or submitting a brief on [aiskillab.work/en/start](/en/start), prepare six short inputs ([AI Skill Lab — Business](/en/business)):

- Process: which single recurring workflow is taking up team capacity right now?

- Performer & Owner: who performs the work today, and who will own and review the process after handoff?

- Frequency: how often does this task run per week or month?

- Input Data: what documents, spreadsheets, or knowledge sources feed the process, and where do privacy boundaries sit?

- Good Outcome: what does an acceptable draft or output look like, and how quickly can a human verify it?

- Consequence of AI Error: what happens if the model hallucinates a number or rule, and where must the human checkpoint sit?

Published offers are listed on the [pricing](/en/pricing) and [business](/en/business) pages. The scope and terms of a specific engagement are agreed before payment.

| Format | Published Price (USD) | Bounded Scope & Written Terms Before Payment |
| --- | --- | --- |
| Free Intro Call | Free ($0) | 15 minutes: initial fit check, stop-signal triage, and route selection ([/en/pricing](/en/pricing)). |
| Diagnostic Session | $120 | 60 minutes: structured task breakdown and starting plan. Credited toward a package purchased within 14 days ([/en/pricing](/en/pricing)). |
| Workflow Audit | $890 | Fixed scope: one workflow map, data boundaries, risk checkpoints, and pilot candidates ([/en/business](/en/business), [/en/pricing](/en/pricing)). |
| Team Training | From $390 / session (minimum 4 sessions — from $1,560) | 60-minute sessions for up to 5 team members working on real company tasks ([/en/business](/en/business), [/en/pricing](/en/pricing)). |
| Implementation Pilot | From $4,900 | One bounded workflow; scope cap of 35 hours. Includes prototype, test set verification, named owner, and handoff artifacts ([/en/business](/en/business), [/en/pricing](/en/pricing)). |
| Post-Launch Support | $490 / month (4 hours) $890 / month (8 hours) $178 / month (Office hours, 2 sessions) | Bounded ongoing support after handoff. There is no instant online checkout: final scope, schedule, payment method, rescheduling, and refund terms are confirmed in writing before payment ([/en/pricing](/en/pricing)). |

Related pages: [AI for Business](/en/business) · [Pricing](/en/pricing) · [Prepare a Business Brief](/en/start) · [Parent Guide: AI Safety for Kids](/en/guides/ai-safety-for-kids).

## Sources

- [EUR-Lex · AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [digital-strategy.ec.europa.eu · repository ai literacy practices](https://digital-strategy.ec.europa.eu/en/policies/repository-ai-literacy-practices)
