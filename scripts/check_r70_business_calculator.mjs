#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sourcePath = path.join(root, 'components', 'BusinessValueCalculator.tsx');
const source = fs.readFileSync(sourcePath, 'utf8');

const requiredSourceContracts = [
  'const WEEKS_PER_MONTH = 52 / 12;',
  'const monthlyRoutine = team * weeklyHours * WEEKS_PER_MONTH;',
  'const recoverableHours = monthlyRoutine * (recoverable / 100);',
  'const grossValue = recoverableHours * rate;',
  'min="1" max="30" value={team}',
  'min="1" max="40" value={weeklyHours}',
  'min="10" max="200" step="5" value={rate}',
  'min="10" max="80" step="5" value={recoverable}',
];
for (const contract of requiredSourceContracts) {
  assert.ok(source.includes(contract), `source contract missing: ${contract}`);
}

const WEEKS_PER_MONTH = 52 / 12;
function calc(team, weeklyHours, rate, recoverable) {
  const monthlyRoutine = team * weeklyHours * WEEKS_PER_MONTH;
  const recoverableHours = monthlyRoutine * (recoverable / 100);
  const grossValue = recoverableHours * rate;
  return { monthlyRoutine, recoverableHours, grossValue };
}

const vectors = [
  { team: 1,  weeklyHours: 1,  rate: 10,  recoverable: 10, expectedGross: 4.333333333333334 },
  { team: 30, weeklyHours: 40, rate: 200, recoverable: 80, expectedGross: 832000 },
  { team: 3,  weeklyHours: 10, rate: 25,  recoverable: 30, expectedGross: 975 },
  { team: 5,  weeklyHours: 15, rate: 40,  recoverable: 20, expectedGross: 2600 },
  { team: 10, weeklyHours: 20, rate: 50,  recoverable: 50, expectedGross: 21666.666666666668 },
  { team: 2,  weeklyHours: 5,  rate: 15,  recoverable: 15, expectedGross: 97.5 },
  { team: 8,  weeklyHours: 8,  rate: 60,  recoverable: 25, expectedGross: 4160 },
  { team: 12, weeklyHours: 12, rate: 80,  recoverable: 35, expectedGross: 17472 },
  { team: 4,  weeklyHours: 18, rate: 35,  recoverable: 40, expectedGross: 4368 },
  { team: 20, weeklyHours: 25, rate: 120, recoverable: 60, expectedGross: 156000 },
  { team: 1,  weeklyHours: 40, rate: 100, recoverable: 50, expectedGross: 8666.666666666668 },
  { team: 15, weeklyHours: 10, rate: 30,  recoverable: 20, expectedGross: 3900 },
  { team: 6,  weeklyHours: 6,  rate: 45,  recoverable: 30, expectedGross: 2106 },
  { team: 25, weeklyHours: 30, rate: 150, recoverable: 70, expectedGross: 341250 },
  { team: 2,  weeklyHours: 2,  rate: 20,  recoverable: 10, expectedGross: 34.66666666666667 },
  { team: 18, weeklyHours: 14, rate: 75,  recoverable: 45, expectedGross: 36855 },
  { team: 7,  weeklyHours: 9,  rate: 55,  recoverable: 25, expectedGross: 3753.75 },
  { team: 11, weeklyHours: 22, rate: 65,  recoverable: 35, expectedGross: 23857.166666666668 },
  { team: 14, weeklyHours: 16, rate: 90,  recoverable: 50, expectedGross: 43680 },
  { team: 30, weeklyHours: 1,  rate: 10,  recoverable: 10, expectedGross: 130 },
];

for (const [index, v] of vectors.entries()) {
  assert.ok(v.team >= 1 && v.team <= 30, `vector ${index + 1}: team out of UI bounds`);
  assert.ok(v.weeklyHours >= 1 && v.weeklyHours <= 40, `vector ${index + 1}: weeklyHours out of UI bounds`);
  assert.ok(v.rate >= 10 && v.rate <= 200 && v.rate % 5 === 0, `vector ${index + 1}: rate out of UI bounds/step`);
  assert.ok(v.recoverable >= 10 && v.recoverable <= 80 && v.recoverable % 5 === 0, `vector ${index + 1}: recoverable out of UI bounds/step`);
  const result = calc(v.team, v.weeklyHours, v.rate, v.recoverable);
  assert.ok(Number.isFinite(result.monthlyRoutine), `vector ${index + 1}: monthlyRoutine not finite`);
  assert.ok(Number.isFinite(result.recoverableHours), `vector ${index + 1}: recoverableHours not finite`);
  assert.ok(Number.isFinite(result.grossValue), `vector ${index + 1}: grossValue not finite`);
  assert.ok(Math.abs(result.grossValue - v.expectedGross) < 1e-6, `vector ${index + 1}: gross=${result.grossValue} expected=${v.expectedGross}`);
  console.log(`vector_${String(index + 1).padStart(2, '0')}: PASS gross=${result.grossValue}`);
}

console.log(`business_calculator_vectors=${vectors.length} source_contracts=${requiredSourceContracts.length}`);
console.log('R70_BUSINESS_CALCULATOR_DETERMINISM_PASS');
