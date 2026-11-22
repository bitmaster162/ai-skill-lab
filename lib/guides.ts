import fs from "node:fs";
import path from "node:path";
import { createHash } from "node:crypto";

export type GuideLocale = "ru" | "en";

export type GuideMeta = {
  site: string;
  path: string;
  alternate: string;
  lang: GuideLocale;
  title: string;
  seo_title: string;
  description: string;
  reviewed: string;
  next_review: string;
  related: string[];
  schema: string[];
  research_source: string;
};

export type Guide = {
  slug: string;
  meta: GuideMeta;
  markdown: string;
};

export type GuideDocument = {
  h1: string;
  leadHtml: string;
  bodyHtml: string;
  toc: Array<{ id: string; label: string }>;
};

const GUIDE_DIR = path.join(process.cwd(), "guides", "aiskillab");

// Source existence alone never grants publishing authority: the static manifest,
// exact reviewed RU/EN bytes, and matching two HTML records must all agree.
const FUTURE_GUIDE_RELEASE = "T1_6F2_ADULT_FIRST_TASKS_R1";
const FUTURE_GUIDE_SLUG = "ai-first-tasks-for-adults";
const FUTURE_GUIDE_PAYLOAD_SHA = "188c0b7c3204dd4c1366a51facafeb09421c929e58913e34c7500d9fdf2ea30e";
// R7C is a separately pinned, exact-copy withdrawal, not a new guide admission.
const R7C_TERMS_PATCH = "PHUKET_UNIVERSE_U3_R7C_TERMS_WITHDRAWAL_20261015";
const R7C_PARENT_MANIFEST_SHA = "a8166f8a45f17df8b7359dfb62bba467c6061f61cab1db164183216d31c42bb6";
const R7C_MANIFEST_SHA = "b10b2ad45184e2f19a329dbe22b7e2c18fef0c075f13a31a435abdf83167adc3";
const R7C_PAYLOAD_SHA = "34881e21029130c17ee6ed5fae6f4355ffda71daf5c4d32f6eb9d64cc62db832";
// Local-only candidate: adds form readiness and EN metadata, retains R7C static guide pins.
const R31_POST_R7C_PATCH = "SITE_FORM_METADATA_R31_POST_R7C_LOCAL_20261016";
const R31_POST_R7C_MANIFEST_SHA = "c9c1ffa4a227a4ed324901c7bb6019e16dcf28722fc70c72e70badfb22752505";
const R31_POST_R7C_PAYLOAD_SHA = "33fce831c34403b7236c8267ea4adf37c57d3412ce796a8858cbf8ce28debf61";
// Separately pinned sitemap-only successor. Both Universe routes retain 2026-10-15.
const R31_SITEMAP_R2_PATCH = "SITE_FORM_METADATA_R31_POST_R7C_SITEMAP_20261016_LOCAL_R2";
const R31_SITEMAP_R2_MANIFEST_SHA = "fc57c61c7ac502644665f7cc06152f43fb0b5d7f67827eb6fd4b12aadfc83f37";
const R31_SITEMAP_R2_PAYLOAD_SHA = "9a8e8b41646a2dcb07ef7fa849088666c07891a41e5050d56bcfc99a1ff03b0e";
const SITE_A2_PATCH = "SITE_A1_A2_R2_20261026_DRAFT_REVIEW";
const SITE_A2_MANIFEST_SHA = "79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889";
const SITE_A2_PAYLOAD_SHA = "9c5bcc257f49e53172abddd1b9f366e560adbbd00f269950cc408c555536efe3";
const SITE_A2_PARENT_SHA = "ad8282f6b7a670c9e5e5f840dd0d427f3c24f87a2210f64d40dab1cf7bf497e5";
const SITE_A2_ADMISSION_SHA = "fb4a04354f1a99a2d2d0cc7b5364403b2b520406660cdeb9d4ce3eaf865c7034";

const FUTURE_GUIDE_SOURCE_SHA: Record<GuideLocale, string> = {
  ru: "5c5f8d8da100a8657aeefbe5d9044462095e92db341e240a37bdebae57bba61b",
  en: "b0bcd0a6b545d2d8d4b190e55ab9d3c76350a9a30a8e1c745fb23e04b48df671",
};
const FUTURE_GUIDE_R7_STATIC_ASSETS = [
  ["guides/ai-first-tasks-for-adults.html", 27846, "580cc6096fe22e0a27d60543d7d3d93b8b61fd1db582511d31087c29fd57497c"],
  ["en/guides/ai-first-tasks-for-adults.html", 20997, "5831839b802f7755adaf8d17420e0b6cbc8ee5445713924b92dfa29c1325a20b"],
] as const;

