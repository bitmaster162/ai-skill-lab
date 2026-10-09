#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"

CASES = {
    "ru": [
        {
            "label": "ИНЦИДЕНТ · JUL 2025",
            "title": "Replit Agent удалил данные production-базы.",
            "body": "Во время эксперимента SaaStr агент Replit удалил данные приложения из базы. Replit позже публично подтвердил проблему: до нового разделения development/production изменения во время разработки могли затронуть production; данные удалось восстановить через rollback.",
            "note": "Урок: текстовый запрет вроде «ничего не менять» слабее технической границы, которая физически не даёт агенту писать в production.",
            "source": "https://replit.com/blog/doubling-down-on-our-commitment-to-secure-vibe-coding",
            "source_label": "Replit · 29.07.2025",
        },
        {
            "label": "УЯЗВИМОСТЬ · CVE-2025-32711",
            "title": "EchoLeak показал, что входящие данные могут стать инструкцией.",
            "body": "Исследователи показали цепочку indirect prompt injection в Microsoft 365 Copilot: специально подготовленное письмо могло попасть в контекст Copilot и привести к утечке данных без клика по письму. Microsoft исправила уязвимость; публично сообщалось, что признаков эксплуатации «в дикой природе» не было.",
            "note": "Урок: письмо, веб-страница, документ или комментарий — это недоверенные данные, даже если агент умеет их читать автоматически.",
            "source": "https://www.scworld.com/news/microsoft-365-copilot-zero-click-vulnerability-enabled-data-exfiltration",
            "source_label": "SC Media · Microsoft CVE-2025-32711",
        },
        {
            "label": "АТАКА ОБНАРУЖЕНА · DEC 2025",
            "title": "Unit 42 увидела hidden prompts на мошеннических страницах.",
            "body": "Unit 42 обнаружила реальные веб-страницы с indirect prompt injection, включая попытку заставить AI-систему проверки рекламы одобрить мошенническое объявление. Исследователи отдельно отмечают: подтверждённого успешного обхода deployed ad-checker в этом кейсе они не видели.",
            "note": "Урок: агент, который читает интернет, должен отделять содержимое страницы от команд и не получать лишние права только потому, что «это удобно».",
            "source": "https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/",
            "source_label": "Palo Alto Networks Unit 42",
        },
    ],
    "en": [
        {
            "label": "INCIDENT · JUL 2025",
            "title": "Replit Agent deleted production-app database data.",
            "body": "During a SaaStr experiment, Replit Agent deleted app data from a database. Replit later acknowledged the problem publicly: before its new development/production separation, changes made during development could affect production; the data was restored through rollback.",
            "note": "Lesson: a written instruction such as “do not change anything” is weaker than a technical boundary that prevents the agent from writing to production.",
            "source": "https://replit.com/blog/doubling-down-on-our-commitment-to-secure-vibe-coding",
            "source_label": "Replit · 29 Jul 2025",
        },
        {
            "label": "VULNERABILITY · CVE-2025-32711",
            "title": "EchoLeak showed that incoming data can become an instruction.",
            "body": "Researchers demonstrated an indirect prompt-injection chain in Microsoft 365 Copilot: a crafted email could enter Copilot context and enable data exfiltration without the user clicking the email. Microsoft patched the issue; public reporting said Microsoft had no evidence of in-the-wild exploitation.",
            "note": "Lesson: email, webpages, documents and comments are untrusted data even when an agent can read them automatically.",
            "source": "https://www.scworld.com/news/microsoft-365-copilot-zero-click-vulnerability-enabled-data-exfiltration",
            "source_label": "SC Media · Microsoft CVE-2025-32711",
        },
        {
            "label": "ATTACK OBSERVED · DEC 2025",
            "title": "Unit 42 found hidden prompts on malicious webpages.",
            "body": "Unit 42 observed real webpages carrying indirect prompt injection, including an attempt to make an AI ad-review system approve a scam advertisement. The researchers explicitly noted that they had not confirmed a successful bypass of a deployed ad-checking agent in that case.",
            "note": "Lesson: an agent that reads the web must separate page content from commands, and it should not gain extra authority simply because automation is convenient.",
            "source": "https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/",
            "source_label": "Palo Alto Networks Unit 42",
        },
    ],
}

