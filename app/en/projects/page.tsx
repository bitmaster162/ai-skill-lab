import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Example AI projects",
  description: "Example AI learning projects for kids, teens, adults and business — clearly labeled as examples, not client case studies.",
  alternates: { canonical: "/en/projects", languages: { ru: "/projects", en: "/en/projects" } },
};

const groups = [
  ["Ages 8–13", "Create and explain.", [
    ["01 · RESEARCH", "Fact detective", "Topic → 3+ sources → claim table → short presentation of what was verified and what was not."],
    ["02 · CREATE", "World & character", "Character bible, visual rules, storyboard and a short final story with clear separation between the learner’s idea and AI assistance."],
    ["03 · LOGIC", "Mini game", "Rules, states, simple logic and a prototype the learner can explain."],
  ]],
  ["Ages 14–18", "Build for a portfolio.", [
    ["04 · STUDY", "Research OS", "A reusable research template: question, sources, claims, verification, memo and presentation."],
    ["05 · BUILD", "AI assistant prototype", "A simple assistant or workflow for a real task: input, rules, output, failure cases and README."],
    ["06 · PRODUCT", "Mini-product", "User problem, prototype, test scenarios, limitations and a short demo."],
  ]],
  ["Adults / business", "An artifact that remains after training.", [
    ["07 · WORKFLOW", "Personal research workflow", "A repeatable system for search, source comparison, synthesis and verification."],
    ["08 · AUTOMATION", "Process prototype", "An assistant or automation serving one repeatable process, with ownership and fallback."],
    ["09 · PLAYBOOK", "AI operating rules", "Task templates, verification criteria, data boundaries and repeatable instructions."],
  ]],
] as const;

export default function Page() {
  return <><Header locale="en" contactHref="/en/start" alternateHref="/projects"/><main id="main">
    <section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> EXAMPLE OUTPUTS · NOT TESTIMONIALS</div><h1>Show an output,<br/><span>not a promise.</span></h1><p className="heroLead">These are example project formats that can be built during training. They are not claims about specific clients or learners.</p></div></section>
    {groups.map(([label,title,items])=><section className="section" key={label}><div className="shell"><div className="sectionHead"><span className="kicker">{label}</span><h2>{title}</h2></div><div className="programGrid">{items.map(([m,t,d])=><article className="programCard" key={m}><span className="cardMeta">{m}</span><div className="cardSpacer"/><h3>{t}</h3><p>{d}</p></article>)}</div></div></section>)}
    <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Start</span><h2>Choose a project around a real interest.</h2><p>The examples above are not a mandatory syllabus. The final project is selected by goal, age and depth.</p></div><Link className="button buttonPrimary" href="/en/start">Find a route →</Link></div></section>
  </main><Footer locale="en"/></>;
}
