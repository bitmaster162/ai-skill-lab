"""Exercise the shipped diagnostic links and form in Chromium with offline fixtures."""
import json
import mimetypes
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


LIVE = Path(__file__).resolve().parents[1] / "deploy/live"
ORIGIN = "https://aiskillab.work"
CTA_PAGES = ("", "/pricing", "/personal", "/business", "/kids", "/teens", "/parents", "/matcher", "/start")
HEADERS = next(row["headers"] for row in json.loads((LIVE / "vercel.json").read_bytes())["headers"]
               if row["source"] == "/(.*)")


def browser_path():
    windows_chrome = Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe"
    return (os.environ.get("CHROME_BIN") or shutil.which("google-chrome") or
            shutil.which("chromium") or (str(windows_chrome) if windows_chrome.is_file() else None))


def check_language_switch(page, start, locale):
    other = "/en/start" if locale == "ru" else "/start"
    language = "EN" if locale == "ru" else "RU"
    selected = "?program=diagnostic#application-form"
    form = page.locator("form#application-form")
    program = form.locator('[name="program"]')

    def follow(label, target, expected_program):
        switch = page.get_by_role("link", name=label, exact=True)
        expect(switch).to_have_count(1)
        expect(switch).to_have_attribute("href", target)
        with page.expect_request(lambda request: request.is_navigation_request()
                                 and request.frame == page.main_frame) as navigation:
            switch.click()
        # A clean href alone does not protect the source URL on a same-origin GET.
        assert navigation.value.header_value("referer") in (None, "", ORIGIN, ORIGIN + "/")
        expect(page).to_have_url(ORIGIN + target)
        expect(form).to_have_attribute("data-lead-state", "ready")
        expect(program).to_have_value(expected_program)

    cases = (
        ("", ""),
        ("?contact=qa%40example.invalid#private-note", ""),
        ("?program=other&contact=qa%40example.invalid#application-form", ""),
        ("?program=DIAGNOSTIC#application-form", ""),
        ("?program=diagnostic&program=diagnostic", ""),
        ("?program=other&program=diagnostic", ""),
        (selected, selected),
        ("?contact=qa%40example.invalid&program=diagnostic&utm_source=qa#private-note", selected),
    )
    for source_suffix, target_suffix in cases:
        page.goto(ORIGIN + start + source_suffix)
        expect(form).to_have_attribute("data-lead-state", "ready")
        expected_program = "diagnostic" if target_suffix else ""
        expect(program).to_have_value(expected_program)
        follow(language, other + target_suffix, expected_program)

    # Return through the actual header link and submit the form in this locale.
    follow(locale.upper(), start + selected, "diagnostic")


def run_locale(browser, prefix, locale):
    start = prefix + "/start"
    captured = []
    context = browser.new_context(offline=True, service_workers="block",
                                  viewport={"width": 1280 if prefix else 390, "height": 860})

    def fixture(route):
        request = route.request
        url = urlsplit(request.url)
        if url.scheme != "https" or url.netloc != "aiskillab.work":
            return route.abort()
        if request.method == "POST" and url.path == "/api/lead":
            captured.append(request.post_data_json)
            # Exercise both an unsuccessful attempt and a subsequent retry.
            return route.fulfill(status=503 if len(captured) == 1 else 200,
                                 json={"ok": len(captured) != 1})
        if request.method != "GET" or url.path.startswith("/api/"):
            return route.abort()
        name = url.path.lstrip("/") or "index"
        path = (LIVE / (name if Path(name).suffix else name + ".html")).resolve()
        if not path.is_relative_to(LIVE) or not path.is_file():
            return route.fulfill(status=404, body="")
        headers = {row["key"]: row["value"] for row in HEADERS} if path.suffix == ".html" else {}
        media_type = "text/javascript" if path.suffix == ".js" else mimetypes.guess_type(path)[0]
        return route.fulfill(path=path, content_type=media_type, headers=headers)

    context.route("**/*", fixture)
    page = context.new_page()
    page.set_default_timeout(6000)
    form = page.locator("form#application-form")
    program = form.locator('[name="program"]')
    try:
        for source in CTA_PAGES:
            page.goto(ORIGIN + (prefix + source or "/"))
            label = "Обсудить диагностику →"
            if locale == "en":
                label = "Book diagnostic →" if source == "/pricing" else "Discuss diagnostic →"
            link = page.get_by_role("link", name=label, exact=True)
            expect(link).to_have_count(1)
            link.click()
            expect(page).to_have_url(ORIGIN + start + "?program=diagnostic#application-form")
            expect(form).to_have_attribute("data-lead-state", "ready")
            expect(program).to_have_value("diagnostic")

        check_language_switch(page, start, locale)
        name = form.locator('[name="name"]')
        submit = form.locator('button[type="submit"]')
        def fill_synthetic():
            name.fill("Diagnostic QA")
            form.locator('[name="contact"]').fill("qa@example.invalid")
            form.locator('[name="goal"]').fill("Offline form regression")
            form.locator('[name="privacyConsent"]').check()

        fill_synthetic()
        submit.click()
        expect(form.locator("[data-lead-message]")).to_have_class(re.compile(r"\berror\b"))
        expect(name).to_have_value("Diagnostic QA")
        submit.click()
        expect(form.locator("[data-lead-message]")).to_have_class(re.compile(r"\bsuccess\b"))
        expect(name).to_have_value("")
        expect(program).to_have_value("diagnostic")
        assert [(p["program"], p["locale"], p["sourcePath"]) for p in captured] == [
            ("diagnostic", locale, start), ("diagnostic", locale, start)]

        for query in ("", "?program=", "?program=teens-builder", "?program=DIAGNOSTIC",
                      "?program=diagnostic&program=diagnostic", "?program=other&program=diagnostic"):
            page.goto(ORIGIN + start + query)
            expect(form).to_have_attribute("data-lead-state", "ready")
            expect(program).to_have_value("")
        fill_synthetic()
        submit.click()
        expect(form.locator("[data-lead-message]")).to_have_class(re.compile(r"\bsuccess\b"))
        assert len(captured) == 3 and captured[-1]["program"] == ""
        return captured[1:]
    finally:
        context.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path())
        try:
            successful_forms = run_locale(browser, "", "ru") + run_locale(browser, "/en", "en")
        finally:
            browser.close()
    delivery = Path(__file__).with_name("verify_diagnostic_intent_delivery.mjs")
    subprocess.run(["node", str(delivery)], check=True, input=json.dumps(successful_forms), text=True)
    print("Diagnostic intent verified: 18 links in Chromium, RU/EN language switches and retries, "
          "four in-memory SQL rows, zero live requests.")
