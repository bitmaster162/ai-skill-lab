// Extend the static Start form in the business-pilot release candidate.
(() => {
  "use strict";
  const path = window.location.pathname;
  if (path !== "/start" && path !== "/en/start") return;

  const form = document.querySelector("form#application-form[data-lead-bound='true']");
  const audience = form?.elements.namedItem("audience");
  if (!audience || typeof URLSearchParams !== "function") return;
  const business = audience.querySelector('option[value="business"]');
  const adult = audience.querySelector('option[value="adult"]');
  if (!business || !adult) return;

  const alternate = path === "/start" ? "/en/start" : "/start";
  const languageLink = document.querySelector(
    `header a.workshopUtility[href="${alternate}"], header a.workshopUtility[href^="${alternate}?"]`
  );
  const originalAdultDefault = adult.defaultSelected;
  let manual = false;
  let businessIntent = false;

  function updateLanguageLink() {
    if (!languageLink) return;
    const params = new URLSearchParams(window.location.search);
    const program = params.getAll("program");
    const target = new URLSearchParams();
    if (program.length === 1 && program[0] === "diagnostic") target.set("program", "diagnostic");
    if (businessIntent) target.set("audience", "business");
    const query = target.toString();
    languageLink.href = query ? alternate + "?" + query + "#application-form" : alternate;
  }

  function syncIntent() {
    const values = new URLSearchParams(window.location.search).getAll("audience");
    const next = values.length === 1 && values[0] === "business";
    if (next !== businessIntent) {
      const selection = audience.value;
      businessIntent = next;
      adult.defaultSelected = !next && originalAdultDefault;
      business.defaultSelected = next;
      audience.value = manual ? selection : next ? "business" : "adult";
    }
    updateLanguageLink();
  }

  audience.addEventListener("change", () => { manual = true; });
  form.addEventListener("reset", () => { manual = false; });
  // The base form refreshes its diagnostic language link on submission.
  form.addEventListener("submit", updateLanguageLink);
  window.addEventListener("popstate", syncIntent);
  syncIntent();
})();