RULES = {
    "ru": [
        ("01 · Сначала read-only", "Пусть агент сначала читает, планирует и показывает diff. Право писать выдаётся отдельно и только там, где оно действительно нужно."),
        ("02 · Минимальные права", "Тестовая среда, отдельные аккаунты и ключи, запрет production-доступа по умолчанию. Не давайте агенту больше полномочий, чем требует одна задача."),
        ("03 · Человек перед необратимым действием", "Удаление данных, публикация, отправка сообщения, покупка, платёж или изменение доступа требуют явного подтверждения перед эффектом."),
        ("04 · Данные не равны инструкциям", "Текст из письма, сайта, файла, issue или чата может быть враждебным. Агент не должен превращать найденный контент в новые команды без отдельной проверки."),
        ("05 · Проверка после эффекта", "Нужны журнал действия, проверка результата, способ отката и стоп-условие. «Агент сказал, что всё готово» — не доказательство."),
    ],
    "en": [
        ("01 · Start read-only", "Let the agent read, plan and show a diff first. Grant write authority separately and only where one task actually requires it."),
        ("02 · Least privilege", "Use test environments, separate accounts and keys, and no production access by default. Do not give an agent more authority than one task needs."),
        ("03 · Human before irreversible effects", "Data deletion, publishing, sending messages, purchasing, payment or access changes require explicit confirmation before the effect."),
        ("04 · Data is not instruction", "Text from email, webpages, files, issues or chat can be hostile. Retrieved content must not become a new command without a separate trust check."),
        ("05 · Verify after the effect", "Keep an action log, verify the result, define rollback and a stop condition. “The agent said it is done” is not evidence."),
    ],
}

CSS = r"""
/* N15_AGENT_SAFETY_START */
.agentSafety{background:var(--ground)}
.agentSafetyCases{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:32px 0 52px}
.agentSafetyCase{min-width:0;padding:24px;background:var(--card);border:1px solid var(--border);border-radius:20px;display:flex;flex-direction:column}
.agentSafetyCase>span{color:var(--muted);font-weight:850;letter-spacing:.04em}
.agentSafetyCase h3{margin:20px 0 12px}
.agentSafetyCase p{color:var(--second);line-height:1.7;margin:0 0 18px}
.agentSafetyCase strong{display:block;line-height:1.6;margin-top:auto}
.agentSafetyCase a{min-height:48px;display:flex;align-items:center;margin-top:18px;color:var(--ink);text-decoration:underline;text-underline-offset:4px;overflow-wrap:anywhere}
.agentSafetyRules{list-style:none;padding:0;margin:28px 0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.agentSafetyRules li{min-width:0;padding:22px;border:1px solid var(--border);border-radius:20px;background:var(--panel)}
.agentSafetyRules strong{display:block;margin-bottom:10px}
.agentSafetyRules p{margin:0;color:var(--second);line-height:1.65}
.agentSafetyNote{max-width:900px;margin:26px 0 0;color:var(--muted);line-height:1.7}
@media(max-width:1050px){.agentSafetyCases{grid-template-columns:1fr 1fr}}
@media(max-width:620px){.agentSafetyCases,.agentSafetyRules{grid-template-columns:1fr}.agentSafetyCase,.agentSafetyRules li{padding:20px}}
/* N15_AGENT_SAFETY_END */
""".strip()

TARGETS = {
    "personal.html": ("ru", "pricing"),
    "en/personal.html": ("en", "pricing"),
    "teens.html": ("ru", "pricing"),
    "en/teens.html": ("en", "pricing"),
    "business.html": ("ru", "pilot"),
    "en/business.html": ("en", "pilot"),
}

