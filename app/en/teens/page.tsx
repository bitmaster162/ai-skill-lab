import type { Metadata } from "next";
import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { ContactButtons } from "@/components/ContactButtons";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { LeadForm } from "@/components/LeadForm";

export const metadata: Metadata = { title: "AI for teens ages 14–18", description: "One-to-one AI education for ages 14–18: research, code, automation, portfolio work and a final AI project." };

const modules = [
  ["01","AI literacy","How modern models work, where they help and why outputs still need verification."],
  ["02","Research system","Sources, comparison, argumentation and concise evidence-based conclusions."],
  ["03","Prompting as specification","Context, criteria, constraints and iteration instead of magic prompt recipes."],
  ["04","Create & present","Writing, visuals and presentations with transparent authorship."],
  ["05","Code with AI","Read, modify and test simple code with AI support even when programming is new."],
  ["06","Automation","Turn repeatable steps into a workflow and identify unsafe automation boundaries."],
  ["07","Product thinking","Problem, user, scenario, prototype and usefulness before features."],
  ["08","Portfolio build","Assemble the project with decisions, sources, limitations and personal contribution documented."],
  ["09","Stress-test","Check failure modes, edge cases, source quality and whether the project actually works."],
  ["10","Demo & next step","Present the work and map the next skill path: code, design, research or automation."],
];

export default function EnglishTeens() {
  return <><Header locale="en" contactHref="#teens-contact" alternateHref="/teens"/><main>
    <section className="teenHero"><div className="shell teenHeroGrid"><div><div className="eyebrow eyebrowLight"><span className="dot dotLight"/> Ages 14–18 · portfolio track</div><h1>Do not only prepare for the future.<br/><span>Start building it.</span></h1><p>AI as a practical skill: research, code, automation, presentations and a project that can actually be shown.</p><div className="heroActions"><Link className="button buttonLight" href="#teens-contact">Find a track <ArrowIcon/></Link><Link className="textLink textLinkLight" href="#teen-program">See curriculum <ArrowIcon/></Link></div></div><div className="teenTerminal"><div className="terminalTop"><span>portfolio_project.ai</span><span>● ACTIVE</span></div><div className="terminalLines"><span><i>01</i> DEFINE PROBLEM</span><span><i>02</i> RESEARCH SOURCES</span><span><i>03</i> BUILD PROTOTYPE</span><span><i>04</i> TEST OUTPUT</span><span><i>05</i> EXPLAIN DECISIONS</span></div><div className="terminalOutput"><small>OUTPUT</small><b>PROJECT THAT CAN BE SHOWN.</b></div></div></div></section>
    <section className="section" id="teen-program"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Curriculum</span><h2>10 modules from AI literacy<br/>to portfolio project</h2></div><p>Depth follows the starting level. Stronger learners move faster toward code and automation.</p></div><div className="curriculumList">{modules.map(([n,t,x])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{x}</p></article>)}</div></div></section>
    <section className="section sectionMuted"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Pricing</span><h2>Three levels of depth</h2></div><p>Start shorter and move into Builder only if the format and interest fit.</p></div><div className="pricingGrid"><article className="priceCard"><span className="cardMeta">Explorer</span><h3>6 sessions</h3><div className="price">$490</div><p>AI literacy + research + one small project.</p><Link className="button buttonGhost buttonWide" href="#teens-contact">Choose Explorer</Link></article><article className="priceCard featuredPrice"><span className="popular">Core</span><span className="cardMeta">Portfolio</span><h3>10 sessions</h3><div className="price">$890</div><p>Full route with a finished project and a personal next-step map.</p><Link className="button buttonPrimary buttonWide" href="#teens-contact">Choose Portfolio</Link></article><article className="priceCard"><span className="cardMeta">Builder</span><h3>12 sessions</h3><div className="price">$1,290</div><p>More code, automation and time for a technical or product project.</p><Link className="button buttonGhost buttonWide" href="#teens-contact">Choose Builder</Link></article></div></div></section>
    <section className="contactSection" id="teens-contact"><div className="shell contactGrid"><div><span className="kicker kickerLight">Start</span><h2>Tell us what the teenager is already curious about.</h2><p>Code, design, games, science, content, business — or no clear direction yet. That is enough to design the first route. For minors, contact and organization go through an adult.</p><ContactButtons fallbackHref="#teens-form-en" locale="en"/></div><div id="teens-form-en"><LeadForm defaultAudience="teen" locale="en" program="teens-14-18"/></div></div></section>
  </main><Footer locale="en"/></>;
}