const FUTURE_GUIDE_STATIC_ASSETS = [
  ["guides/ai-first-tasks-for-adults.html", 27314, "f3cecb6ea3f46ab64ac3d3ab16db955ab8776d5edeb0c87b3b9b46bcaae2af91"],
  ["en/guides/ai-first-tasks-for-adults.html", 20480, "dd43b529fac595d4ac5ea2d848de54db8dd11be761bf873b109593476f2c58aa"],
] as const;

function futureGuidePairApproved(): boolean {
  try {
    const manifestBytes = fs.readFileSync(path.join(process.cwd(), "deploy", "live", "_release.json"));
    const manifest: unknown = JSON.parse(manifestBytes.toString("utf8"));
    if (manifest === null || typeof manifest !== "object" || Array.isArray(manifest)) return false;
    const header = manifest as Record<string, unknown>;
    const isU1R3 = header.release_id === "PHUKET_UNIVERSE_U1_STATIC_R3_20261014";
    const isU1R5 = header.release_id === "PHUKET_UNIVERSE_U1_AGENCY_TERMS_R5_20261014";
    const isU2R6 = header.release_id === "PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014";
    const isU3R7 = header.release_id === "PHUKET_UNIVERSE_U3_E38_DORMANT_R7_20261015";
    const isU3R7B = header.release_id === "PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015";
    const isU3R7C = isU3R7B && header.patch_id === R7C_TERMS_PATCH;
    const isPostR7C = isU3R7B && header.patch_id === R31_POST_R7C_PATCH;
    const isSitemapR2 = isU3R7B && header.patch_id === R31_SITEMAP_R2_PATCH;
    const isSiteA2 = isU3R7B && header.patch_id === SITE_A2_PATCH;
    // Keep the existing guide pair on releases that attest all shipped static bytes.
    const seals = new Map([
      ["AISL_SEO_METHOD_R1_DRAFT_20261121", {
        count: 108,
        parent: "79ecdcd892a308ef3ae93b6f551a4c01e59e9a584eee39764daba5498df11889",
        payload: "f2678f7fb3ff5381e421795f83bd8115fa7365613806443cfeea9802efacdf88",
        manifest: "ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0",
      }],
      ["AISL_ADULT_GA4_OPT_IN_R3_20261121", {
        count: 112,
        parent: "ef0bc7d77b523c480fa78e3ea4c87ac1ebfbffc2567f461b077b9328c7341ab0",
        payload: "a436546681cb59eafb62b7faf8237fee7202c85cb5517cb57bd5bd1ad3db5113",
        manifest: "9758df02a2c862c643cd87c5005176ff3751ca72011ffbdaacd7112588043c73",
      }],
      ["AISL_ADULT_GUIDE_DONORS_R1_20261121", {
        count: 112,
        parent: "9758df02a2c862c643cd87c5005176ff3751ca72011ffbdaacd7112588043c73",
        payload: "b0042500ae2b8ef56311d2c6d14807f94742a64b56ce207bd4916e4e6280b2e1",
        manifest: "b222558702afafb10849792f693b8322272461098c2385b7a3b6acf4fdbd5fc7",
      }],
      ["AISL_DIAGNOSTIC_INTENT_R1_20261121", {
        count: 112,
        parent: "b222558702afafb10849792f693b8322272461098c2385b7a3b6acf4fdbd5fc7",
        payload: "8a0a23c11b4977021bb8b1ef8417746e21f0aef0f49beba2aaaf88edcb55be29",
        manifest: "78cb75d81138d54f47a37555f6eea6dff9f53f578a76779d902f0c39e97530dc",
      }],
      ["AISL_DIAGNOSTIC_INTENT_R2_20261121", {
        count: 112,
        parent: "78cb75d81138d54f47a37555f6eea6dff9f53f578a76779d902f0c39e97530dc",
        payload: "b5a10b18ca918fd8f5de0e9746c0f12ed337b7760c23ee8a10aee9b8770d7c0b",
        manifest: "aa60dba1a0760c0b74eb02e84a5168d397d87d38263fc27e54935687ce12a6ff",
      }],
      ["AISL_SITEMAP_ROUTE_DATES_R1_20261122", {
        count: 112,
        parent: "aa60dba1a0760c0b74eb02e84a5168d397d87d38263fc27e54935687ce12a6ff",
        payload: "0e377c619f86a36f55d925056b4073dc17a3cc5e5ff2f19962a7a5fedf77202f",
        manifest: "eafa144171a7deed62f06d4a18b6fa98bab7c169cf6ec829b6709060be4b52ca",
      }],
      ["AISL_CERTIFICATE_DONORS_R2_20261122", {
        count: 112,
        parent: "eafa144171a7deed62f06d4a18b6fa98bab7c169cf6ec829b6709060be4b52ca",
        payload: "9d2ea15d2f201981f14c6d3d0f431d3c3302e5b808855bc8608121b76e92641a",
        manifest: "ce4124e6afe3a8ec1fbf00131f1f8b8cad2444faac37a928f37ac632809240ed",
      }],
      ["AISL_TELEGRAM_CARD_R1_20261122", {
        count: 112,
        parent: "ce4124e6afe3a8ec1fbf00131f1f8b8cad2444faac37a928f37ac632809240ed",
        payload: "bd07783abfa0c8313d334ef33dd5449f09c2544385fedf72c0323455994b9d1c",
        manifest: "e70b076b1f754bc3dac1b402c70362d773d61e9ba2a4fbe7f7dc12c56bfd28f2",
      }],
    ]);
    const seal = typeof header.release_id === "string" ? seals.get(header.release_id) : undefined;
    if (seal) {
      if (header.patch_id !== header.release_id || header.parent_manifest_sha256 !== seal.parent ||
          header.payload_sha256 !== seal.payload || header.file_count !== seal.count ||
          createHash("sha256").update(manifestBytes).digest("hex") !== seal.manifest) return false;
      const records = header.files;
      if (!Array.isArray(records) || records.length !== seal.count) return false;
      const indexed = new Map<string, { size: number; sha256: string }>();
      for (const item of records) {
        if (!item || typeof item !== "object" || Array.isArray(item)) return false;
        const asset = item as Record<string, unknown>;
        const rel = asset.path;
        if (typeof rel !== "string" || rel.startsWith("/") || rel.includes("\\") ||
            rel.split("/").includes("..") || indexed.has(rel) ||
            !Number.isInteger(asset.size) || typeof asset.sha256 !== "string" ||
            !/^[a-f0-9]{64}$/.test(asset.sha256)) return false;
        const bytes = fs.readFileSync(path.join(process.cwd(), "deploy", "live", rel));
        if (bytes.length !== asset.size ||
            createHash("sha256").update(bytes).digest("hex") !== asset.sha256) return false;
        indexed.set(rel, { size: asset.size as number, sha256: asset.sha256 });
      }
      if (indexed.size !== seal.count) return false;
      for (const [assetPath, expectedSize, expectedSHA] of FUTURE_GUIDE_R7_STATIC_ASSETS) {
        const item = indexed.get(assetPath);
        if (!item || item.size !== expectedSize || item.sha256 !== expectedSHA) return false;
      }
      for (const locale of ["ru", "en"] as const) {
        const bytes = fs.readFileSync(path.join(GUIDE_DIR, `${FUTURE_GUIDE_SLUG}.${locale}.md`));
        if (createHash("sha256").update(bytes).digest("hex") !== FUTURE_GUIDE_SOURCE_SHA[locale]) return false;
      }
      return true;
    }
    if (isSiteA2) {
      // No wildcard: bind manifest bytes AND standalone immutable admission.
      const digest = createHash("sha256").update(manifestBytes).digest("hex");
      if (digest !== SITE_A2_MANIFEST_SHA ||
          header.parent_manifest_sha256 !== SITE_A2_PARENT_SHA ||
          header.payload_sha256 !== SITE_A2_PAYLOAD_SHA ||
          header.file_count !== 108) return false;
      const admissionBytes = fs.readFileSync(path.join(
        process.cwd(), "data", "SITE_A1_A2_R2_METADATA_SUCCESSOR_ADMISSION_V2_20261026.json"
      ));
      if (createHash("sha256").update(admissionBytes).digest("hex") !== SITE_A2_ADMISSION_SHA) return false;
      const admission = JSON.parse(admissionBytes.toString("utf8")) as Record<string, unknown>;
      if (admission.patch_id !== SITE_A2_PATCH ||
          admission.candidate_manifest_sha256 !== SITE_A2_MANIFEST_SHA ||
          admission.candidate_payload_sha256 !== SITE_A2_PAYLOAD_SHA ||
          admission.historical_r7b_manifest_sha256 !== "a8166f8a45f17df8b7359dfb62bba467c6061f61cab1db164183216d31c42bb6") return false;
    }
    if (header.patch_id !== undefined && !isU3R7C && !isPostR7C && !isSitemapR2 && !isSiteA2) return false;
    if (isU3R7C && (
      header.parent_manifest_sha256 !== R7C_PARENT_MANIFEST_SHA ||
      createHash("sha256").update(manifestBytes).digest("hex") !== R7C_MANIFEST_SHA
    )) return false;
    if (isPostR7C && (
      header.parent_manifest_sha256 !== R7C_MANIFEST_SHA ||
      createHash("sha256").update(manifestBytes).digest("hex") !== R31_POST_R7C_MANIFEST_SHA
    )) return false;
    if (isSitemapR2 && (
      header.parent_manifest_sha256 !== R31_POST_R7C_MANIFEST_SHA ||
      createHash("sha256").update(manifestBytes).digest("hex") !== R31_SITEMAP_R2_MANIFEST_SHA
    )) return false;
    const expectedRecords = isPostR7C || isSitemapR2 || isSiteA2 ? 108 : isU3R7B || isU3R7 ? 107 : isU2R6 ? 106 : isU1R3 || isU1R5 ? 104 : 98;
    if (
      header.schema !== "ai-skill-lab.static-release.v1" ||
      header.release_id !== (isU3R7B ? "PHUKET_UNIVERSE_U3_E38_DORMANT_R7B_20261015" : isU3R7 ? "PHUKET_UNIVERSE_U3_E38_DORMANT_R7_20261015" : isU2R6 ? "PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014" : isU1R5 ? "PHUKET_UNIVERSE_U1_AGENCY_TERMS_R5_20261014" : isU1R3 ? "PHUKET_UNIVERSE_U1_STATIC_R3_20261014" : FUTURE_GUIDE_RELEASE) ||
      header.file_count !== expectedRecords ||
      header.payload_sha256 !== (isSiteA2 ? SITE_A2_PAYLOAD_SHA : isSitemapR2 ? R31_SITEMAP_R2_PAYLOAD_SHA : isPostR7C ? R31_POST_R7C_PAYLOAD_SHA : isU3R7C ? R7C_PAYLOAD_SHA : isU3R7B ? "bfe1742f1ce3946f700fff9a67d273d840809d33f5e279123a205696305d2cab" : isU3R7 ? "7b74fffcd33b11c8985c5b9bc67bbee30c2d59594495183d129ab44399ab64cb" : isU2R6 ? "0b5f3b9d20d3dbcb9dcb03c6e65c0f9b513792c7cbaf71d958ee15d13914ec94" : isU1R5 ? "e8b41c9e6fed3e6b1f2b9edf66e1ddd227c4253fd1cb70c7030265dba1c63726" : isU1R3 ? "40606d00063d1ec99f495bf3623f8a8ddba23bc04298c530cf6cd97f92965c10" : FUTURE_GUIDE_PAYLOAD_SHA)
    ) return false;
    const files = header.files;
    if (!Array.isArray(files) || files.length !== expectedRecords) return false;
    const indexed = new Map<string, { size: number; sha256: string }>();
    for (const item of files) {
      if (!item || typeof item !== "object" || Array.isArray(item)) return false;
      const asset = item as Record<string, unknown>;
      if (
        typeof asset.path !== "string" ||
        !Number.isInteger(asset.size) ||
        typeof asset.sha256 !== "string" ||
        indexed.has(asset.path)
      ) return false;
      indexed.set(asset.path, { size: asset.size as number, sha256: asset.sha256 });
    }
    for (const [assetPath, expectedSize, expectedSHA] of ((isU3R7 || isU3R7B) ? FUTURE_GUIDE_R7_STATIC_ASSETS : FUTURE_GUIDE_STATIC_ASSETS)) {
      const actual = indexed.get(assetPath);
      if (!actual || actual.size !== expectedSize || actual.sha256 !== expectedSHA) return false;
    }
    for (const locale of ["ru", "en"] as const) {
      const bytes = fs.readFileSync(path.join(GUIDE_DIR, `${FUTURE_GUIDE_SLUG}.${locale}.md`));
      if (createHash("sha256").update(bytes).digest("hex") !== FUTURE_GUIDE_SOURCE_SHA[locale]) return false;
    }
    return true;
  } catch {
    return false;
  }
}

