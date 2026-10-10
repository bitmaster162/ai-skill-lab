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
const FUTURE_GUIDE_PAYLOAD_SHA = "bd972c8b657e6ebf558da3630970668f935b149abc88e28e10cc53a36d9c5973";
const FUTURE_GUIDE_SOURCE_SHA: Record<GuideLocale, string> = {
  ru: "5c5f8d8da100a8657aeefbe5d9044462095e92db341e240a37bdebae57bba61b",
  en: "b0bcd0a6b545d2d8d4b190e55ab9d3c76350a9a30a8e1c745fb23e04b48df671",
};
const FUTURE_GUIDE_STATIC_ASSETS = [
  ["guides/ai-first-tasks-for-adults.html", 27314, "f3cecb6ea3f46ab64ac3d3ab16db955ab8776d5edeb0c87b3b9b46bcaae2af91"],
  ["en/guides/ai-first-tasks-for-adults.html", 20480, "dd43b529fac595d4ac5ea2d848de54db8dd11be761bf873b109593476f2c58aa"],
] as const;

function futureGuidePairApproved(): boolean {
  try {
    const manifest: unknown = JSON.parse(
      fs.readFileSync(path.join(process.cwd(), "deploy", "live", "_release.json"), "utf8"),
    );
    if (manifest === null || typeof manifest !== "object" || Array.isArray(manifest)) return false;
    const header = manifest as Record<string, unknown>;
    if (
      header.schema !== "ai-skill-lab.static-release.v1" ||
      header.release_id !== FUTURE_GUIDE_RELEASE ||
      header.file_count !== 98 ||
      header.payload_sha256 !== FUTURE_GUIDE_PAYLOAD_SHA
    ) return false;
    const files = header.files;
    if (!Array.isArray(files) || files.length !== 98) return false;
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
    for (const [assetPath, expectedSize, expectedSHA] of FUTURE_GUIDE_STATIC_ASSETS) {
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
