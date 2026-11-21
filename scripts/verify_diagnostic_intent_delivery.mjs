// Replay the offline browser's successful requests through both handlers and the real SQL schema.
import assert from "node:assert/strict";
import { randomBytes } from "node:crypto";
import { readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";
import { handleLead } from "../services/lead-ingress/api/lead.js";
import { handleReceiver } from "../services/lead-receiver-cloudflare/src/index.js";

const forms = JSON.parse(readFileSync(0, "utf8"));
const db = new DatabaseSync(":memory:");
db.exec(readFileSync(new URL("../schema/lead_intake_r101b.sql", import.meta.url), "utf8"));
const secret = randomBytes(32).toString("hex");
const origin = "https://site.example.invalid";
const webhook = "https://receiver.example.invalid/r101b/lead";
const ingress = {
  LEAD_INGRESS_ENABLED: "true", LEAD_ALLOWED_ORIGINS: origin,
  LEAD_WEBHOOK_URL: webhook, LEAD_WEBHOOK_SECRET: secret,
  LEAD_LEGAL_OPERATOR_NAME: "Offline fixture", LEAD_LEGAL_JURISDICTION: "Fixture",
  LEAD_PRIVACY_CONTACT: "qa@example.invalid", LEAD_RETENTION_DAYS: "30", LEAD_RATE_LIMIT_READY: "true",
};
const receiver = {
  LEAD_RECEIVER_ENABLED: "true", LEAD_WEBHOOK_SECRET: secret,
  LEAD_RATE_LIMITER: { limit: async () => ({ success: true }) },
  DB: {
    prepare(sql) {
      const statement = db.prepare(sql);
      return { bind: (...values) => ({ run: () => ({ meta: statement.run(...values) }) }) };
    },
  },
};
const originalFetch = globalThis.fetch;
try {
  globalThis.fetch = async (url, init) => {
    assert.equal(String(url), webhook);
    return handleReceiver(new Request(webhook, init), receiver);
  };
  for (const form of forms) {
    const response = await handleLead(new Request(origin + "/api/lead", {
      method: "POST", body: JSON.stringify(form),
      headers: { "Content-Type": "application/json", Origin: origin, "X-Forwarded-For": "192.0.2.1" },
    }), ingress);
    assert.equal(response.status, 200);
  }
  const rows = db.prepare("SELECT program, locale, source_path FROM lead_intake_r101b ORDER BY rowid")
    .all().map(row => [row.program, row.locale, row.source_path]);
  assert.deepEqual(rows, [
    ["diagnostic", "ru", "/start"], ["", "ru", "/start"],
    ["diagnostic", "en", "/en/start"], ["", "en", "/en/start"],
  ]);
} finally {
  globalThis.fetch = originalFetch;
  db.close();
}