function stripQuoted(value: string): string {
  const s = value.trim();
  if (s.startsWith('"') && s.endsWith('"')) return JSON.parse(s);
  return s;
}

function parseList(value: string): string[] {
  const s = value.trim();
  if (!s.startsWith("[") || !s.endsWith("]")) return [];
  return s.slice(1, -1).split(",").map((item) => stripQuoted(item.trim())).filter(Boolean);
}

function parseGuideFile(filePath: string): Guide {
  const raw = fs.readFileSync(filePath, "utf8");
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(raw);
  if (!match) throw new Error(`guide frontmatter missing: ${filePath}`);
  const values = new Map<string, string>();
  for (const line of match[1].split(/\r?\n/)) {
    const idx = line.indexOf(":");
    if (idx < 1) continue;
    values.set(line.slice(0, idx).trim(), line.slice(idx + 1).trim());
  }
  const required = ["site", "path", "alternate", "lang", "title", "seo_title", "description", "reviewed", "next_review", "related", "schema", "research_source"];
  for (const key of required) if (!values.has(key)) throw new Error(`guide frontmatter missing ${key}: ${filePath}`);
  const lang = stripQuoted(values.get("lang")!) as GuideLocale;
  if (lang !== "ru" && lang !== "en") throw new Error(`unsupported guide lang: ${lang}`);
  const route = stripQuoted(values.get("path")!);
  const slug = route.split("/").filter(Boolean).at(-1);
  if (!slug) throw new Error(`guide slug missing: ${filePath}`);
  return {
    slug,
    meta: {
      site: stripQuoted(values.get("site")!),
      path: route,
      alternate: stripQuoted(values.get("alternate")!),
      lang,
      title: stripQuoted(values.get("title")!),
      seo_title: stripQuoted(values.get("seo_title")!),
      description: stripQuoted(values.get("description")!),
      reviewed: stripQuoted(values.get("reviewed")!),
      next_review: stripQuoted(values.get("next_review")!),
      related: parseList(values.get("related")!),
      schema: parseList(values.get("schema")!),
      research_source: stripQuoted(values.get("research_source")!),
    },
    markdown: match[2].trim(),
  };
}

