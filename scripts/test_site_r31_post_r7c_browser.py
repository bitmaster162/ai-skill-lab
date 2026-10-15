#!/usr/bin/env python3
"""Offline Chromium checks for post-R7C form readiness (zero live requests)."""
from __future__ import annotations
import json
import mimetypes
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import site_r31_post_r7c_profile as gate

ORIGIN = "https://aiskillab.work"
ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
BROWSER = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError("R31_BROWSER_HOLD " + why)


def run() -> None:
    gate.check_release()
    need(BROWSER.is_file(), "browser_absent")
    cfg = json.loads((LIVE / "vercel.json").read_bytes())
    response_headers = {
        item["key"]: item["value"]
        for entry in cfg["headers"] if entry["source"] == "/(.*)"
        for item in entry["headers"]
    }
    result = []
    with sync_playwright() as api:
        browser = api.chromium.launch(
            executable_path=str(BROWSER), headless=True, timeout=25000,
            args=["--disable-background-networking", "--disable-component-update",
                  "--no-first-run", "--disable-default-apps"],
        )
        try:
            for locale in ("ru", "en"):
                route_path = "/en/start" if locale == "en" else "/start"
                for scenario in ("no_js", "runtime_missing", "ready_success", "ready_error"):
                    ctx = browser.new_context(
                        java_script_enabled=scenario != "no_js",
                        service_workers="block", offline=True,
                        viewport={"width": 390, "height": 844},
                    )
                    ctx.set_default_timeout(5000)
                    api_calls = []
                    allowed_local = []
                    blocked = []
                    def handle(route):
                        request = route.request
                        url = urlsplit(request.url)
                        if (url.scheme != "https" or url.netloc != "aiskillab.work"
                                or url.query or url.fragment):
                            blocked.append(("external_or_url_data", request.method, url.path))
                            route.abort()
                            return
                        if request.method == "POST" and url.path == "/api/lead":
                            api_calls.append(request.post_data or "")
                            if scenario == "ready_success":
                                route.fulfill(status=200,content_type="application/json",
                                              body='{"ok":true}')
                            elif scenario == "ready_error":
                                route.fulfill(status=503,content_type="application/json",
                                              body='{"ok":false}')
                            else:
                                blocked.append(("unexpected_post", request.method, url.path))
                                route.abort()
                            return
                        if request.method != "GET" or url.path.startswith("/api/") or url.path.startswith("/_vercel/"):
                            blocked.append(("not_fixture_get", request.method, url.path))
                            route.abort()
                            return
                        if url.path == "/lead-form-runtime.js" and scenario == "runtime_missing":
                            route.abort()
                            return
                        rel = "index.html" if url.path == "/" else url.path.lstrip("/")
                        if "." not in Path(rel).name:
                            rel += ".html"
                        dest = (LIVE / rel).resolve()
                        if not dest.is_relative_to(LIVE.resolve()) or not dest.is_file():
                            blocked.append(("missing_file", request.method, url.path))
                            route.abort()
                            return
                        allowed_local.append(rel)
                        content_type = mimetypes.guess_type(dest.name)[0] or "application/octet-stream"
                        if dest.suffix == ".js":
                            content_type = "application/javascript"
                        route.fulfill(status=200, body=dest.read_bytes(),
                                      headers={**response_headers, "Content-Type": content_type})
                    ctx.route("**/*", handle)
                    page = ctx.new_page()
                    try:
                        response = page.goto(ORIGIN + route_path, wait_until="load", timeout=12000)
                        need(response is not None and response.status == 200, "page_loading")
                        form = page.locator("form#application-form")
                        submit = form.locator('button[type="submit"]')
                        note = form.locator("[data-lead-readiness]")
                        direct = form.locator("[data-lead-direct-contact] a")
                        need(form.count()==1 and direct.is_visible(), "missing_form_or_fallback")
                        need(direct.get_attribute("href") == "#contact-channels", "fallback_target")
                        need(page.locator("#contact-channels").count() == 1, "fallback_anchor")
                        if scenario in ("no_js", "runtime_missing"):
                            need(submit.is_disabled() and note.is_visible(), "unready_must_be_disabled")
                            need(form.get_attribute("data-lead-state") == "unready", "unready_state")
                            need(len(api_calls) == 0, "unexpected_unready_api")
                        else:
                            page.locator('form#application-form[data-lead-state="ready"]').wait_for(state="attached", timeout=6500)
                            need(submit.is_enabled() and note.is_hidden(), "ready_runtime")
                            form.locator('[name="name"]').fill("ASL_SYNTHETIC_NO_LIVE")
                            form.locator('[name="contact"]').fill("synthetic@example.invalid")
                            form.locator('[name="goal"]').fill("LOCAL ONLY INTERCEPT TEST")
                            form.locator('[name="privacyConsent"]').check()
                            submit.click()
                            page.locator("[data-lead-message].success, [data-lead-message].error").wait_for(state="attached", timeout=6500)
                            need(len(api_calls) == 1, "expected_one_mock_post")
                            need("ASL_SYNTHETIC_NO_LIVE" in api_calls[0], "fixture_post_missing")
                            if scenario == "ready_error":
                                need(form.locator('[name="name"]').input_value()=="ASL_SYNTHETIC_NO_LIVE", "error_lost_user_input")
                            else:
                                need(form.locator('[name="name"]').input_value()=="", "success_not_reset")
                            need(submit.is_enabled(), "submit_not_restored")
                        need(page.url == ORIGIN + route_path, "navigated_away")
                        need(not any(x[0] == "unexpected_post" for x in blocked), "unapproved_posts")
                        result.append({"locale":locale,"scenario":scenario,
                                       "mock_posts":len(api_calls),"status":"PASS",
                                       "fixture_gets":len(allowed_local),"real_requests_continued":0})
                    finally:
                        ctx.close()
        finally:
            browser.close()
    need(len(result)==8,"missing_browser_cases")
    print("R31_POST_R7C_OFFLINE_BROWSER_PASS cases=8 live_requests=0 user_profile=false",
          json.dumps(result,ensure_ascii=True))


if __name__ == "__main__":
    run()
