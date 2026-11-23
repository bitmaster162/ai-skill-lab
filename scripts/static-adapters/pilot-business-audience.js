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
  const options = Array.from(audience.options);
  const defaults = options.map(option => option.defaultSelected);
  const defaultAudience = options.find(option => option.defaultSelected)?.value || options[0].value;
  const refreshEvent = new Event("change");
  let manual = false;
  let routeAudience;

  const goal = form.elements.namedItem("goal");
  const labelText = goal?.labels?.[0]?.firstChild;
  const defaultLabel = labelText?.textContent;
  const defaultPlaceholder = goal?.placeholder;
  const en = document.documentElement.lang === "en";

  function updateGoalHint() {
    if (!goal || labelText?.nodeType !== Node.TEXT_NODE) return;
    const team = audience.value === "business";
    labelText.textContent = team
      ? (en ? "Which process would your team like to pilot with AI?" : "На каком процессе команда хочет испытать ИИ?")
      : defaultLabel;
    goal.placeholder = team
      ? (en ? "We want AI to draft replies to service requests. A coordinator checks each draft before sending."
            : "Хотим, чтобы ИИ готовил черновики ответов на заявки. Перед отправкой их проверяет координатор.")
      : defaultPlaceholder;
  }

  function updateLanguageLink() {
    if (!languageLink) return;
    const params = new URLSearchParams(window.location.search);
    const program = params.getAll("program");
    const target = new URLSearchParams();
    if (program.length === 1 && program[0] === "diagnostic") target.set("program", "diagnostic");
    if (audience.value && audience.value !== defaultAudience) target.set("audience", audience.value);
    const query = target.toString();
    const plainFormLink = !window.location.search && window.location.hash === "#application-form";
    const audienceFormLink = routeAudience != null && window.location.hash === "#application-form";
    const stayAtForm = query || manual || plainFormLink || audienceFormLink;
    languageLink.href = alternate + (query ? "?" + query : "") + (stayAtForm ? "#application-form" : "");
  }

  function syncIntent() {
    const values = new URLSearchParams(window.location.search).getAll("audience");
    const next = values.length === 1 && options.some(option => option.value === values[0]) ? values[0] : null;
    if (next !== routeAudience) {
      const selection = audience.value;
      routeAudience = next;
      options.forEach((option, index) => {
        option.defaultSelected = next ? option.value === next : defaults[index];
      });
      audience.value = manual ? selection : next || defaultAudience;
    }
    refreshForm();
  }

  // Run the base form's guardian-consent handler as well after a restore or reset.
  function refreshForm() {
    audience.dispatchEvent(refreshEvent);
  }

  audience.addEventListener("change", event => {
    if (event !== refreshEvent) manual = true;
    updateLanguageLink();
    updateGoalHint();
  });
  form.addEventListener("reset", () => {
    manual = false;
    queueMicrotask(refreshForm);
  });
  window.addEventListener("pageshow", refreshForm);
  // The base form refreshes its diagnostic language link on submission.
  form.addEventListener("submit", updateLanguageLink);
  window.addEventListener("popstate", syncIntent);
  syncIntent();
})();