export function listGuides(locale: GuideLocale): Guide[] {
  if (!fs.existsSync(GUIDE_DIR)) return [];
  const futureApproved = futureGuidePairApproved();
  return fs.readdirSync(GUIDE_DIR)
    .filter((name) =>
      name === `ai-safety-for-kids.${locale}.md` ||
      (futureApproved && name === `${FUTURE_GUIDE_SLUG}.${locale}.md`)
    )
    .sort()
    .map((name) => parseGuideFile(path.join(GUIDE_DIR, name)));
}

export function getGuide(locale: GuideLocale, slug: string): Guide | null {
  return listGuides(locale).find((guide) => guide.slug === slug) ?? null;
}

function escapeHtml(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function safeHref(raw: string): string {
  const href = raw.trim();
  if (href.startsWith("/") || href.startsWith("https://") || href.startsWith("http://")) return href;
  return "#";
}

function inlineHtml(input: string): string {
  let text = escapeHtml(input);
  const tokens: string[] = [];
  const token = (html: string) => {
    const id = `@@GUIDE_TOKEN_${tokens.length}@@`;
    tokens.push(html);
    return id;
  };
  text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_m, label: string, hrefRaw: string) => {
    const href = safeHref(hrefRaw);
    const external = /^https?:\/\//.test(href);
    return token(`<a href="${escapeHtml(href)}"${external ? ' target="_blank" rel="noopener"' : ""}>${label}</a>`);
  });
  text = text.replace(/https?:\/\/[^\s<]+/g, (url) => {
    const cleaned = url.replace(/[.,;:]$/, "");
    const suffix = url.slice(cleaned.length);
    return token(`<a href="${cleaned}" target="_blank" rel="noopener">${cleaned}</a>`) + suffix;
  });
  text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  tokens.forEach((html, i) => { text = text.replace(`@@GUIDE_TOKEN_${i}@@`, html); });
  return text;
}

