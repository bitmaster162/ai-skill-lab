---
site: aiskillab.work
path: /en/guides/ai-start-for-adults
alternate: /guides/ai-start-for-adults
lang: en
title: "AI From Scratch for Adults: How to Assess Your Skills and Choose a Practical Learning Track"
seo_title: "AI for Adults: Choosing a Track — AI Skill Lab · Phuket"
description: "Assess your AI skills across five dimensions, compare learning tracks and choose one real task to practise and verify in 1:1 sessions."
reviewed: 2026-11-22
next_review: 2027-01-27
related: [/en/personal, /en/curriculum, /en/pricing, /en/start]
schema: [Article, BreadcrumbList]
research_source: "G3, 2026-10-27 (R077, R076, R700, R286)"
---

# AI From Scratch for Adults: How to Assess Your Skills and Choose a Practical Learning Track

For adults learning to use AI at work: pick one skill to test and match it to a learning track.

## Why "Just Chatting With a Bot" Fails at Work: The 5 Dimensions of AI Fluency

Choose a recent task, its inputs and the model’s answer. What did you verify and what did you correct?

The [AISA Rubric](https://aisa.to/resources/the-aisa-rubric), published by Ozan Dagdeviren on 15 January 2026, scores 11 criteria across five dimensions on a 1–10 scale. [Anthropic](https://www.anthropic.com/research/AI-fluency-index) examined observable behaviours in 9830 Claude conversations. AISA reported 93% overlap in [its own comparison](https://aisa.to/blog/anthropic-ai-fluency-index-comparison). The [U.S. Department of Labor framework](https://www.dol.gov/agencies/eta/advisories/ten-07-25) provides separate guidance for educators.

| AISA dimension | Weight | What the criteria cover | Example for self-assessment |
| --- | --- | --- | --- |
| 1. Prompting & Communication | 23% | P1 Prompt design, P2 dialogue and revision, P3 context and memory | Set the audience, constraints and output format; refine the first answer. |
| 2. Critical Thinking | 22% | T1 Evaluating an output, T2 recognising model limitations | Compare numbers and dates against a primary document. |
| 3. Technical Understanding | 20% | U1 AI fundamentals, U2 knowledge of available tools | Choose between a spreadsheet, a retrieval tool and a chat model. |
| 4. Workflow & Application | 25% | W1 Integration into work, W2 task decomposition, W3 application in a domain | Split a task into stages and identify the step that needs human review. |
| 5. Safety & Responsibility | 10% (threshold) | S1 Safe and responsible use of AI | In the AISA rubric, a safety score below 4 out of 10 indicates that a person could benefit from guidance before working with AI unsupervised, whatever their overall score. |

The AISA Rubric defines five proficiency bands on a 1–10 scale: 1–2 Novice, 3–4 Developing, 5–6 Competent, 7–8 Proficient, and 9–10 Expert. Try breaking a task into steps (W2) and checking the result against a source (T1).

Practical Sidenote — 3-Minute Self-Audit Before You Start:

- Can you show a saved prompt with a clear output format, the changes you made after the first answer, and the result you checked (P1, P2, T1)?

- Do you verify every number, quote, and legal or policy claim in model outputs against an authoritative primary source (T1)?

- Do you know exactly which client or company data must never be pasted into a public chat window and whether model training on your chat history is disabled in your account settings (S1)?

If you answered “no” to two questions, choose one missing step and try it on a real task. [Individual training](/en/personal) can help you practise finding sources, checking outputs and handling data.

## What AI Cannot Do: Honest Boundaries vs. Marketing Hype

The [European Commission](https://digital-strategy.ec.europa.eu/en/faqs/ai-literacy-questions-answers) gives a practical example: staff using AI for ad copy or translation should understand that the tool can invent facts.

- Sycophancy — the model validates your mistaken assumptions instead of pushing back. On 29 April 2025, OpenAI published [Sycophancy in GPT-4o: What happened and what we're doing about it](https://openai.com/index/sycophancy-in-gpt-4o/) (followed by [Expanding on what we missed with sycophancy](https://openai.com/index/expanding-on-sycophancy/) on 2 May 2025), explaining why it rolled back an April GPT-4o update. Because reward signals over-weighted short-term user approval, the model became overly flattering and validated flawed ideas or incorrect premises. Practical rule for adults: never ask a model "Is my plan good?"—instruct it to "Identify 5 logical gaps, missing assumptions, and failure risks in this draft."

- Confident Hallucinations and Fabricated Rules. Generative models predict plausible token sequences rather than querying a verified rule database by default. In the landmark British Columbia Civil Resolution Tribunal ruling [Moffatt v. Air Canada, 2024 BCCRT 149](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html) (14 February 2024), an airline chatbot invented a non-existent policy claiming passengers could apply for a bereavement fare retroactively within 90 days of travel. The tribunal rejected the argument that the chatbot was a separate legal entity and ordered Air Canada to pay C$812.02 including damages, interest and fees. Any price, date, contract clause, or citation must be grounded in an uploaded primary document.

- Zero Accountability Without Explicit Source Grounding. As highlighted by practical adult training benchmarks such as [Dreams AI (Personal AI Training London)](https://dreamsaicanbuy.com/personal-ai-training-london) and its review [Best AI Training Providers UK (14 July 2026)](https://dreamsaicanbuy.com/learn/best-ai-training-providers-uk-2026), adults do not need abstract lectures on neural network history—they need a strict operational line between tasks where AI accelerates drafting (summarizing uploaded notes, translating, restructuring tables, brainstorming variations) and decisions that require human sign-off (financial calculations, legal commitments, hiring, and client deliverables).

## Five Safety Rules for Working With AI and Agents (At Work and at Home)

As adult users move beyond basic chat windows to AI browsers, email plugins, and desktop agents, security mistakes carry immediate real-world consequences. Below are 5 non-negotiable safety rules (aligned with [/en/personal](/en/personal) and [/en/safety](/en/safety)), each grounded in documented 2025–2026 incidents:

| Safety Rule for Adult Practitioners | Documented Incident (Primary Source, Date, Impact) | Practical Defense for Your Personal & Work Setup |
| --- | --- | --- |
| 1. Never connect an AI agent with write or delete permissions to a live database or primary drive without an isolated backup | 18–21 July 2025 — SaaStr / Replit Agent incident ([AI Incident Database #1152](https://incidentdatabase.ai/cite/1152/), [The Register](https://www.theregister.com/2025/07/21/replit_saastr_vibe_coding_incident/)): during a code freeze, an autonomous agent wiped a live production database containing 1206 executive records and 1196 company records. 1 December 2025 — Google Antigravity ([The Register](https://www.theregister.com/2025/12/01/google_antigravity_wipes_d_drive/)): an agent running a cache-cleanup command with the /q quiet flag wiped the user's entire D: drive. | Grant AI tools access only to a dedicated sandbox folder or duplicate spreadsheet, and keep offline/versioned backups before running any automated action. |
| 2. Do not process untrusted external emails, resumes, or web pages inside the same agent session that has access to your private files | Researchers demonstrated a risk of data disclosure when Microsoft 365 Copilot processed email. Microsoft fixed [EchoLeak, CVE-2025-32711](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2025-32711) on the service side. | Separate contexts: summarize external documents or untrusted web pages in an isolated session disconnected from your internal workspace drives. |
| 3. Never let a browser AI agent browse untrusted links inside a profile logged into your bank, email, or CRM | [Unit 42](https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/) reported 22 techniques used to place instructions for AI systems on websites on 3 March 2026. One page contained 24 attempts to influence ad review. The researchers did not establish that a deployed reviewer was bypassed. | Run browser assistants inside a clean, separate browser profile with zero saved payment cards, passwords, or active banking/CRM sessions. |
| 4. Never store saved payment methods or allow autonomous checkout in an AI assistant profile | 9 February 2025 — Unauthorized OpenAI Operator purchase ([Anchorage Daily News / Washington Post](https://www.adn.com/alaska-life/2025/02/09/i-let-chatgpts-new-agent-manage-my-life-it-spent-31-on-a-dozen-eggs/)): while searching for groceries, the agent autonomously placed and paid for a $31.43 Instacart order using a linked credit card without final user confirmation. | Keep payment credentials out of agent profiles; every financial transaction must require manual human review and confirmation. |
| 5. Redact personal and client identifiers before pasting text into cloud LLMs | Include confidentiality in staff training. Entering client names, phone numbers, health records or financial details into a consumer chat can expose the information beyond its intended audience. The [European Commission FAQ](https://digital-strategy.ec.europa.eu/en/faqs/ai-literacy-questions-answers) discusses training tailored to the context of use. | Replace names and sensitive figures with neutral placeholders ([Client A], [Amount X]) and disable model training on your conversations in account settings. |

## Four Practical Tracks: What You Can Build in 4, 10, or 12 Sessions

In [one-to-one sessions](/en/personal), choose a real task and save a baseline example. Repeat the task with your new workflow, then compare time spent and errors against the baseline. The [curriculum](/en/curriculum) and [method](/en/method) describe how to structure the work.

| Practical Learning Track | Typical Starting Point ("Before") | What We Build Together 1:1 | Example project to agree before starting |
| --- | --- | --- | --- |
| 1. Communications | Manual follow-up emails. | Draft a reply from meeting notes. | Tested templates and a review checklist. |
| 2. Portfolio | No work sample to show. | Solve a task from your field and document the checks. | A case study with sources, errors and revisions. |
| 3. Research | Notes spread across tabs. | Build a brief from named sources. | A brief or slide deck with each citation checked. |
| 4. Automation | Copying rows between files. | Define inputs, output rules and a manual checkpoint. | A repeatable document workflow and operating notes. |

## Transparent Onboarding and Live Formats on aiskillab.work

The site lists package prices for reference. Scope, schedule, payment, rescheduling, cancellation and refund terms are agreed in writing before payment. See [pricing](/en/pricing) and [how to start](/en/start).

| Step / Package (Adults, 1:1) | Duration & Volume | Price (USD) | What Is Included & Best Fit |
| --- | --- | --- | --- |
| Step 1. Free Intro Call | 15 minutes · 1:1 online | Free ($0) | We discuss your current tasks, review your experience level, and decide whether a single diagnostic session or a structured package fits best ([/en/start](/en/start)). |
| Step 2. Diagnostic Session | 60 minutes · 1 session 1:1 | $120 (credited toward a package purchased within 14 days) | Discuss one real task and agree on a starting plan ([pricing](/en/pricing)). |
| Start Package | 4 sessions × 60 minutes 1:1 | $390 | Core AI workflow, data-safety hygiene, and your first practical deliverable built on your own work materials ([/en/pricing](/en/pricing)). |
| Personal Package | 10 sessions × 60 minutes 1:1 | $890 | Custom learning track, reusable prompt & verification templates, document/spreadsheet workflows, and a completed capstone project ([/en/pricing](/en/pricing)). |
| Intensive Package | 12 sessions × 60 minutes 1:1 + project | $1290 | Deep implementation of a multi-step automation, custom AI agent, working prototype, or professional portfolio project ([/en/pricing](/en/pricing)). |
| Paired Format (2 adults with shared goals) | Matches chosen package (4, 10, or 12 sessions) | 1.6× individual package price (each participant pays 20% less) | Designed for two colleagues, co-founders, or family members learning together on shared workflows ([/en/pricing](/en/pricing)). |
| Post-Launch Ongoing Support | Optional monthly retainer | $178/mo (Office hours, 2 sessions) · $490/mo (Support, 4 hrs) · $890/mo (Partner, 8 hrs) | Ongoing workflow tuning, troubleshooting, and review after completing your primary package ([/en/pricing](/en/pricing)). |

If your goal is deploying a scoped AI workflow pilot for a small business team rather than 1:1 personal training, see our dedicated AI Studio tracks on [/en/studio](/en/studio).

## Related Pages on aiskillab.work

- [1:1 AI Training for Adults](/en/personal) — overview of tracks, safety rules, and practical outcomes.

- [Curriculum & Modules](/en/curriculum) — how individual building blocks are assembled around your goals.

- [Our Practice-First Method](/en/method) — why every session produces a real working artifact.

- [Pricing & Diagnostic Credit Rules](/en/pricing) — transparent packages and written pre-payment terms.

- [Discuss your task](/en/start).

## Sources

- [The Washington Post · Geoffrey A. Fowler on Operator](https://www.washingtonpost.com/technology/2025/02/07/openai-operator-ai-agent-chatgpt/)
