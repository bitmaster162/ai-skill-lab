import type { Metadata } from "next";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PilotSimulator } from "@/components/PilotSimulator";
import { BusinessValueCalculator } from "@/components/BusinessValueCalculator";

export const metadata: Metadata = {
  title: "AI for business",
  description: "Practical AI enablement and workflow pilots for founders and teams: process map, one testable prototype, QA, ownership and handoff.",
  alternates: { canonical: "/en/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI for business", description: "Practical AI enablement and workflow pilots for founders and teams: process map, one testable prototype, QA, ownership and handoff.", images: ["/opengraph-image"] },
};

const offers = [
  ["01", "Workflow audit", "Map recurring work, bottlenecks, data boundaries and candidate AI insertion points."],
  ["02", "Team training", "Role-specific sessions based on the team's actual documents, workflows and decisions."],
  ["03", "Implementation pilot", "One selected workflow: prototype + QA + ownership + operating rules + handoff."],
];

const pilot = [
  ["01", "Map", "Document the current process, inputs/outputs, owner, frequency, human checks and cost of failure."],
  ["02", "Select", "Choose one workflow with clear value and limited blast radius instead of pretending to automate the company in a week."],
  ["03", "Prototype & test", "Build a working version and test edge cases, quality, data boundaries, fallback and human checkpoints."],
  ["04", "Handoff", "Document ownership, operating rules, limitations, verification criteria and the next improvement backlog."],
];

const good = [
  "repeatable knowledge work with a clear input and output",
  "documents, research, classification, drafting or decision preparation with human review",
  "an accountable process owner and a describable definition of good output",
  "a bounded pilot that does not require autonomous access to critical actions",
];

const bad = [
  "no process owner or nobody willing to review the output",
  "a fully autonomous safety-critical decision is required",
  "required data cannot be used or privacy boundaries are unclear",
  "the expectation is to replace people with one button without redesigning the process or controls",
];

export default function Page() {
  return <>
    <Header locale="en" contactHref="/en/start" alternateHref="/business" />
    <main id="main">
      <section className="teenHero"><div className="shell teenHeroGrid"><div><span className="eyebrow">Founders · teams · operators</span><h1>Do not “add AI”.<br/><span>Change one process.</span></h1><p>Start from recurring work, quality and risk. Then choose one workflow that can be tested, handed to an owner and improved over time.</p><div className="heroActions"><Link className="button buttonLight" href="/en/start">Discuss business scope</Link><Link className="button buttonGhost buttonOnDark" href="/en/method">Method →</Link></div></div></div></section>

      <section className="section"><div className="shell"><span className="kicker">Engagements</span><h2>Three ways to start</h2><div className="programGrid">{offers.map(([n,t,x])=><article className="programCard" key={n}><span className="cardIndex">{n}</span><div className="cardSpacer"/><h3>{t}</h3><p>{x}</p></article>)}</div></div></section>

      <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Implementation pilot</span><h2>One workflow → a testable operating model.</h2><p className="sectionSub">The pilot is deliberately bounded. The goal is to prove that a process can be improved safely and repeatedly, not to produce a flashy demo nobody can maintain.</p></div><div className="steps">{pilot.map(([n,t,d])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div></div></section>

      <section className="section sectionInk" id="pilot-simulator"><div className="shell"><div className="sectionHead sectionHeadLight"><span className="kicker kickerLight">AI Pilot Simulator</span><h2>Scope the process before<br/>you fall in love with the demo.</h2><p>Choose a common workflow pattern. This deterministic local demo shows the candidate boundary, AI role, human checkpoint, success signal and the condition that should stop the pilot.</p></div><PilotSimulator locale="en"/></div></section>

      <section className="section" id="capacity-scenario"><div className="shell"><div className="sectionHead"><span className="kicker">Business economics · scenario</span><h2>Estimate the opportunity<br/>without pretending it is a forecast.</h2><p className="sectionSub">Set team size, routine hours, hourly value and your own assumption for the share of time that could realistically be recovered. The calculator only shows sensitivity to those inputs and does not promise savings.</p></div><BusinessValueCalculator locale="en"/></div></section>

      <section className="section"><div className="shell parentGrid"><div className="parentCard"><span className="kicker">Good candidate</span><h2>Where a pilot makes sense</h2><ul className="checkList checkDark">{good.map((x)=><li key={x}>{x}</li>)}</ul></div><div className="parentCard parentDark"><span className="kicker kickerLight">Stop signals</span><h2>Where another analysis comes first</h2><ul className="checkList">{bad.map((x)=><li key={x}>{x}</li>)}</ul></div></div></section>

      <section className="section sectionInk"><div className="shell splitHead"><div><span className="kicker kickerLight">What remains after the pilot</span><h2>Artifacts,<br/><em>not AI theatre.</em></h2></div><div><p>Current-state map · candidate backlog · prototype / automation · test cases · human checkpoints · privacy/data boundaries · owner & fallback · operating notes.</p><div className="heroActions"><Link className="button buttonLight" href="/en/projects">Example formats →</Link></div></div></div></section>

      <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Decision gate</span><h2>Ship · Revise · Stop.</h2><p className="sectionSub">Before building, define what acceptable output means: output quality, required human review, acceptable failure modes, data boundaries, fallback and process owner. After testing, the decision follows those criteria rather than how impressive the demo looks.</p></div><div className="steps"><article><span>01</span><h3>Ship</h3><p>Verification criteria pass, the owner accepts the workflow and responsibility for ongoing review is clear.</p></article><article><span>02</span><h3>Revise</h3><p>There is value, but bounded quality, data, UX or operating-rule issues should be fixed in another iteration.</p></article><article><span>03</span><h3>Stop</h3><p>Risk, missing ownership, weak quality or data constraints make adoption worse than the current process. The pilot stops without an obligation to “implement AI”.</p></article></div></div></section>

      <section className="section"><div className="shell splitHead"><div><span className="kicker">First message</span><h2>Six points are enough.</h2></div><div><ol className="numberList"><li>Which process you want to improve.</li><li>Who performs it and who owns it.</li><li>How often it repeats.</li><li>Which inputs it uses.</li><li>What a good output looks like.</li><li>What happens if AI is wrong.</li></ol><div className="heroActions"><Link className="button buttonPrimary" href="/en/start">Prepare the brief →</Link></div></div></div></section>
    </main>
    <Footer locale="en" />
  </>;
}
