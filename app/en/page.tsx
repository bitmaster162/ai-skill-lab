import type { Metadata } from "next";
import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { ContactButtons } from "@/components/ContactButtons";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { LeadForm } from "@/components/LeadForm";

export const metadata: Metadata = {
  title: "Personal AI education",
  description: "Practical one-to-one AI education for adults, kids, teens and teams: real projects, research, automation and responsible AI use.",
};

const programs = [
  ["01", "AI for work & life", "Use modern models for research, writing, analysis, decisions and repeatable personal workflows.", "1:1 · beginner-friendly", "#contact"],
  ["02", "AI Builder", "Build assistants, automations, agents and lightweight AI products instead of only learning prompts.", "projects · systems", "#contact"],
  ["03", "AI for business", "Map team workflows, identify useful AI insertion points and train people around measurable tasks.", "teams · processes", "#contact"],
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
      <Header locale="en" alternateHref="/" />
      <main>
        <section className="hero heroR2">
          <div className="orb orbOne" /><div className="orb orbTwo" />
          <div className="shell heroGrid">
            <div className="heroCopy">
              <div className="eyebrow"><span className="dot" /> Personal AI education · online / Phuket</div>
              <h1>AI should not make you<br /><span>more dependent.</span></h1>
              <p className="heroLead">It should make you more capable. Learn to research, create, automate and build reliable AI workflows around real tasks.</p>
              <div className="heroActions"><Link className="button buttonPrimary" href="#contact">Find my program <ArrowIcon /></Link><Link className="textLink" href="#programs">Explore tracks <ArrowIcon /></Link></div>
              <div className="heroProofRow"><span>1:1 PERSONAL</span><span>PROJECT-BASED</span><span>RU / EN</span><span>NO FLUFF</span></div>
            </div>
            <div className="heroVisual" aria-label="Practical AI learning system">
              <div className="visualTop"><span>YOUR AI STACK</span><span className="livePill">● BUILD</span></div>
              <div className="visualCore"><div className="coreRing ring1" /><div className="coreRing ring2" /><div className="coreCenter">AI</div><div className="node nodeA">RESEARCH</div><div className="node nodeB">CREATE</div><div className="node nodeC">AUTOMATE</div><div className="node nodeD">VERIFY</div></div>
              <div className="visualBottom"><div><span>01</span><b>GOAL</b></div><i /><div><span>02</span><b>SYSTEM</b></div><i /><div><span>03</span><b>OUTPUT</b></div></div>
            </div>
          </div>
        </section>

        <section className="trustStrip"><div className="shell trustStripGrid"><div><b>Not a mass course</b><span>Route built around the goal</span></div><div><b>Hands-on</b><span>Most time is spent building</span></div><div><b>Visible output</b><span>A project remains at the end</span></div><div><b>Responsible AI</b><span>Verification, privacy, boundaries</span></div></div></section>

        <section className="section" id="programs"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">5 tracks</span><h2>One technology.<br />Very different outcomes.</h2></div><p>We do not force everyone through the same syllabus. First define the outcome; then build the route and tool stack.</p></div><div className="programGrid programGridR2">{programs.map(([num,title,text,meta,href], index)=><article className={`programCard ${index >= 3 ? "youthCard" : ""}`} key={num}><span className="cardIndex">{num}</span><div className="cardSpacer"/><span className="cardMeta">{meta}</span><h3>{title}</h3><p>{text}</p><Link href={href} className="cardLink">Explore <ArrowIcon /></Link></article>)}</div></div></section>

        <section className="section sectionInk"><div className="shell"><div className="sectionHead splitHead sectionHeadLight"><div><span className="kicker kickerLight">What counts as progress</span><h2>Not “I watched it.”<br /><em>I can do it.</em></h2></div><p>Projects are chosen around the learner's goals. We intentionally avoid invented testimonials, income claims or vanity metrics.</p></div><div className="outcomeGrid"><article><span>01</span><h3>PERSONAL OS</h3><p>A reusable set of AI workflows for work, study or personal tasks.</p></article><article><span>02</span><h3>RESEARCH</h3><p>A source-backed brief with verification and a structured conclusion.</p></article><article><span>03</span><h3>AI AGENT</h3><p>An assistant or automation serving one concrete repeatable process.</p></article><article><span>04</span><h3>PORTFOLIO</h3><p>A finished artifact that can be shown and explained.</p></article></div></div></section>

        <section className="kidsBand kidsBandR2"><div className="shell kidsBandGrid"><div><span className="kicker kickerLight">Ages 8–18</span><h2>Kids need more than homework shortcuts.<br />Teens need <em>more than prompts.</em></h2><p>Two separate age tracks: ages 8–13 focus on curiosity, safe habits and creative projects; ages 14–18 move toward research, portfolio work, code and automation.</p><div className="heroActions"><Link className="button buttonLight" href="/en/kids">Kids 8–13 <ArrowIcon /></Link><Link className="button buttonGhost buttonOnDark" href="/en/teens">Teens 14–18 <ArrowIcon /></Link></div></div><div className="ageSplitVisual"><div className="agePanel"><span>8–13</span><b>CREATE<br/>QUESTION<br/>CHECK</b><small>curiosity → project</small></div><div className="agePanel agePanelAcid"><span>14–18</span><b>BUILD<br/>RESEARCH<br/>SHIP</b><small>skill → portfolio</small></div></div></div></section>

        <section className="section" id="format"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Method</span><h2>Goal → practice → system → project</h2></div><p>AI changes too quickly for button-by-button training. The program focuses on transferable ways to specify, verify and build.</p></div><div className="steps"><article><span>01</span><h3>Diagnosis</h3><p>Define current level, interests, constraints and a concrete outcome.</p></article><article><span>02</span><h3>Personal route</h3><p>Remove irrelevant modules and choose only useful tools.</p></article><article><span>03</span><h3>Build by doing</h3><p>Every session produces an artifact or a piece of the final project.</p></article><article><span>04</span><h3>Final project</h3><p>The learner explains the logic, limitations and their own contribution.</p></article></div></div></section>

        <section className="section sectionMuted premiumParents"><div className="shell premiumParentGrid"><div className="premiumParentCopy"><span className="kicker">Premium Family</span><h2>Not just lessons.<br />A managed family AI setup.</h2><p>A higher-touch format: personal track for the child or teen, separate parent sessions, home-use rules and a final project presentation.</p><ul className="featureList"><li>12 personal sessions for the learner</li><li>2 separate parent sessions</li><li>custom final-project theme</li><li>family privacy and AI-use rules</li><li>final project presentation</li></ul></div><article className="premiumPriceCard"><span className="cardMeta">Family Concierge</span><div className="price">$1,490</div><p>Tool choice depends on age and is agreed with the parent before use.</p><Link className="button buttonPrimary buttonWide" href="#contact">Discuss Family</Link><small>Third-party AI subscriptions, if needed, are separate.</small></article></div></section>

        <section className="section" id="pricing"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Pricing</span><h2>Start small if you want<br />to test the format first.</h2></div><p>These prices cover one-to-one adult learning. Youth tracks have their own pages and packages.</p></div><div className="pricingGrid"><article className="priceCard"><span className="cardMeta">Start</span><h3>4 sessions</h3><div className="price">$390</div><p>Build a useful baseline workflow and understand what to learn next.</p><Link className="button buttonGhost buttonWide" href="#contact">Choose Start</Link></article><article className="priceCard featuredPrice"><span className="popular">Core</span><span className="cardMeta">Personal</span><h3>10 sessions</h3><div className="price">$890</div><p>Full personal route with practice, reusable templates and a final project.</p><Link className="button buttonPrimary buttonWide" href="#contact">Choose Personal</Link></article><article className="priceCard"><span className="cardMeta">Intensive</span><h3>12 sessions + project</h3><div className="price">$1,290</div><p>For a more technical automation, agent, mini-product or portfolio project.</p><Link className="button buttonGhost buttonWide" href="#contact">Choose Intensive</Link></article></div></div></section>

        <section className="section" id="faq"><div className="shell faqGrid"><div className="sectionHead stickyHead"><span className="kicker">FAQ</span><h2>The essentials</h2></div><div className="faqList">{faq.map(([q,a])=><details key={q}><summary>{q}<span>+</span></summary><p>{a}</p></details>)}</div></div></section>

        <section className="contactSection" id="contact"><div className="shell contactGrid"><div><span className="kicker kickerLight">Start</span><h2>Start with the outcome.<br />Then build the program.</h2><p>Tell us who the training is for and what should become possible afterwards. For minors, the contact details must belong to an adult.</p><ContactButtons fallbackHref="#contact-form-en" locale="en" /></div><div id="contact-form-en"><LeadForm locale="en" /></div></div></section>
      </main>
      <Footer locale="en" />
    </>
  );
}
