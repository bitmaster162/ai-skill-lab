"""Verify both pilot guides against an offline static release in Chromium."""
import argparse
import json
import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright
from prepare_phuket_universe_static_r1 import sha, verify_manifest
from test_diagnostic_intent_browser import browser_path

ORIGIN = "https://127.0.0.1"
BUSINESS = "?audience=business#application-form"


def serve_fixture(route, root, headers, submissions):
    request = route.request
    url = urlsplit(request.url)
    if url.scheme != "https" or url.netloc != "127.0.0.1":
        return route.abort()
    if request.method == "POST" and url.path == "/api/lead":
        submissions.append(request.post_data_json)
        return route.fulfill(json={"ok": True})
    if request.method != "GET" or url.path.startswith("/api/"):
        return route.abort()
    name = url.path.lstrip("/") or "index"
    path = (root / (name if Path(name).suffix else name + ".html")).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return route.fulfill(status=404)
    media = "text/javascript" if path.suffix == ".js" else mimetypes.guess_type(path)[0]
    return route.fulfill(path=path, content_type=media, headers=headers if path.suffix == ".html" else {})


def check_locale(browser, root, headers, locale):
    prefix = "/en" if locale == "en" else ""
    guide = ORIGIN + prefix + "/guides/ai-pilot-for-small-business"
    start = prefix + "/start"
    target = start + BUSINESS
    submissions = []
    with browser.new_context(offline=True, service_workers="block") as context:
        context.route("**/*", lambda route: serve_fixture(route, root, headers, submissions))
        page = context.new_page()
        page.set_default_timeout(5000)
        form = page.locator("form#application-form")
        audience = form.locator('select[name="audience"]')
        privacy = form.locator('[name="privacyConsent"]')
        guardian = form.locator('[name="adultConfirmation"]')
        submit = form.locator('[type="submit"]')

        page.goto(guide)
        article_links = page.locator("main article a[href]").evaluate_all(
            """(links, start) => links.filter(link => link.origin === location.origin
                && link.pathname === start).map(link => link.getAttribute('href'))""",
            start,
        )
        if article_links != [target] * 3:
            raise AssertionError(f"{locale} pilot application links: {article_links!r}")
        for index in range(len(article_links)):
            page.goto(guide)
            calls_to_action = page.locator(f'main a[href="{target}"]')
            expect(calls_to_action).to_have_count(3)
            calls_to_action.nth(index).click()
            expect(page).to_have_url(ORIGIN + target)
            expect(form).to_have_attribute("data-lead-state", "ready")
            expect(audience).to_have_value("business")

        for selection in ("business", "adult", "parent", "teen"):
            page.goto(ORIGIN + target)
            expect(audience).to_have_value("business")
            if selection != "business":
                audience.select_option(selection)
                page.evaluate("""() => {
                    history.pushState(null, "", location.pathname);
                    dispatchEvent(new PopStateEvent("popstate"));
                    history.pushState(null, "", location.pathname + "?audience=business#application-form");
                    dispatchEvent(new PopStateEvent("popstate"));
                }""")
                expect(audience).to_have_value(selection)
            form.locator('[name="name"]').fill("Offline regression")
            form.locator('[name="contact"]').fill("qa@example.invalid")
            expect(privacy).not_to_be_checked()
            assert privacy.evaluate("el => el.required && el.validity.valueMissing")
            privacy.check()
            if selection in ("parent", "teen"):
                expect(guardian).to_be_visible()
                assert guardian.evaluate("el => el.required && el.validity.valueMissing")
                guardian.check()
            else:
                expect(guardian).not_to_be_visible()
                assert not guardian.evaluate("el => el.required")
            with page.expect_response(lambda response: response.url == ORIGIN + "/api/lead"):
                submit.click()
            sent = submissions[-1]
            assert (sent["audience"], sent["locale"], sent["program"]) == (selection, locale, "")
            assert sent["privacyConsent"] == "yes"
            assert (sent.get("adultConfirmation") == "yes") == (selection in ("parent", "teen"))
        assert len(submissions) == 4

        page.goto(ORIGIN + start + "?program=diagnostic&audience=business#application-form")
        expect(audience).to_have_value("business")
        expect(form.locator('[name="program"]')).to_have_value("diagnostic")

        for query, program in (("", ""), ("?audience=unknown", ""),
                               ("?audience=business&audience=business", ""),
                               ("?audience=adult&audience=business", ""),
                               ("?program=diagnostic", "diagnostic")):
            page.goto(ORIGIN + start + query)
            expect(form).to_have_attribute("data-lead-state", "ready")
            expect(audience).to_have_value("adult")
            expect(form.locator('[name="program"]')).to_have_value(program)

    return {"guide": urlsplit(guide).path, "application_links": article_links,
            "simulated_submissions": len(submissions)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("static_root", type=Path, help="Directory containing the static release")
    parser.add_argument("--receipt", type=Path, help="Write the offline result and tested manifest hash as JSON")
    args = parser.parse_args()
    root = args.static_root.resolve()
    paths = list(root.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Unexpected symlink in static site")
    assets = {path.relative_to(root).as_posix(): path.read_bytes() for path in paths if path.is_file()}
    manifest_raw = assets.pop("_release.json")
    manifest = verify_manifest(assets, manifest_raw)
    config = json.loads((root / "vercel.json").read_bytes())
    headers = next({h["key"]: h["value"] for h in rule["headers"]}
                   for rule in config["headers"] if rule["source"] == "/(.*)")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=browser_path())
        try:
            results = {locale: check_locale(browser, root, headers, locale) for locale in ("ru", "en")}
        finally:
            browser.close()
    if args.receipt:
        receipt = {"manifest_sha256": sha(manifest_raw),
                   "release_id": manifest["release_id"], "locales": results}
        args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("Pilot audience verified: six guide links, eight simulated submissions, zero live requests.")