function isTableDivider(line: string): boolean {
  return /^\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?$/.test(line.trim());
}

function tableCells(line: string): string[] {
  return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim());
}

export function renderGuideMarkdown(markdown: string): GuideDocument {
  const lines = markdown.replace(/\r\n/g, "\n").split("\n");
  let i = 0;
  while (i < lines.length && !lines[i].trim()) i += 1;
  if (!lines[i]?.startsWith("# ")) throw new Error("guide markdown must start with h1");
  const h1 = lines[i].slice(2).trim();
  i += 1;
  while (i < lines.length && !lines[i].trim()) i += 1;
  const lead: string[] = [];
  while (i < lines.length && lines[i].trim() && !lines[i].startsWith("## ")) {
    lead.push(lines[i].trim());
    i += 1;
  }
  while (i < lines.length && !lines[i].trim()) i += 1;
  if (i < lines.length && /^\*\*(Проверено|Checked)\b/.test(lines[i].trim())) {
    i += 1;
    while (i < lines.length && !lines[i].trim()) i += 1;
  }

  const toc: Array<{ id: string; label: string }> = [];
  const html: string[] = [];
  let section = 0;

  const pushParagraph = (parts: string[]) => {
    if (parts.length) html.push(`<p>${inlineHtml(parts.join(" "))}</p>`);
  };

  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i += 1; continue; }

    if (line.startsWith("## ")) {
      section += 1;
      const label = line.slice(3).trim();
      const id = label.toLowerCase().includes("источ") || label.toLowerCase() === "sources" ? "sources" : `section-${section}`;
      toc.push({ id, label });
      html.push(`<h2 id="${id}">${escapeHtml(label)}</h2>`);
      i += 1;
      continue;
    }

    if (line.trim().startsWith("|") && i + 1 < lines.length && isTableDivider(lines[i + 1])) {
      const header = tableCells(line);
      i += 2;
      const rows: string[][] = [];
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        rows.push(tableCells(lines[i]));
        i += 1;
      }
      html.push('<div class="guideTableWrap"><table><thead><tr>' + header.map((cell) => `<th>${inlineHtml(cell)}</th>`).join("") + "</tr></thead><tbody>" + rows.map((row) => "<tr>" + row.map((cell) => `<td>${inlineHtml(cell)}</td>`).join("") + "</tr>").join("") + "</tbody></table></div>");
      continue;
    }

    if (/^\d+\.\s+/.test(line.trim())) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^\d+\.\s+/, ""));
        i += 1;
      }
      html.push("<ol>" + items.map((item) => `<li>${inlineHtml(item)}</li>`).join("") + "</ol>");
      continue;
    }

    if (/^-\s+/.test(line.trim())) {
      const items: string[] = [];
      while (i < lines.length && /^-\s+/.test(lines[i].trim())) {
        items.push(lines[i].trim().replace(/^-\s+/, ""));
        i += 1;
      }
      html.push("<ul>" + items.map((item) => `<li>${inlineHtml(item)}</li>`).join("") + "</ul>");
      continue;
    }

    const paragraph: string[] = [];
    while (
      i < lines.length &&
      lines[i].trim() &&
      !lines[i].startsWith("## ") &&
      !/^\d+\.\s+/.test(lines[i].trim()) &&
      !/^-\s+/.test(lines[i].trim()) &&
      !(lines[i].trim().startsWith("|") && i + 1 < lines.length && isTableDivider(lines[i + 1]))
    ) {
      paragraph.push(lines[i].trim());
      i += 1;
    }
    pushParagraph(paragraph);
  }

  return { h1, leadHtml: inlineHtml(lead.join(" ")), bodyHtml: html.join("\n"), toc };
}

export function formatGuideDate(iso: string, locale: GuideLocale): string {
  const date = new Date(`${iso}T00:00:00Z`);
  return new Intl.DateTimeFormat(locale === "ru" ? "ru-RU" : "en-GB", {
    day: "numeric", month: "long", year: "numeric", timeZone: "UTC",
  }).format(date);
}
