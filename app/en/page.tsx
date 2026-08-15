import type { Metadata } from "next";
import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { ContactButtons } from "@/components/ContactButtons";
import { Footer } from "@/components/Footer";
import { JsonLd } from "@/components/JsonLd";
import { organizationSchemaEn, websiteSchema } from "@/lib/structured-data";
import { Header } from "@/components/Header";
import { HeroEngine } from "@/components/HeroEngine";

export const metadata: Metadata = {
  title: "Personal AI education",
  description: "Practical one-to-one AI education for adults, kids, teens and teams: real projects, research, automation and responsible AI use.",
  alternates: { canonical: "/en", languages: { ru: "/", en: "/en" } },
};

const programs = [
  ["01", "AI for work & life", "Use modern models for research, writing, analysis, decisions and repeatable personal workflows.", "1:1 · beginner-friendly", "/en/start"],
  ["02", "AI Builder", "Build assistants, automations, agents and lightweight AI products instead of only learning prompts.", "projects · systems", "/en/start"],
  ["03", "AI for business", "Map team workflows, identify useful AI insertion points and train people around measurable tasks.", "teams · processes", "/en/start"],
  ["04", "AI for kids", "Ages 8–13: creativity, research, critical thinking, privacy and a project they can explain themselves.", "8–13 · adult contact", "/en/kids"],
  ["05", "AI for teens", "Ages 14–18: research, code, automation, portfolio work and the beginnings of real AI product thinking.", "14–18 · portfolio", "/en/teens"],
];

const faq = [
  ["Do I need to know how to code?", "No. Core programs can start without code. Technical tools are introduced only when they serve the learner's goal."],
  ["Is this a recorded course?", "No. The core format is one-to-one, project-based work. Templates and project materials stay with the learner."],
  ["Which AI tools do you teach?", "Tools are selected by task. The objective is a transferable method for specifying, verifying and building — not dependency on one interface."],
  ["Can children and teenagers join?", "Yes. Ages 8–13 and 14–18 have separate tracks. Applications and contact details for minors are handled by an adult."],
  ["What is the output?", "A finished artifact: a workflow, research brief, assistant, presentation, mini-product or portfolio project — not attendance alone."],
];

