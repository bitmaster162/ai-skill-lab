"""Compare the reviewed simulator before and after the Russian label repair."""
import argparse
import json
from math import isclose
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
from rehearse_pilot_audience_release import JOINT_MANIFEST, snapshot
from test_diagnostic_intent_browser import browser_path
from test_pilot_audience_browser import ORIGIN, serve_fixture

CANDIDATE = "0e2702981427152474dbdfbe12380bdd02b9ea08fa9dc3ab73ed5931941550b7"
KEYS = ("knowledge", "documents", "routing", "decision")
FIELDS = ("title", "signal", "scope", "ai", "human", "success", "stop", "artifact")
STATUS = ["ПРИВЯЗАНО К ИСТОЧНИКУ", "ПРОВЕРЯЕМО", "MEASURABLE", "ПОД КОНТРОЛЕМ ЧЕЛОВЕКА"]


def observe(browser, root, locale, js=True):
    route = "/business" if locale == "ru" else "/en/business"
    rule = "/:adultRoute(business|personal)" if locale == "ru" else "/en/:adultRoute(business|personal)"
    config = json.loads((root / "vercel.json").read_bytes())["headers"]
    headers = {}
    for row in config:
        if row["source"] in ("/(.*)", rule):
            headers.update({h["key"]: h["value"] for h in row["headers"]})
    ctx = browser.new_context(java_script_enabled=js, viewport={"width": 390, "height": 844})
    try:
        ctx.route("**/*", lambda req: serve_fixture(req, root, headers, []))
        page = ctx.new_page()
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(ORIGIN + route)
        def visible():
            return {k: page.locator("#pilot-" + k).inner_text() for k in FIELDS}
        initial = visible()
        if not js:
            return initial
        scenarios = {}
        for i, key in enumerate((*KEYS, KEYS[0])):
            page.locator('[data-pilot-key="' + key + '"]').click()
            assert page.locator('[data-pilot-key][aria-pressed="true"]').count() == 1
            assert page.locator('[data-pilot-key][aria-pressed="true"]').get_attribute("data-pilot-key") == key
            assert page.locator("#pilot-index").inner_text() == f"0{KEYS.index(key)+1}"
            value = visible()
            if i == len(KEYS):
                assert value == initial == scenarios[key]
            scenarios[key] = value
        scenario = page.locator("[data-business-value]")
        sliders = scenario.locator('input[type="range"]')
        assert sliders.count() == 4
        def results():
            team, hours, rate, percent = [float(x.input_value()) for x in sliders.all()]
            monthly = team * hours * (52 / 12)
            expected = [monthly, monthly * percent / 100, monthly * percent / 100 * rate]
            values = [float(x.get_attribute("data-value")) for x in scenario.locator("[data-bv-result]").all()]
            assert all(isclose(a, b) for a, b in zip(values, expected, strict=True)), (values, expected)
            # Capture generated text even when its disclosure is collapsed.
            return {"values":values, "brief":scenario.locator("[data-bv-brief]").text_content()}
        calculator = [results()]
        for i in range(4):
            slider = sliders.nth(i)
            assert slider.is_enabled()
            for side in ("Home","End"):
                slider.press(side)
                expect(slider).to_have_value(slider.get_attribute("min" if side == "Home" else "max"))
                calculator.append(results())
        assert all(sample["brief"] for sample in calculator)
        assert not errors, errors
        return {"initial": initial, "scenarios": scenarios, "calculator": calculator}
    finally:
        ctx.close()


def compare(before, after):
    old = snapshot(before, JOINT_MANIFEST)
    new = snapshot(after, CANDIDATE)
    assert old.keys() == new.keys()
    assert {key for key in old if old[key] != new[key]} == {"business.html", "vercel.json"}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=browser_path())
        facts = {"browser":browser.version}
        for locale in ("ru", "en"):
            static = observe(browser, before, locale, js=False)
            assert static == observe(browser, after, locale, js=False)
            was = observe(browser, before, locale)
            now = observe(browser, after, locale)
            assert static == now["initial"]
            assert was["calculator"] == now["calculator"]
            changed = [(k,f) for k in KEYS for f in FIELDS if was["scenarios"][k][f] != now["scenarios"][k][f]]
            expect = [("knowledge","signal"),("knowledge","success"),("documents","signal"),("decision","signal")]
            assert changed == (expect if locale == "ru" else [])
            if locale == "ru":
                assert [now["scenarios"][k]["signal"] for k in KEYS] == STATUS
                assert was["initial"]["signal"] == "SOURCE-BOUND"
            facts[locale] = {"changed":changed, "signals_before":[was["scenarios"][k]["signal"] for k in KEYS],
                "signals_after":[now["scenarios"][k]["signal"] for k in KEYS],
                "states":len(now["scenarios"]), "calculator_samples":len(now["calculator"]), "revisit":True}
        browser.close()
        return facts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.parent.resolve(), args.candidate.resolve()), ensure_ascii=False, indent=2))
