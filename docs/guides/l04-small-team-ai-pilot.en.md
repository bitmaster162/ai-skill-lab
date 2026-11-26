---
site: aiskillab.work
path: /en/guides/small-team-ai-pilot
alternate: /guides/small-team-ai-pilot
lang: en
title: "Introducing AI to a small team: a practical pilot"
seo_title: "AI for Small Teams: A Practical Pilot | AI Skill Lab"
description: "Choose one team workflow for AI, protect data, assign reviewers, measure observable results and decide whether to extend a pilot."
reviewed: 2026-11-19
next_review: 2027-02-19
related: [/en/curriculum, /en/personal]
schema: [Article, BreadcrumbList]
research_source: "03_RESEARCH_MODELS R700 and AI_Skill_Lab research informed topic selection; claims checked against NIST AI RMF and official OpenAI guidance. Editorial draft."
---

# Introducing AI to a small team: a pilot without miracle claims

Do not start by buying a collection of tools or installing an "agent for everything". Start with one repeatable task, an accountable owner, inputs you are allowed to use, and a way to compare the outcome with normal work. This guide is **a learning pilot plan**, not a promise to reduce costs or replace colleagues.

AI Skill Lab starts with an actual task, checks sources and keeps a person responsible for the outcome. See the [curriculum](/en/curriculum) and [individual learning route](/en/personal). NIST provides voluntary AI risk guidance across Govern, Map, Measure and Manage that should be tailored to the actual use case, not mistaken for a certification. [S1](https://airc.nist.gov/airmf-resources/playbook/)

## 1. Choose one task, not "AI transformation"

Find a process with identifiable input, a repeatable output, and a person capable of judging its quality. For early learning, favour **drafts** that can be corrected before communication or a system change. Do not begin with healthcare, legal decisions, payments, account access or irreversible effects without appropriate expert review.

Before making a selection, answer:
1. **Input:** which documents or facts already exist, who owns them, and are you permitted to use them in this service under applicable terms?
2. **Output:** do you need a plan, letter, summary, question list or comparison table?
3. **Acceptance:** how will a human verify accuracy, completeness, tone and the absence of invented details?
4. **Owner:** who accepts the result, fixes errors and can stop the exercise?
5. **Boundary:** what must the model not see and which actions must it not perform?

The scenarios below are **learning exercises**, not real customer stories and not evidence of savings.

| Practice task | Safe example of input | AI draft output | Human quality check |
|---|---|---|---|
| Meeting plan | Anonymised agenda notes | Draft agenda and open questions | Original points included; no extra commitments |
| Process email | Generic briefing without contact details | Editable message | Facts, tone, recipient and approval before sending |
| Option comparison | Official public descriptions and specified criteria | Differences and gaps table | Claims agree with primary sources |
| Internal procedure FAQ | An approved instruction with no secrets | FAQ draft for colleagues | Rules unchanged and owner has signed off |

## 2. Check data and access before the first prompt

Identify information classes: public, internal, personal, confidential and access secrets. Use only approved content or synthetic examples for a practice exercise. **Removing names does not always anonymise material**: context and unique details may still identify a person. Do not share another person's information without authority and an understanding of how the service processes it.

Review the provider's terms for data processing, retention, administrator access and whether content may be used to improve models. For example, the [OpenAI Data Controls FAQ](https://help.openai.com/en/articles/7730893-data-usage-for-openai-models) describes settings for controlling the use of conversations; the available settings depend on the product and account. A model-training switch **does not replace** your permission to process confidential material. Do not paste passwords, API keys, real payment data or other people's private documents into practice chats.

NIST also addresses generative-AI-specific risks in its [GenAI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence). This is a voluntary risk resource, not universal proof that an individual team is compliant. [S2](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)

## 3. Assign roles and agree on a checking process

Even in a very small team, distinguish **the person asking for a draft**, **the person checking it** and **the owner who can authorise an external action**. Someone may hold multiple roles, but the moment of approval must remain visible. Permission to create a draft is not permission to send a message, overwrite a file or update a CRM.

Use this procedure:
1. Record the aim, sample input and acceptance criteria before generating.
2. Produce a draft with limited context and a specified output format.
3. Find names, dates, figures, URLs, quotations and fresh promises in the result.
4. Compare every material assertion with the source material or a primary source.
5. Retain the corrected version and the human decision: accept, revise or reject.

[OpenAI's prompting guidance](https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt) recommends being specific about the task, context, constraints and output format. OpenAI also explains that ChatGPT can present incorrect facts, invented quotations and links. Checking remains a separate operation. [S3](https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt) [S4](https://help.openai.com/en/articles/8313428-does-chatgpt-tell-the-truth)

## 4. Run a limited pilot and measure what you observed

First perform the selected task as you ordinarily would and preserve a reference result. Then try it with AI using comparable, authorised input. Define **before the exercise** which errors are unacceptable and what should stop the pilot. If the output cannot be checked, there is no defensible acceptance gate for this task yet.

Keep a simple worksheet for each trial:
- Task, date, tool version and the class of data authorised for use.
- Checkable quality criteria and a reference result for comparison.
- Human time spent preparing, reviewing and correcting; tool cost if available.
- Detected factual errors, omissions, mismatches and their severity.
- Review outcome: accepted, revised, rejected or insufficient evidence.
- Who made the decision and whether data or access boundaries were breached.

Do not turn a feeling of convenience into a claim of "productivity growth": a small pilot may only tell you about its specific tasks. Include the cost of verification and newly introduced risks. NIST encourages organisations to document risks and use decisions across Govern, Map, Measure and Manage. [S1](https://airc.nist.gov/airmf-resources/playbook/)

## 5. Give colleagues a repeatable template

**Practice prompt:**

"Help create [specific draft] for [audience]. Base the result solely on [approved material]. Do not add facts, dates or commitments that are not in that material. If anything is missing, list questions instead of guessing. Return [format]. Finish with a separate list of items that a person must verify before use."

There are no magic words. The person defines criteria and reviews the output; another prompt can fix a specific problem but does not automatically establish factual accuracy. Preserve the best verified example, rather than keeping a full chat history full of unnecessary personal data.

Run a short teach-back exercise: each participant should explain where the facts came from, what was verified, where uncertainty remains and who can release the result outside the team. If these questions cannot be answered, the workflow is not ready for automation.

## 6. Decide whether to extend, revise or stop

**Extend** only when repeated trials meet the accepted quality criteria, input handling is controlled, ownership is clear, and review effort has been observed. **Revise** if some use is apparent but the criteria or training are inadequate. **Stop** when unauthorised data enters the workflow, consequential facts cannot be verified, or external actions occur without approval.

You do not have to move to autonomous agents. For many initial tasks, a draft-generating model and a human reviewer are enough. Adding email, documents or API integrations requires separate work on permissions, approvals and logging — it is not merely another prompt.

## Sources

- **[S1](https://airc.nist.gov/airmf-resources/playbook/)** NIST, *AI RMF Playbook* — voluntary Govern/Map/Measure/Manage risk guidance.
- **[S2](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)** NIST, *Generative AI Profile* — generative AI risk considerations.
- **[S3](https://help.openai.com/en/articles/10032626-prompt-engineering-best-practices-for-chatgpt)** OpenAI Help Center, *Prompt engineering best practices* — explicit task and format.
- **[S4](https://help.openai.com/en/articles/8313428-does-chatgpt-tell-the-truth)** OpenAI Help Center, *Does ChatGPT tell the truth?* — fact-checking.
- **[S5](https://help.openai.com/en/articles/7730893-data-usage-for-openai-models)** OpenAI Help Center, *Data Controls FAQ* — controls over data use.

**Status: editorial draft.** All examples are synthetic practice scenarios. Effectiveness, return on investment and the absence of risk are not guaranteed.