export default function EnglishHome() {
  return (
    <>
      <JsonLd data={[websiteSchema, organizationSchemaEn]} />
      <Header locale="en" alternateHref="/" />
      <main>
        <section className="hero heroR2">
          <div className="orb orbOne" /><div className="orb orbTwo" />
          <div className="shell heroGrid">
            <div className="heroCopy">
              <div className="eyebrow"><span className="dot" /> Personal AI education · online / Phuket</div>
              <h1>AI should not make you<br /><span>more dependent.</span></h1>
              <p className="heroLead">It should make you more capable. Learn to research, create, automate and build reliable AI workflows around real tasks.</p>
              <div className="heroActions"><Link className="button buttonPrimary" href="/en/start">Find my program <ArrowIcon /></Link><Link className="textLink" href="#programs">Explore tracks <ArrowIcon /></Link></div>
              <div className="heroProofRow"><span>1:1 PERSONAL</span><span>PROJECT-BASED</span><span>RU / EN</span><span>NO FLUFF</span></div>
            </div>
            <HeroEngine locale="en" />
          </div>
        </section>

        <section className="trustStrip"><div className="shell trustStripGrid"><div><b>Not a mass course</b><span>Route built around the goal</span></div><div><b>Hands-on</b><span>Most time is spent building</span></div><div><b>Visible output</b><span>A project remains at the end</span></div><div><b>Responsible AI</b><span>Verification, privacy, boundaries</span></div></div></section>

        <section className="proofHome"><div className="shell proofHomeGrid"><div><span className="kicker">Site as proof</span><h2>This site does not tell you<br/><em>we can build with AI.</em><br/>It shows you.</h2><p>Source/static parity, tracker-free privacy, hashed CSP, runtime smoke tests, a release manifest and byte-exact reconstruction. These are actual project gates, not decorative badges.</p><div className="proofHomeActions"><Link className="button buttonLight" href="/en/proof">Open Proof Lab →</Link><a className="button buttonGhost" href="/_release.json">Release manifest ↗</a></div></div><div className="proofHomeBoard" aria-label="Release system checks"><div className="proofBoardTop"><span>AI SKILL LAB / BUILD PROOF</span><b>● LOCAL VERIFIED</b></div><div className="proofBoardRows"><p><span>01</span><b>broken_links</b><strong className="ok">0 / PASS</strong></p><p><span>02</span><b>public_forms + trackers</b><strong className="ok">0 / PASS</strong></p><p><span>03</span><b>client_runtime</b><strong>SMOKE TESTED</strong></p><p><span>04</span><b>script_policy</b><strong>HASHED CSP</strong></p><p><span>05</span><b>release_payload</b><strong>SHA-256</strong></p><p><span>06</span><b>reconstruction</b><strong className="ok">BYTE-EXACT</strong></p></div><div className="proofBoardFoot"><span>DEFINE</span><i/><span>BUILD</span><i/><span>VERIFY</span><i/><span>SHIP</span></div></div></div></section>

        <section className="section" id="programs"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">5 tracks</span><h2>One technology.<br />Very different outcomes.</h2></div><p>We do not force everyone through the same syllabus. First define the outcome; then build the route and tool stack.</p></div><div className="programGrid programGridR2">{programs.map(([num,title,text,meta,href], index)=><article className={`programCard ${index >= 3 ? "youthCard" : ""}`} key={num}><span className="cardIndex">{num}</span><div className="cardSpacer"/><span className="cardMeta">{meta}</span><h3>{title}</h3><p>{text}</p><Link href={href} className="cardLink">Explore <ArrowIcon /></Link></article>)}</div></div></section>

        <section className="section sectionInk"><div className="shell"><div className="sectionHead splitHead sectionHeadLight"><div><span className="kicker kickerLight">AI Capability Matrix</span><h2>Not a bag of prompts.<br /><em>A system from input to shipped output.</em></h2></div><p>Four kinds of work we turn into governed processes. AI accelerates the build layer; the human owns criteria, verification and release.</p></div><div className="outcomeGrid"><article><span>01</span><h3>RESEARCH</h3><p><b>INPUT</b> A fuzzy question, many sources and conflicting claims.</p><p><b>AI LAYER</b> Search expansion, evidence comparison, synthesis and uncertainty mapping.</p><p><b>HUMAN GATE</b> Source quality, disputed points, assumptions and final judgement.</p><p><b>SHIP</b> Source-backed brief + source map + next action.</p></article><article><span>02</span><h3>BUILD</h3><p><b>INPUT</b> A product, assistant or internal-tool idea.</p><p><b>AI LAYER</b> Specification, UI/code options, prototyping and test scaffolding.</p><p><b>HUMAN GATE</b> Scope, product decisions, QA, limitations and release gate.</p><p><b>SHIP</b> Working prototype + tests + known limits + handoff.</p></article><article><span>03</span><h3>AUTOMATE</h3><p><b>INPUT</b> A repeatable process consuming time and attention.</p><p><b>AI LAYER</b> Decomposition, routing, transformations, templates and glue code.</p><p><b>HUMAN GATE</b> Permissions, failure modes, rollback, owner and acceptance criteria.</p><p><b>SHIP</b> Workflow / agent + fallback + operating instructions.</p></article><article><span>04</span><h3>TEACH</h3><p><b>INPUT</b> A skill a person wants to apply independently.</p><p><b>AI LAYER</b> Explanation, exercises, alternatives, draft critique and practice.</p><p><b>HUMAN GATE</b> Understanding, authorship, fact-checking and ability to defend the work.</p><p><b>SHIP</b> Project + explanation + repeatable process + checklist.</p></article></div></div></section>

        <section className="kidsBand kidsBandR2"><div className="shell kidsBandGrid"><div><span className="kicker kickerLight">Ages 8–18</span><h2>Kids need more than homework shortcuts.<br />Teens need <em>more than prompts.</em></h2><p>Two separate age tracks: ages 8–13 focus on curiosity, safe habits and creative projects; ages 14–18 move toward research, portfolio work, code and automation.</p><div className="heroActions"><Link className="button buttonLight" href="/en/kids">Kids 8–13 <ArrowIcon /></Link><Link className="button buttonGhost buttonOnDark" href="/en/teens">Teens 14–18 <ArrowIcon /></Link></div></div><div className="ageSplitVisual"><div className="agePanel"><span>8–13</span><b>CREATE<br/>QUESTION<br/>CHECK</b><small>curiosity → project</small></div><div className="agePanel agePanelAcid"><span>14–18</span><b>BUILD<br/>RESEARCH<br/>SHIP</b><small>skill → portfolio</small></div></div></div></section>

        <section className="section" id="format"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Method</span><h2>Goal → practice → system → project</h2></div><p>AI changes too quickly for button-by-button training. The program focuses on transferable ways to specify, verify and build.</p></div><div className="steps"><article><span>01</span><h3>Diagnosis</h3><p>Define current level, interests, constraints and a concrete outcome.</p></article><article><span>02</span><h3>Personal route</h3><p>Remove irrelevant modules and choose only useful tools.</p></article><article><span>03</span><h3>Build by doing</h3><p>Every session produces an artifact or a piece of the final project.</p></article><article><span>04</span><h3>Final project</h3><p>The learner explains the logic, limitations and their own contribution.</p></article></div></div></section>

        <section className="section sectionMuted premiumParents"><div className="shell premiumParentGrid"><div className="premiumParentCopy"><span className="kicker">Premium Family</span><h2>Not just lessons.<br />A managed family AI setup.</h2><p>A higher-touch format: personal track for the child or teen, separate parent sessions, home-use rules and a final project presentation.</p><ul className="featureList"><li>12 personal sessions for the learner</li><li>2 separate parent sessions</li><li>custom final-project theme</li><li>family privacy and AI-use rules</li><li>final project presentation</li></ul></div><article className="premiumPriceCard"><span className="cardMeta">Family Concierge</span><div className="price">$1,490</div><p><strong>12 learner sessions + 2 parent sessions</strong></p><p>Tool choice depends on age and is agreed with the parent before use.</p><Link className="button buttonPrimary buttonWide" href="/en/start">Discuss Family</Link><small>Third-party AI subscriptions, if needed, are separate.</small></article></div></section>

        <section className="section" id="pricing"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Pricing</span><h2>Start small if you want<br />to test the format first.</h2></div><p>These prices cover one-to-one adult learning. Youth tracks have their own pages and packages.</p></div><div className="pricingGrid"><article className="priceCard"><span className="cardMeta">Start</span><h3>4 sessions</h3><div className="price">$390</div><p>Build a useful baseline workflow and understand what to learn next.</p><Link className="button buttonGhost buttonWide" href="/en/start">Choose Start</Link></article><article className="priceCard featuredPrice"><span className="popular">Core</span><span className="cardMeta">Personal</span><h3>10 sessions</h3><div className="price">$890</div><p>Full personal route with practice, reusable templates and a final project.</p><Link className="button buttonPrimary buttonWide" href="/en/start">Choose Personal</Link></article><article className="priceCard"><span className="cardMeta">Intensive</span><h3>12 sessions + project</h3><div className="price">$1,290</div><p>For a more technical automation, agent, mini-product or portfolio project.</p><Link className="button buttonGhost buttonWide" href="/en/start">Choose Intensive</Link></article></div></div></section>

        <section className="section instructorSection"><div className="shell instructorGrid"><div className="instructorBadge"><span>HUMAN<br />IN THE<br />LOOP</span></div><div><span className="kicker">Robert · founder / instructor</span><h2>Training built from practice,<br />not from slides.</h2><p>I build and use AI systems in real work: research workflows, agents, automation, decision workflows and digital products. Sessions use real tasks: define, build, test and fix weak points.</p><div className="expertiseTags"><span>AI WORKFLOWS</span><span>AGENTS</span><span>RESEARCH</span><span>AUTOMATION</span><span>PRODUCT</span></div><p className="finePrint">No invented client logos, testimonials or income claims. Proof of progress is an output the learner can show and explain.</p></div></div></section>

        <section className="section" id="faq"><div className="shell faqGrid"><div className="sectionHead stickyHead"><span className="kicker">FAQ</span><h2>The essentials</h2></div><div className="faqList">{faq.map(([q,a])=><details key={q}><summary>{q}<span>+</span></summary><p>{a}</p></details>)}</div></div></section>

        <section className="contactSection" id="contact"><div className="shell contactGrid"><div><span className="kicker kickerLight">Start · contact-only</span><h2>Start with the outcome.<br />Then build the program.</h2><p>Tell us who the training is for and what should become possible afterwards. For minors, the contact details must belong to an adult.</p><ContactButtons fallbackHref="/en/start" locale="en" /></div><div className="contactOnlyCard"><span className="cardMeta">Short brief</span><h3>No form and no unnecessary data</h3><p>Include who the training is for, the goal, current level and online / Phuket format. For a minor, age and interests are enough at first.</p><Link className="button buttonPrimary buttonWide" href="/en/start">What to send →</Link></div></div></section>
      </main>
      <Footer locale="en" />
    </>
  );
}