LEARNER_CASES = [('Replit: автоматическое действие привело к удалению данных.', 'Во время эксперимента SaaStr агент Replit удалил данные приложения из базы. Replit подтвердил проблему, а данные впоследствии восстановили.', 'Для практики используйте учебные или тестовые данные и проверяйте, что именно изменится.'), ('Copilot: письмо содержало скрытые инструкции.', 'Исследователи описали уязвимость EchoLeak в Microsoft 365 Copilot: специально подготовленное письмо могло привести к утечке данных без клика по письму. Microsoft исправила уязвимость; подтверждённых случаев эксплуатации в открытых источниках не сообщалось.', 'Письмо или файл могут содержать вредоносные инструкции. Проверяйте, откуда взялся текст.'), ('Unit 42: на веб-страницах нашли скрытые команды.', 'Исследователи обнаружили веб-страницы с попытками скрыто направлять работу ИИ, включая проверку рекламы. Подтверждённого успешного обхода действующей системы в этом случае не было.', 'Содержимое сайта — источник информации, а не команда, которую ИИ должен выполнять.')]
LEARNER_RULES = [('01 · Проверяйте источники', 'Сверяйте важные утверждения с первоисточником и не принимайте уверенный ответ за доказательство.'), ('02 · Берегите личные данные', 'Не вводите пароли, адреса, платёжные сведения и чужие данные без необходимости и разрешения.'), ('03 · Отличайте данные от указаний', 'Текст из письма, сайта или файла может содержать команды для ИИ. Не считайте их своими инструкциями.'), ('04 · Согласовывайте важные действия', 'Перед отправкой, публикацией, удалением или оплатой проверяйте действие и получайте нужное разрешение.'), ('05 · Проверяйте результат', 'Сравните результат с задачей. Если возможны изменения данных, заранее продумайте способ исправления.')]
LEARNER_LEAD = 'Безопасность ИИ — это умение проверять источники, беречь данные и не превращать непроверенный ответ в действие без человека.'
LEARNER_NOTE = 'Примеры различаются: Replit — реальный случай удаления данных; EchoLeak — исправленная уязвимость без подтверждённой эксплуатации в открытых источниках; Unit 42 — обнаруженная попытка скрытого управления ИИ, без подтверждённого успешного обхода.'

def esc(value: str) -> str:
    return html.escape(value, quote=True)

def block(locale: str) -> str:
    en = locale == "en"
    cases_html = []
    for item in CASES[locale]:
        cases_html.append(
            '<article class="agentSafetyCase">'
            f'<span>{esc(item["label"])}</span>'
            f'<h3>{esc(item["title"])}</h3>'
            f'<p>{esc(item["body"])}</p>'
            f'<strong>{esc(item["note"])}</strong>'
            f'<a href="{esc(item["source"])}" target="_blank" rel="noopener noreferrer">{esc(item["source_label"])} ↗</a>'
            '</article>'
        )
    rules_html = "".join(
        f'<li><strong>{esc(title)}</strong><p>{esc(body)}</p></li>'
        for title, body in RULES[locale]
    )
    eyebrow = "SAFE AGENT WORK · 3 CASES + 5 RULES" if en else "БЕЗОПАСНАЯ РАБОТА С AI-АГЕНТАМИ · 3 КЕЙСА + 5 ПРАВИЛ"
    heading = "Do not trust the plan. Control the effect." if en else "Не доверять плану. Контролировать эффект."
    lead = (
        "An AI agent can read, decide and use tools. The risk starts when a plausible answer can turn directly into an external effect. These three documented cases show different failure modes."
        if en else
        "AI-агент умеет читать, принимать решения и использовать инструменты. Риск начинается там, где правдоподобный ответ может сразу превратиться во внешний эффект. Эти три документированных кейса показывают разные классы отказа."
    )
    rules_label = "FIVE OPERATING RULES" if en else "ПЯТЬ РАБОЧИХ ПРАВИЛ"
    rules_heading = "Authority should be explicit." if en else "Полномочия должны быть явными."
    note = (
        "The cases are not equivalent: Replit was a real operational incident; EchoLeak was a confirmed vulnerability patched before public disclosure with no known in-the-wild exploitation; the Unit 42 case was an observed malicious injection attempt without confirmed successful bypass of a deployed ad-review agent."
        if en else
        "Кейсы не равнозначны: Replit — реальный операционный инцидент; EchoLeak — подтверждённая уязвимость, исправленная до публичного раскрытия, без известной эксплуатации; кейс Unit 42 — обнаруженная вредоносная попытка prompt injection без подтверждённого успешного обхода deployed ad-review агента."
    )
    return (
        '<section class="section agentSafety" id="agent-safety" data-n15-agent-safety="true">'
        f'<div class="sectionHead"><span>{esc(eyebrow)}</span><h2>{esc(heading)}</h2></div>'
        f'<p class="longCopy">{esc(lead)}</p>'
        f'<div class="agentSafetyCases">{"".join(cases_html)}</div>'
        f'<div class="sectionHead"><span>{esc(rules_label)}</span><h2>{esc(rules_heading)}</h2></div>'
        f'<ol class="agentSafetyRules">{rules_html}</ol>'
        f'<p class="agentSafetyNote">{esc(note)}</p>'
        '</section>'
    )


