import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SkillGraph } from "@/components/SkillGraph";

export const metadata: Metadata = {
  title: "AI learning curriculum",
  description: "Compare AI Skill Lab tracks for adults, kids 8–13 and teens 14–18: topics, artifacts, format and depth.",
  alternates: { canonical: "/en/curriculum", languages: { ru: "/curriculum", en: "/en/curriculum" } },
};

const tracks = [
  { meta:"ADULT · 1:1", title:"Adults", text:"From confident model use to research workflows, automation and a useful AI tool.", output:"Outcome: a workflow, automation, assistant or mini-product.", href:"/en/personal" },
  { meta:"KIDS · 8–13", title:"Kids", text:"Creativity, strong questions, research, fact-checking, digital boundaries and a final project.", output:"Outcome: a project the learner can explain and present.", href:"/en/kids" },
  { meta:"TEENS · 14–18", title:"Teens", text:"AI literacy, research, code-thinking, automation, product thinking and a portfolio artifact.", output:"Outcome: a finished artifact with visible personal contribution.", href:"/en/teens" },
];

const adult = [
  ["01","Diagnosis","Tasks, current level, constraints and a useful success criterion."],
  ["02","Context & specification","Requirements, quality criteria and expected output format."],
  ["03","Research","Sources, competing claims, fact-checking and uncertainty."],
  ["04","Reusable patterns","Instructions, templates and repeatable scenarios for real work."],
  ["05","Data & documents","Supplying source material, controlling context and validating conclusions."],
  ["06","Automation","Breaking a repeated task into steps and designing an automatable workflow."],
  ["07","AI assistant","Roles, rules, inputs/outputs, failure cases and responsibility boundaries."],
  ["08","Quality control","Edge cases, hallucinations, sources, privacy and human checkpoints."],
  ["09","Project build","Integrating the skills into one workflow or tool."],
  ["10","Handoff","README, operating rules, improvements and the next independent iteration."],
];

const youth = [
  ["1–2","Understand the tool","What AI can do, where it fails, how to give context and why answers need checking."],
  ["3–4","Create","Ideas, writing, visuals or interaction while preserving the learner's own intent."],
  ["5–6","Research","Sources, fact comparison, presentation structure and explaining a conclusion."],
  ["7–8","Build","Algorithmic thinking, simple logic, a prototype, game or mini-product."],
  ["9–10","Defend the project","Final build, verification, personal contribution and an independent presentation."],
];

export default function CurriculumPage() {
  return <>
    <Header locale="en" contactHref="/en/start" alternateHref="/curriculum" />
    <main id="main">
      <section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot" /> CURRICULUM · OUTCOME FIRST</div><h1>Not a list of buttons.<br/><span>A path to an outcome.</span></h1><p className="heroLead">Topics adapt to level and goal. The structure below shows what is learned and what should exist at the end before anyone commits to a package.</p><div className="heroActions"><Link className="button buttonPrimary" href="/en/pricing">Compare packages →</Link><Link className="button buttonGhost" href="/en/start">Choose a program →</Link></div></div></section>
      <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">Three tracks</span><h2>One principle: learn on a real task.</h2></div><div className="programGrid">{tracks.map((track)=><article className="programCard" key={track.title}><span className="cardMeta">{track.meta}</span><h3>{track.title}</h3><p>{track.text}</p><p><b>{track.output}</b></p><Link className="textLink" href={track.href}>Open the track →</Link></article>)}</div></div></section>
      <section className="section sectionInk"><div className="shell"><div className="sectionHead splitHead sectionHeadLight"><div><span className="kicker kickerLight">AI Skill Graph</span><h2>Different context.<br/><em>Same operating discipline.</em></h2></div><p>Switch Adult / Kids / Teens / Business. Each route changes the depth and ownership model, while Think → Build → Verify → Ship stays explicit.</p></div><SkillGraph locale="en"/></div></section><section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Adults · example 10-session core</span><h2>From task definition to a working AI process.</h2><p className="sectionSub">This is a baseline, not a rigid calendar. Technical and business goals shift the depth of individual blocks.</p></div><div className="curriculumList">{adult.map(([n,t,d])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div></div></section>
      <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">Youth · logic of a 10-session route</span><h2>Understand → create → verify → explain.</h2><p className="sectionSub">Kids and Teens differ in complexity, independence and technical depth; organizational contact for minors stays with an adult.</p></div><div className="curriculumList">{youth.map(([n,t,d])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div><div className="heroActions"><Link className="button buttonGhost" href="/en/kids">Kids 8–13 →</Link><Link className="button buttonGhost" href="/en/teens">Teens 14–18 →</Link><Link className="button buttonGhost" href="/en/parents">For parents →</Link></div></div></section>
      <section className="section sectionInk"><div className="shell splitHead"><div><span className="kicker kickerLight">How progress is measured</span><h2>Artifact + explanation.<br/><em>Not prompt count.</em></h2></div><div><p>The learner should be able to define the task, explain the decision, verify the result, name limitations and repeat the process without constant instructor prompting.</p><div className="heroActions"><Link className="button buttonLight" href="/en/projects">Example projects →</Link><Link className="button buttonGhost buttonOnDark" href="/en/method">Learning method →</Link></div></div></div></section>
    </main>
    <Footer locale="en" />
  </>;
}
