import type { WorkshopLocale } from "@/components/workshop/WorkshopShell";

type RealProject = {
  meta: string;
  title: string;
  status: string;
  summary: string;
  evidence: string;
  boundary: string;
  href: string;
};

const projects: Record<WorkshopLocale, RealProject[]> = {
  ru: [
    {
      meta: "VISUAL AI · PUBLIC REPO",
      title: "VisionAssist",
      status: "RESEARCH / OFFLINE TESTABLE",
      summary: "Визуально-семантический слой для evidence-grounded observations, competing hypotheses, counterevidence, uncertainty и явной human-AI revision.",
      evidence: "Публичный репозиторий фиксирует 75-case corpus: 60 market chart cases + 15 deterministic visual-control cases, offline harness, scorer и proof checklist.",
      boundary: "README не заявляет calibration, human-AI uplift, natural-scene generality или production value.",
      href: "https://github.com/bitmaster162/VisionAssist",
    },
    {
      meta: "MEMORY · PUBLIC REPO",
      title: "ContinuityOS",
      status: "LOCAL-FIRST / OPEN SOURCE",
      summary: "Durable memory и continuity layer для AI-агентов и людей: canon, frontiers, open loops, checkpoints и handoff context.",
      evidence: "Публичный репозиторий и PyPI package; core memory работает локально на SQLite, поддерживает CLI, Python API, MCP и импорт AI-history из нескольких провайдеров.",
      boundary: "Demo доказывает bounded persistence через новый процесс, а не поведенческую идентичность модели или production security.",
      href: "https://github.com/bitmaster162/continuityos",
    },
    {
      meta: "AGENT GOVERNANCE · PUBLIC REPO",
      title: "BitEvo Agent Authority",
      status: "DETERMINISTIC REFERENCE",
      summary: "Публичный reference package семи ворот Agent Authority & Evidence для проверки одного action-capable workflow.",
      evidence: "spec/gates.json, локальный deterministic evaluator, fail-closed validation и regression tests; package source-bound к публичной BitEvo реализации.",
      boundary: "Не выдаёт trust/safety score, не сертифицирует систему, не исполняет внешние действия и не запрашивает credentials.",
      href: "https://github.com/bitmaster162/agent-authority",
    },
    {
      meta: "AI PRODUCT · PUBLIC REPO",
      title: "BitEvo Agent Site",
      status: "PUBLIC PRODUCT / EVIDENCE SURFACE",
      summary: "Публичный продукт для authority-first AI-agent engineering, где SOURCE, BUILD, DEPLOYMENT, READBACK и EXTERNAL EFFECT разделены как разные классы доказательств.",
      evidence: "Astro site с provider-bound build receipts, deterministic release gates, CSP hash allowlist и раздельными Vercel / Cloudflare provider paths.",
      boundary: "Production promotion отделён от build/readback; публичный repository прямо фиксирует can_trade=false и capital_permission=DENY.",
      href: "https://github.com/bitmaster162/bitevo-agent-site",
    },
    {
      meta: "CONTROL STACK · PUBLIC REPO",
      title: "TRIAXIS",
      status: "VALIDATION-ONLY",
      summary: "Versioned governance/control stack с deterministic validation assets для policy binding, external witnesses, execution reconciliation и rollback detection.",
      evidence: "Публичный репозиторий содержит executable validation harnesses для signed policy heads, quorum, execution ledger, provider reconciliation и completion witnesses.",
      boundary: "Repository прямо указывает: это не production gateway; validation results не доказывают production exactly-once behavior или complete mediation.",
      href: "https://github.com/bitmaster162/TRIAXIS",
    },
  ],
  en: [
    {
      meta: "VISUAL AI · PUBLIC REPO",
      title: "VisionAssist",
      status: "RESEARCH / OFFLINE TESTABLE",
      summary: "A visual-semantic cognition layer for evidence-grounded observations, competing hypotheses, counterevidence, uncertainty and explicit human-AI revision.",
      evidence: "The public repository documents a 75-case corpus: 60 market chart cases plus 15 deterministic visual-control cases, with an offline harness, scorer and proof checklist.",
      boundary: "The README makes no calibration, human-AI uplift, natural-scene generality or production-value claim.",
      href: "https://github.com/bitmaster162/VisionAssist",
    },
    {
      meta: "MEMORY · PUBLIC REPO",
      title: "ContinuityOS",
      status: "LOCAL-FIRST / OPEN SOURCE",
      summary: "Durable memory and continuity for AI agents and humans: canon, frontiers, open loops, checkpoints and handoff context.",
      evidence: "Public repository and PyPI package; core memory is local SQLite and supports a CLI, Python API, MCP and multi-provider AI-history import.",
      boundary: "The demo proves bounded persistence across a fresh process, not behavioral model identity or production security.",
      href: "https://github.com/bitmaster162/continuityos",
    },
    {
      meta: "AGENT GOVERNANCE · PUBLIC REPO",
      title: "BitEvo Agent Authority",
      status: "DETERMINISTIC REFERENCE",
      summary: "A public seven-gate Agent Authority & Evidence reference package for examining one action-capable workflow.",
      evidence: "spec/gates.json, a local deterministic evaluator, fail-closed validation and regression tests; the package is source-bound to the public BitEvo implementation.",
      boundary: "It does not issue a trust/safety score, certify a system, execute external actions or request credentials.",
      href: "https://github.com/bitmaster162/agent-authority",
    },
    {
      meta: "AI PRODUCT · PUBLIC REPO",
      title: "BitEvo Agent Site",
      status: "PUBLIC PRODUCT / EVIDENCE SURFACE",
      summary: "A public authority-first AI-agent product where SOURCE, BUILD, DEPLOYMENT, READBACK and EXTERNAL EFFECT are kept as separate evidence classes.",
      evidence: "Astro site with provider-bound build receipts, deterministic release gates, a CSP hash allowlist and separate Vercel / Cloudflare provider paths.",
      boundary: "Production promotion is separate from build/readback; the public repository explicitly fixes can_trade=false and capital_permission=DENY.",
      href: "https://github.com/bitmaster162/bitevo-agent-site",
    },
    {
      meta: "CONTROL STACK · PUBLIC REPO",
      title: "TRIAXIS",
      status: "VALIDATION-ONLY",
      summary: "A versioned governance/control stack with deterministic validation assets for policy binding, external witnesses, execution reconciliation and rollback detection.",
      evidence: "The public repository includes executable validation harnesses for signed policy heads, quorum, execution ledger, provider reconciliation and completion witnesses.",
      boundary: "The repository explicitly says it is not a production gateway; validation results do not prove production exactly-once behavior or complete mediation.",
      href: "https://github.com/bitmaster162/TRIAXIS",
    },
  ],
};

export function RealProjectGallery({ locale = "ru" }: { locale?: WorkshopLocale }) {
  const en = locale === "en";
  return <div className="projectStudioGrid" data-real-projects>
    {projects[locale].map((project, index) => <article className="projectStudioCard" data-real-project key={project.href}>
      <div className="projectCardTop"><span>{project.meta}</span><b>{project.status}</b></div>
      <h2><small>{String(index + 1).padStart(2, "0")}</small>{project.title}</h2>
      <p className="projectSummary">{project.summary}</p>
      <div className="projectAnatomy">
        <p><span>01</span><b>{en ? "Evidence" : "Доказательство"}</b><em>{project.evidence}</em></p>
        <p><span>02</span><b>{en ? "Boundary" : "Граница claims"}</b><em>{project.boundary}</em></p>
      </div>
      <a className="textLink" href={project.href} target="_blank" rel="noopener noreferrer">GitHub ↗</a>
    </article>)}
  </div>;
}