def learner_block() -> str:
    items = []
    for index, item in enumerate(CASES["ru"]):
        title, body, note = LEARNER_CASES[index]
        items.append(
            '<article class="agentSafetyCase">'
            f'<span>{esc(item["label"])}</span>'
            f'<h3>{esc(title)}</h3>'
            f'<p>{esc(body)}</p>'
            f'<strong>{esc(note)}</strong>'
            f'<a href="{esc(item["source"])}" target="_blank" rel="noopener noreferrer">{esc(item["source_label"])} ↗</a>'
            '</article>'
        )
    rules_html = "".join(
        f'<li><strong>{esc(title)}</strong><p>{esc(body)}</p></li>' for title, body in LEARNER_RULES
    )
    return (
        '<section class="section agentSafety" id="agent-safety" data-n15-agent-safety="true">'
        '<div class="sectionHead"><span>ТРИ ПРИМЕРА · ПЯТЬ ПРАВИЛ</span><h2>Безопасность ИИ</h2></div>'
        f'<p class="longCopy">{esc(LEARNER_LEAD)}</p>'
        f'<div class="agentSafetyCases">{"".join(items)}</div>'
        '<p class="longCopy"><strong>Пять правил практики</strong></p>'
        f'<ol class="agentSafetyRules">{rules_html}</ol>'
        f'<p class="agentSafetyNote">{esc(LEARNER_NOTE)}</p>'
        '</section>'
    )

def update_page(path: Path, locale: str, mode: str) -> bool:
    raw = path.read_text(encoding="utf-8")
    marker = 'data-n15-agent-safety="true"'

    # E3.4: one learner-focused block below the price/packages section, only on RU audience routes.
    is_learner = (json.loads((LIVE / "_release.json").read_text(encoding="utf-8")).get("release_id") == "E3_4_AI_SAFETY_AUDIENCE_R1" and locale == "ru" and path.parent == LIVE and path.name in {"personal.html", "teens.html"})
    if is_learner:
        section = re.compile(
            r'<section class="section agentSafety" id="agent-safety" data-n15-agent-safety="true">[\s\S]*?</section>'
        )
        old_blocks = section.findall(raw)
        if len(old_blocks) != 1:
            raise RuntimeError(f"{path}: original N15 block count {len(old_blocks)}")
        cleared = section.sub("", raw, count=1)
        pricing = re.compile(r'<section class="section paper" id="pricing">[\s\S]*?</section>')
        slots = list(pricing.finditer(cleared))
        if len(slots) != 1:
            raise RuntimeError(f"{path}: pricing section count {len(slots)}")
        updated = cleared[:slots[0].end()] + learner_block() + cleared[slots[0].end():]
        if updated != raw:
            path.write_text(updated, encoding="utf-8", newline="\n")
            return True
        return False
    if marker in raw:
        # Replace the exact generated block to keep regeneration deterministic.
        raw2, count = re.subn(
            r'<section class="section agentSafety" id="agent-safety" data-n15-agent-safety="true">[\s\S]*?</section>',
            block(locale),
            raw,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"{path}: existing N15 block replacement failed")
        changed = raw2 != raw
        if changed:
            path.write_text(raw2, encoding="utf-8", newline="\n")
        return changed

    if mode == "pricing":
        anchor = '<section class="section paper" id="pricing">'
    else:
        anchor = '<section class="section"><div class="sectionHead"><span>IMPLEMENTATION PILOT</span>'
    if raw.count(anchor) != 1:
        raise RuntimeError(f"{path}: insertion anchor count={raw.count(anchor)}")
    raw = raw.replace(anchor, block(locale) + anchor, 1)
    path.write_text(raw, encoding="utf-8", newline="\n")
    return True

def update_css() -> bool:
    path = LIVE / "workshop.css"
    raw = path.read_text(encoding="utf-8")
    pattern = re.compile(r"/\* N15_AGENT_SAFETY_START \*/[\s\S]*?/\* N15_AGENT_SAFETY_END \*/")
    if pattern.search(raw):
        new = pattern.sub(CSS, raw)
    else:
        new = raw.rstrip() + "\n" + CSS + "\n"
    if new != raw:
        path.write_text(new, encoding="utf-8", newline="\n")
        return True
    return False

def main() -> int:
    changed = 0
    for rel, (locale, mode) in TARGETS.items():
        changed += int(update_page(LIVE / rel, locale, mode))
    css_changed = update_css()
    print(f"N15_BUILD_PASS pages={len(TARGETS)} page_changes={changed} css_changed={str(css_changed).lower()} cases=3 rules=5")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
