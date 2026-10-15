/* Static export adapter. Keep its readiness and consent behavior in sync with LeadForm.tsx. */
(function () {
  "use strict";
  const form = document.querySelector("form#application-form");
  if (!form || form.dataset.leadBound === "true") return;
  const submit = form.querySelector('button[type="submit"]');
  const readiness = form.querySelector("[data-lead-readiness]");
  const direct = form.querySelector("[data-lead-direct-contact] a");
  const message = form.querySelector("[data-lead-message]");
  const successActions = form.querySelector("[data-lead-success-actions]");
  const audience = form.elements.namedItem("audience");
  const adultWrap = form.querySelector("[data-adult-confirmation]");
  const adult = form.querySelector('input[name="adultConfirmation"]');
  if (!submit || !readiness || !direct || !message || !audience || !adultWrap || !adult) return;
  submit.disabled = true;
  if (typeof window.fetch !== "function" || typeof window.FormData !== "function" ||
      typeof Object.fromEntries !== "function") return;
  const en = document.documentElement.lang === "en";
  let ready = false;
  let busy = false;
  function syncAudience() {
    const needed = audience.value === "parent" || audience.value === "teen";
    adultWrap.hidden = !needed;
    adult.required = needed;
    if (!needed) adult.checked = false;
  }
  async function onSubmit(event) {
    event.preventDefault();
    // Covers Enter, requestSubmit and repeated submit events before a render/update.
    if (!ready || busy || !form.checkValidity()) return;
    busy = true;
    submit.disabled = true;
    form.setAttribute("aria-busy", "true");
    if (successActions) successActions.hidden = true;
    message.textContent = en ? "Sending…" : "Отправляем…";
    message.className = "formMessage";
    try {
      const data = Object.fromEntries(new FormData(form).entries());
      const response = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const result = await response.json();
      if (!response.ok || !result || result.ok !== true) throw new Error("send-failed");
      form.reset();
      syncAudience();
      message.textContent = en
        ? "Application sent. We reply within 1–2 business days."
        : "Заявка отправлена. Ответим в течение 1–2 рабочих дней.";
      message.className = "formMessage success";
      if (successActions) successActions.hidden = false;
      window.dispatchEvent(new CustomEvent("asl:lead-event", { detail: { event: "lead_submit_ok" } }));
    } catch (_) {
      if (successActions) successActions.hidden = true;
      message.textContent = en
        ? "Could not send the application. Use a direct contact route below."
        : "Не удалось отправить заявку. Используйте прямой канал связи ниже.";
      message.className = "formMessage error";
      window.dispatchEvent(new CustomEvent("asl:lead-event", { detail: { event: "lead_submit_error" } }));
    } finally {
      busy = false;
      form.setAttribute("aria-busy", "false");
      submit.disabled = !ready;
    }
  }
  try {
    syncAudience();
    audience.addEventListener("change", syncAudience);
    form.addEventListener("submit", onSubmit);
    form.dataset.leadBound = "true";
    // Enable last: an absent, unparseable, or partially initialized script stays unavailable.
    form.setAttribute("data-lead-state", "ready");
    readiness.hidden = true;
    ready = true;
    submit.disabled = false;
  } catch (_) {
    ready = false;
    submit.disabled = true;
    readiness.hidden = false;
    form.setAttribute("data-lead-state", "unready");
  }
})();
