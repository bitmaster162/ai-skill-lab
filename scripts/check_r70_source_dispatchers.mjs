#!/usr/bin/env node
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const surfaces = [
  {
    file: "components/ProgramMatcher.tsx",
    required: [
      'const telegramHref = result ? `https://t.me/BiTFormer?text=${encodeURIComponent(buildBrief())}` : "https://t.me/BiTFormer";',
      'target="_blank"',
      'rel="noopener noreferrer"',
      '"Контекст: [1–2 предложения без чувствительных данных]"',
      '"Context: [1–2 sentences without sensitive data]"',
    ],
  },
  {
    file: "components/BriefCompiler.tsx",
    required: [
      'const telegramHref=`https://t.me/BiTFormer?text=${encodeURIComponent(brief)}`;',
      'target="_blank"',
      'rel="noopener noreferrer"',
      '"HUMAN GATE: не выпускать без подтверждённой человеком проверки."',
      '"HUMAN GATE: do not ship until the verification criterion is confirmed by a person."',
    ],
  },
  {
    file: "components/BusinessValueCalculator.tsx",
    required: [
      'const telegramHref = `https://t.me/BiTFormer?text=${encodeURIComponent(brief)}`;',
      'target="_blank"',
      'rel="noopener noreferrer"',
      '"Статус: scenario only · не прогноз · требуется human validation процесса."',
      '"Status: scenario only · not a forecast · process assumptions require human validation."',
    ],
  },
];

const forbidden = [
  "fetch(",
  "XMLHttpRequest",
  "sendBeacon(",
  "WebSocket(",
  "localStorage",
  "sessionStorage",
  "document.cookie",
];

let checks = 0;
for (const surface of surfaces) {
  const source = fs.readFileSync(path.join(root, surface.file), "utf8");
  for (const marker of surface.required) {
    checks += 1;
    assert.ok(source.includes(marker), `${surface.file}: missing source contract: ${marker}`);
  }
  for (const primitive of forbidden) {
    checks += 1;
    assert.ok(!source.includes(primitive), `${surface.file}: forbidden automatic/effectful primitive: ${primitive}`);
  }
}
console.log(`r70_source_dispatcher_checks=${checks} surfaces=${surfaces.length}`);
console.log("R70_SOURCE_DISPATCHER_GATE_PASS");
