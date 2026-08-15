import type { Metadata } from "next";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Build Log — how AI Skill Lab was built with AI",
  description: "The open build log of AI Skill Lab: real iterations, failures, AI roles, human gates, automated verification and release engineering.",
  alternates: { canonical: "/en/build", languages: { ru: "/build", en: "/en/build" } },
};

const milestones = [
  ["R8", "BASELINE", "Proof + parent decision layer", "The project gained its first portable source authority and an honest proof layer without invented testimonials or guarantees."],
  ["R24", "COMMERCIAL", "Commercial parity", "Pricing, packages and claims were reconciled into one commercial truth and protected by an automated parity gate."],
  ["R31", "RUNTIME", "Behavior, not markup", "A real static matcher syntax bug led to runtime smoke tests, no-JS fallback and a verifiable Start flow."],
  ["R38", "GOVERNANCE", "Security + structured data", "Hashed CSP, privacy contracts, metadata/structured-data integrity and source/static semantic gates became release requirements."],
  ["R49", "RELEASE", "Deterministic builder", "Release artifacts, manifests and wrappers became byte-for-byte reproducible instead of manually packaged."],
  ["R60", "EXPERIENCE", "Site becomes the demo", "Proof Lab, Project Studio, Pilot Simulator, Brief Compiler, Challenge and Skill Graph turned the site into an interactive proof surface."],
  ["R65", "ATTENTION", "Product-scene hero", "The hero stopped acting like a marketing illustration and began showing ACTIVE WORKFLOW → DEFINE → BUILD → VERIFY → SHIP."],
  ["R66", "PROVENANCE", "Build process becomes public", "The build history, failures, toolchain and responsibility boundaries become part of the product itself."],
  ["R68", "TRANSFER", "Performance becomes a contract", "Worst-case first view stays around 14 KB Brotli: HTML + shared CSS + LAB runtime. The budget is verified on every release."],
] as const;

const failures = [
  ["STATIC JS BROKE", "The deployable static matcher contained a syntax error.", "Added syntax gates plus behavioral runtime smoke."],
  ["METADATA DRIFT", "RU/EN and source/static surfaces diverged in social and SEO metadata.", "Added deterministic metadata, hreflang and structured-data gates."],
  ["WRAPPER CORRUPTED", "One release wrapper was found to be malformed.", "Added a builder that checks archive SHA, manifest SHA and byte-exact reconstruction."],
  ["SANDBOX DISAPPEARED", "A working directory disappeared during an iteration.", "Recovered the exact project from a Git bundle. Continuity became tested practice, not a promise."],
  ["DEPLOYMENT BLOCKED", "Vercel quota/provider blockers prevented release.", "Source, build, deployment and readback remained separate states. A blocker was never reported as PASS."],
] as const;

