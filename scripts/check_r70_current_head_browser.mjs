#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { createRequire } from "node:module";
import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const axePath = require.resolve("axe-core/axe.min.js");

const baseUrl = process.env.R70_BROWSER_BASE_URL || "http://127.0.0.1:4173";
const outDir = path.resolve(process.env.R70_BROWSER_EVIDENCE_DIR || "artifacts/r70-current-head-browser");
fs.mkdirSync(outDir, { recursive: true });

const routes = ["/", "/en", "/business", "/en/business", "/matcher", "/en/matcher", "/proof", "/en/proof"];
const viewports = {
  desktop: { width: 1440, height: 1200 },
  tablet: { width: 768, height: 1000 },
  mobile430: { width: 430, height: 900 },
  mobile390: { width: 390, height: 844 },
  mobile360: { width: 360, height: 800 },
  mobile320: { width: 320, height: 700 },
};

const failures = [];
const evidence = {
  schema: "ai-skill-lab.r70.current-head-browser-evidence/v1",
  baseUrl,
  playwright: "1.62.1",
  axeCore: "4.13.0",
  routes: {},
  screenshots: [],
  interaction: {},
  reducedMotion: {},
  reflowProxy: {},
};

function safeName(route) {
  if (route === "/") return "home-ru";
  if (route === "/en") return "home-en";
  return route.replace(/^\/|\/$/g, "").replaceAll("/", "-");
}

function fail(label, detail) {
  failures.push({ label, detail: String(detail) });
}

async function makePage(browser, viewport, label) {
  const context = await browser.newContext({ viewport });
  const page = await context.newPage();
  const pageErrors = [];
  const consoleErrors = [];
  const externalRequests = [];
  page.on("pageerror", err => pageErrors.push(String(err)));
  page.on("console", msg => { if (msg.type() === "error") consoleErrors.push(msg.text()); });
  page.on("request", req => {
    try {
      const u = new URL(req.url());
      const b = new URL(baseUrl);
      if ((u.protocol === "http:" || u.protocol === "https:") && u.origin !== b.origin) {
        externalRequests.push(req.url());
      }
    } catch {}
  });
  return { context, page, pageErrors, consoleErrors, externalRequests, label };
}

async function axeAudit(page) {
  await page.addScriptTag({ path: axePath });
  return await page.evaluate(async () => {
    const result = await globalThis.axe.run(document, {
      runOnly: {
        type: "tag",
        values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"],
      },
    });
    return {
      violations: result.violations.map(v => ({
        id: v.id,
        impact: v.impact,
        help: v.help,
        nodes: v.nodes.length,
      })),
      passes: result.passes.length,
      incomplete: result.incomplete.length,
    };
  });
}

async function routeAudit(browser, route, viewportName) {
  const vp = viewports[viewportName];
  const h = await makePage(browser, vp, `${route}:${viewportName}`);
  const url = new URL(route, baseUrl).toString();
  const response = await h.page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
  const status = response?.status() ?? 0;
  const dom = await h.page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const blankLinks = [...document.querySelectorAll('a[target="_blank"]')].map(a => ({
      href: a.getAttribute("href"),
      rel: (a.getAttribute("rel") || "").split(/\s+/).filter(Boolean),
    }));
    return {
      title: document.title,
      h1: document.querySelector("h1")?.textContent?.trim() || null,
      scrollWidth: Math.max(root.scrollWidth, body?.scrollWidth || 0),
      clientWidth: root.clientWidth,
      blankLinks,
    };
  });
  const axe = await axeAudit(h.page);
  const record = {
    status,
    viewport: vp,
    dom,
    axe,
    pageErrors: h.pageErrors,
    consoleErrors: h.consoleErrors,
    externalRequests: [...new Set(h.externalRequests)],
  };

  if (status !== 200) fail(`${route}:${viewportName}:http`, status);
  if (dom.scrollWidth > dom.clientWidth + 1) {
    fail(`${route}:${viewportName}:overflow`, `${dom.scrollWidth}>${dom.clientWidth}`);
  }
  if (axe.violations.length) fail(`${route}:${viewportName}:axe`, JSON.stringify(axe.violations));
  if (h.pageErrors.length) fail(`${route}:${viewportName}:pageerror`, h.pageErrors.join(" | "));
  if (h.consoleErrors.length) fail(`${route}:${viewportName}:console`, h.consoleErrors.join(" | "));
  if (record.externalRequests.length) fail(`${route}:${viewportName}:external-network`, record.externalRequests.join(" | "));
  for (const link of dom.blankLinks) {
    if (!link.rel.includes("noopener") || !link.rel.includes("noreferrer")) {
      fail(`${route}:${viewportName}:target-blank-rel`, JSON.stringify(link));
    }
  }

  evidence.routes[`${route}:${viewportName}`] = record;
  await h.context.close();
}

