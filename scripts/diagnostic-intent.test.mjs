import assert from "node:assert/strict";
import { test } from "node:test";
import { diagnosticApplicationHref, selectStartProgram, selectStartProgramValues, START_PROGRAMS } from "../lib/diagnostic-intent.ts";

test("only explicitly allowed start programs can be selected", () => {
  assert.deepEqual(START_PROGRAMS, ["", "diagnostic"]);
  assert.equal(selectStartProgram("diagnostic"), "diagnostic");
  for (const value of [null, "", "intro", "kids-creator", "teens-builder", "DIAGNOSTIC", "diagnostic ", "paid", "other"]) {
    assert.equal(selectStartProgram(value), "");
  }
});

test("duplicate, unknown, and youth-track start queries fail closed", () => {
  assert.equal(selectStartProgramValues(["diagnostic"]), "diagnostic");
  for (const values of [[], ["diagnostic", "diagnostic"], ["diagnostic", "kids-creator"], ["kids-creator"], ["intro"]]) {
    assert.equal(selectStartProgramValues(values), "");
  }
});

test("both diagnostic CTAs use only public lead intent without PII", () => {
  assert.equal(diagnosticApplicationHref("ru"), "/start?program=diagnostic#application-form");
  assert.equal(diagnosticApplicationHref("en"), "/en/start?program=diagnostic#application-form");
  for (const locale of ["ru", "en"]) {
    const href = new URL(diagnosticApplicationHref(locale), "https://aiskillab.work");
    assert.deepEqual([...href.searchParams.entries()], [["program", "diagnostic"]]);
    assert.equal(href.hash, "#application-form");
  }
});