export default function BuildPage() {
  return <><Header locale="en" alternateHref="/build"/><main id="main" className="proofPage">
    <section className="proofHero"><div className="shell proofHeroGrid"><div>
      <span className="proofEyebrow"><i/> BUILD STORY / OPEN PROVENANCE</span>
      <h1>This site is<br/><em>our own case study.</em></h1>
      <p>Not “made with AI” as a sticker. Below is the actual iteration history: what AI accelerated, what stayed a human decision, which failures were found and which controls appeared because of them.</p>
      <div className="heroActions"><a className="button buttonLight" href="#timeline">Open build log ↓</a><a className="button buttonGhost buttonOnDark" href="/_release.json">Current manifest ↗</a></div>
    </div><div className="proofConsole" aria-label="Build provenance console"><div className="proofConsoleTop"><span>AI SKILL LAB / BUILD PROVENANCE</span><b>● EVIDENCE-SCOPED</b></div><div className="proofConsoleBody"><p><span>01</span><b>ai_role</b><strong>ACCELERATE</strong></p><p><span>02</span><b>human_role</b><strong>DECIDE</strong></p><p><span>03</span><b>machine_role</b><strong>VERIFY</strong></p><p><span>04</span><b>claims</b><strong>BOUNDED</strong></p><p><span>05</span><b>history</b><strong>PORTABLE</strong></p><p><span>06</span><b>release</b><strong>MANIFESTED</strong></p></div><div className="proofConsoleFoot"><span>IDEA</span><i/><span>ITERATE</span><i/><span>BREAK</span><i/><span>PROVE</span></div></div></div></section>

    <section className="section" id="timeline"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Build timeline</span><h2>Not one prompt.<br/><em>A system of iterations.</em></h2></div><p>This is a milestone snapshot, not the full changelog. Exact current release identity always lives in <code>/_release.json</code>.</p></div><div className="programGrid">{milestones.map(([r,meta,title,text],i)=><article className="programCard" key={r}><span className="cardIndex">{String(i+1).padStart(2,"0")}</span><div className="cardSpacer"/><span className="cardMeta">{r} · {meta}</span><h3>{title}</h3><p>{text}</p></article>)}</div></div></section>

    <section className="proofSplit"><div className="shell proofSplitGrid"><article><span className="kicker">AI did</span><h2>Searched,<br/>generated,<br/>accelerated.</h2><ul><li>researched options and current policies</li><li>proposed architecture, copy and code</li><li>searched for source/static divergence</li><li>built testing and release scaffolding</li></ul></article><article className="proofHuman"><span className="kicker kickerLight">Human owned</span><h2>Selected,<br/>bounded,<br/>authorized.</h2><ul><li>defined product intent and commercial truth</li><li>made visual and semantic decisions</li><li>set risk / claims / youth-safety boundaries</li><li>kept final authority over production release</li></ul></article></div></section>

    <section className="section sectionInk"><div className="shell"><div className="sectionHead splitHead sectionHeadLight"><div><span className="kicker kickerLight">Actual toolchain</span><h2>Only what<br/><em>was actually used.</em></h2></div><p>Planned tools are not added to the case study retroactively. If another agent or service joins later, that becomes a separate verifiable iteration.</p></div><div className="proofGateGrid"><article><span>01</span><h3>CHATGPT</h3><p>Product reasoning, research synthesis, code drafting, QA design and iterative development.</p></article><article><span>02</span><h3>WEB RESEARCH</h3><p>Current policy checks and comparison of modern product/design patterns.</p></article><article><span>03</span><h3>LOCAL TEST STACK</h3><p>Python + Node gates, runtime smoke, CSP hashes, metadata parity and release manifests.</p></article><article><span>04</span><h3>GIT / BUNDLES</h3><p>Exact history, clean checkpoints and portable project recovery.</p></article><article><span>05</span><h3>VERCEL</h3><p>Deployment target. Preview, production and readback are separate release gates.</p></article><article><span>06</span><h3>HUMAN REVIEW</h3><p>Intent, taste, factual claims, risk boundaries and the final decision to release.</p></article></div></div></section>

    <section className="section"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Failure log</span><h2>The system grew most<br/>when something broke.</h2></div><p>Failures are not removed from the case study. A useful failure changes the system so that the same class cannot pass unnoticed again.</p></div><div className="programGrid">{failures.map(([title,problem,fix],i)=><article className="programCard" key={title}><span className="cardIndex">0{i+1}</span><div className="cardSpacer"/><span className="cardMeta">FAILURE → CONTROL</span><h3>{title}</h3><p>{problem}</p><p><strong>→ {fix}</strong></p></article>)}</div></div></section>

    <section className="section sectionMuted"><div className="shell proofHonesty"><div><span className="kicker">What this proves</span><h2>Not “AI built a website.”<br/><em>We can govern an AI build.</em></h2></div><div><p>The evidence is not the number of generated lines. It is the ability to evolve, verify, recover, constrain and release a product without losing commercial or semantic truth.</p><p>That is the same discipline behind our training and AI projects: <strong>Define → Build → Verify → Ship.</strong></p><div className="heroActions"><Link className="button buttonPrimary" href="/en/proof">Open Proof Lab →</Link><Link className="textLink" href="/en/projects">Project Studio →</Link></div></div></div></section>
  </main><Footer locale="en"/></>;
}