async function screenshot(browser, route, viewportName, filename, reducedMotion = "no-preference") {
  const context = await browser.newContext({ viewport: viewports[viewportName], reducedMotion });
  const page = await context.newPage();
  await page.goto(new URL(route, baseUrl).toString(), { waitUntil: "networkidle", timeout: 60000 });
  const target = path.join(outDir, filename);
  await page.screenshot({ path: target, fullPage: true });
  evidence.screenshots.push(path.relative(process.cwd(), target));
  await context.close();
}

async function touchTargets(browser) {
  for (const route of ["/", "/en"]) {
    for (const viewportName of ["mobile390", "mobile320"]) {
      const h = await makePage(browser, viewports[viewportName], `touch:${route}:${viewportName}`);
      await h.page.goto(new URL(route, baseUrl).toString(), { waitUntil: "networkidle", timeout: 60000 });
      const result = await h.page.evaluate(() => {
        const els = [...document.querySelectorAll("a,button")].filter(el => {
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none";
        });
        const failures = els.map(el => {
          const r = el.getBoundingClientRect();
          return {
            tag: el.tagName,
            text: (el.textContent || "").trim().slice(0, 80),
            width: Math.round(r.width * 10) / 10,
            height: Math.round(r.height * 10) / 10,
          };
        }).filter(x => x.width < 44 || x.height < 44);
        return { total: els.length, failures };
      });
      evidence.interaction[`touch:${route}:${viewportName}`] = result;
      if (result.failures.length) fail(`touch:${route}:${viewportName}`, JSON.stringify(result.failures.slice(0, 20)));
      await h.context.close();
    }
  }
}

async function businessInteraction(browser) {
  for (const route of ["/business", "/en/business"]) {
    const h = await makePage(browser, viewports.desktop, `business:${route}`);
    await h.page.goto(new URL(route, baseUrl).toString(), { waitUntil: "networkidle", timeout: 60000 });
    const range = h.page.locator('[data-business-value] input[type="range"]').first();
    if (await range.count() !== 1) {
      fail(`${route}:range`, "missing business range");
      await h.context.close();
      continue;
    }
    const live = h.page.locator('[data-business-value] [aria-live="polite"]').first();
    const before = await range.inputValue();
    const liveBefore = (await live.textContent()) || "";
    await range.focus();
    const focused = await range.evaluate(el => document.activeElement === el);
    await range.press("ArrowRight");
    const after = await range.inputValue();
    const liveAfter = (await live.textContent()) || "";
    const result = { before, after, focused, liveChanged: liveBefore !== liveAfter };
    evidence.interaction[`business:${route}`] = result;
    if (!focused) fail(`${route}:range-focus`, "range did not receive keyboard focus");
    if (before === after) fail(`${route}:range-keyboard`, "ArrowRight did not change range value");
    if (!result.liveChanged) fail(`${route}:aria-live`, "live-region output did not change");
    const target = path.join(outDir, `${safeName(route)}-range-focus-1440.png`);
    await h.page.screenshot({ path: target, fullPage: true });
    evidence.screenshots.push(path.relative(process.cwd(), target));
    await h.context.close();
  }
}

