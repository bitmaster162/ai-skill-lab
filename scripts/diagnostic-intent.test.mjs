import assert from "node:assert/strict";
import { test } from "node:test";
import { diagnosticApplicationHref, selectStartProgram, START_PROGRAMS } from "../lib/diagnostic-intent.ts";

test("only explicitly allowed start programs can be selected", () => {
  assert.deepEqual(START_PROGRAMS, ["", "diagnostic"]);
  assert.equal(selectStartProgram("diagnostic"), "diagnostic");
  for (const value of [null, "", "intro", "kids-creator", "teens-builder", "DIAGNOSTIC", "diagnostic ", "paid", "other"]) {
    assert.equal(selectStartProgram(value), "");
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