async function reducedMotion(browser) {
  for (const route of ["/", "/en"]) {
    const context = await browser.newContext({ viewport: viewports.mobile390, reducedMotion: "reduce" });
    const page = await context.newPage();
    await page.goto(new URL(route, baseUrl).toString(), { waitUntil: "networkidle", timeout: 60000 });
    const result = await page.evaluate(() => {
      const offenders = [...document.querySelectorAll("*")].map(el => {
        const s = getComputedStyle(el);
        const duration = s.animationDuration.split(",").map(v => parseFloat(v) || 0);
        const hasMotion = s.animationName !== "none" && Math.max(...duration, 0) > 0.05;
        const infinite = s.animationIterationCount.split(",").includes("infinite");
        return hasMotion && infinite ? {
          tag: el.tagName,
          id: el.id || null,
          cls: typeof el.className === "string" ? el.className.slice(0, 120) : null,
          animationName: s.animationName,
          animationDuration: s.animationDuration,
          iteration: s.animationIterationCount,
        } : null;
      }).filter(Boolean);
      return {
        mediaMatches: matchMedia("(prefers-reduced-motion: reduce)").matches,
        continuousAnimationOffenders: offenders,
        h1: document.querySelector("h1")?.textContent?.trim() || null,
      };
    });
    evidence.reducedMotion[route] = result;
    if (!result.mediaMatches) fail(`${route}:reduced-motion-media`, "media query did not match");
    if (result.continuousAnimationOffenders.length) {
      fail(`${route}:reduced-motion-animation`, JSON.stringify(result.continuousAnimationOffenders.slice(0, 20)));
    }
    const target = path.join(outDir, `${safeName(route)}-reduced-motion-390.png`);
    await page.screenshot({ path: target, fullPage: true });
    evidence.screenshots.push(path.relative(process.cwd(), target));
    await context.close();
  }
}

async function textScaleProxy(browser) {
  // This is explicitly a 200% root-font-size reflow proxy, not a claim of browser zoom equivalence.
  for (const route of ["/", "/en"]) {
    const context = await browser.newContext({ viewport: viewports.mobile390 });
    const page = await context.newPage();
    await page.goto(new URL(route, baseUrl).toString(), { waitUntil: "networkidle", timeout: 60000 });
    await page.evaluate(() => { document.documentElement.style.fontSize = "200%"; });
    await page.waitForTimeout(150);
    const result = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      clientWidth: document.documentElement.clientWidth,
      h1: document.querySelector("h1")?.textContent?.trim() || null,
    }));
    evidence.reflowProxy[route] = result;
    if (result.scrollWidth > result.clientWidth + 1) {
      fail(`${route}:text-scale-200-proxy-overflow`, `${result.scrollWidth}>${result.clientWidth}`);
    }
    const target = path.join(outDir, `${safeName(route)}-text-scale-200-proxy-390.png`);
    await page.screenshot({ path: target, fullPage: true });
    evidence.screenshots.push(path.relative(process.cwd(), target));
    await context.close();
  }
}

const browser = await chromium.launch({ headless: true });
try {
  // Current-head route + axe + overflow matrix.
  for (const route of routes) {
    const vpNames = route === "/" || route === "/en"
      ? ["desktop", "tablet", "mobile430", "mobile390", "mobile360", "mobile320"]
      : ["desktop", "mobile390"];
    for (const vp of vpNames) await routeAudit(browser, route, vp);
  }

  // Exact current screenshots.
  await screenshot(browser, "/", "desktop", "home-ru-1440.png");
  await screenshot(browser, "/", "tablet", "home-ru-768.png");
  await screenshot(browser, "/", "mobile390", "home-ru-390.png");
  await screenshot(browser, "/", "mobile320", "home-ru-320.png");
  await screenshot(browser, "/en", "desktop", "home-en-1440.png");
  await screenshot(browser, "/en", "mobile390", "home-en-390.png");
  await screenshot(browser, "/business", "desktop", "business-ru-1440.png");
  await screenshot(browser, "/business", "mobile390", "business-ru-390.png");
  await screenshot(browser, "/matcher", "desktop", "matcher-ru-1440.png");
  await screenshot(browser, "/matcher", "mobile390", "matcher-ru-390.png");

  await touchTargets(browser);
  await businessInteraction(browser);
  await reducedMotion(browser);
  await textScaleProxy(browser);
} finally {
  await browser.close();
}

evidence.failures = failures;
evidence.status = failures.length ? "FAIL" : "PASS";
evidence.notes = [
  "Current-head browser evidence targets the Next.js source application, not frozen deploy/live.",
  "The 200% check is a root-font-size reflow proxy and must not be represented as browser-zoom equivalence.",
  "Historical A7 evidence contains the actual 200% zoom/reflow capture and remains separate historical support.",
];

fs.writeFileSync(path.join(outDir, "browser-evidence.json"), JSON.stringify(evidence, null, 2) + "\n");
console.log(JSON.stringify({
  status: evidence.status,
  auditedRouteViewportPairs: Object.keys(evidence.routes).length,
  screenshots: evidence.screenshots.length,
  failures,
}, null, 2));

if (failures.length) process.exit(1);
console.log("R70_CURRENT_HEAD_BROWSER_EVIDENCE_PASS");
