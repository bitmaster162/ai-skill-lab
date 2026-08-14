import type { Metadata } from "next";
import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { ContactButtons } from "@/components/ContactButtons";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { LeadForm } from "@/components/LeadForm";

export const metadata: Metadata = { title: "AI for kids ages 8–13", description: "One-to-one AI learning for ages 8–13 through creativity, research, verification, privacy and a final project." };

const lessons = [
  ["01","AI without magic","What AI can and cannot do, and why confident answers can still be wrong."],
  ["02","Better questions","Context, constraints and iterative improvement instead of one-shot prompts."],
  ["03","Visual worlds","Create characters, images and a coherent visual language for a project."],
  ["04","Story with AI","Plot, characters, logic and editing while keeping authorship with the child."],
  ["05","AI researcher","Find information, compare sources and separate facts from plausible invention."],
  ["06","Presentation","Turn a topic into a clear visual story that can be explained out loud."],
  ["07","Logic & algorithms","Break a task into steps and learn the beginnings of computational thinking."],
  ["08","Mini game","Build a small interactive project with rules, states and feedback."],
  ["09","My AI project","Plan the final work: goal, structure, materials, verification and improvement."],
  ["10","Demo day","Finish and present the project, explaining what was done independently and where AI helped."],
];

export default function EnglishKids() {
  return <><Header locale="en" contactHref="#kids-contact" alternateHref="/kids"/><main>
    <section className="kidsHero"><div className="shell kidsHeroGrid"><div><div className="eyebrow eyebrowLight"><span className="dot dotLight"/> Ages 8–13 · one-to-one</div><h1>AI is not a button<br/><span>that does it for you.</span></h1><p>It is a tool for imagining, researching, creating and learning to ask better questions — with verification and privacy built in.</p><div className="heroActions"><Link className="button buttonLight" href="#kids-contact">Talk about the program <ArrowIcon/></Link><Link className="textLink textLinkLight" href="#curriculum">See 10 sessions <ArrowIcon/></Link></div></div><div className="kidsHeroBoard"><div className="boardLabel">FINAL PROJECT</div><div className="boardCanvas"><div className="boardCard bc1">IDEA<br/><b>→</b></div><div className="boardCard bc2">RESEARCH<br/><b>→</b></div><div className="boardCard bc3">CREATE<br/><b>→</b></div><div className="boardCenter">MY<br/>AI<br/>PROJECT</div></div><div className="boardFoot"><span>10 LESSONS</span><span>REAL OUTPUT</span></div></div></div></section>
    <section className="section"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Approach</span><h2>Build capability, not AI dependency</h2></div><p>The child learns to think before asking, verify after receiving an answer and understand the tool's boundaries.</p></div><div className="kidsPrinciples"><article><span>01</span><h3>Idea first</h3><p>The child starts with their own intent; AI helps develop it.</p></article><article><span>02</span><h3>Verification matters</h3><p>We examine errors and compare claims with reliable sources.</p></article><article><span>03</span><h3>Privacy by default</h3><p>No unnecessary personal information and clear digital boundaries.</p></article><article><span>04</span><h3>Project over prompt</h3><p>Progress means being able to design, build, explain and improve something.</p></article></div></div></section>
    <section className="section sectionMuted" id="curriculum"><div className="shell"><div className="sectionHead"><span className="kicker">Curriculum</span><h2>10 sessions → one finished project</h2><p className="sectionSub">Themes adapt to the child's age and interests: science, animals, games, art, music or technology.</p></div><div className="curriculumList">{lessons.map(([n,t,x])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{x}</p></article>)}</div></div></section>
    <section className="section sectionMuted"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Pricing</span><h2>45–60 minutes per session</h2></div><p>One-to-one. Pace and complexity adapt to the learner.</p></div><div className="pricingGrid"><article className="priceCard"><span className="cardMeta">Mini</span><h3>4 sessions</h3><div className="price">$290</div><p>A creative introduction and a small project.</p><Link className="button buttonGhost buttonWide" href="#kids-contact">Choose Mini</Link></article><article className="priceCard featuredPrice"><span className="popular">Core</span><span className="cardMeta">Creator</span><h3>10 sessions</h3><div className="price">$890</div><p>Full route from fundamentals to a self-presented final project.</p><Link className="button buttonPrimary buttonWide" href="#kids-contact">Choose Creator</Link></article><article className="priceCard"><span className="cardMeta">Studio</span><h3>12 sessions</h3><div className="price">$1,190</div><p>More time for visual work, a complex project or first technical experiments.</p><Link className="button buttonGhost buttonWide" href="#kids-contact">Choose Studio</Link></article></div></div></section>
    <section className="familyConciergeBand"><div className="shell familyConciergeGrid"><div><span className="kicker kickerLight">Family Concierge</span><h2>A higher-touch format for families.</h2><p>12 learner sessions + 2 parent sessions + custom project + home AI-use rules.</p></div><div className="familyConciergePrice"><span>PREMIUM</span><b>$1,490</b><Link className="button buttonLight buttonWide" href="#kids-contact">Discuss Family</Link></div></div></section>
    <section className="contactSection" id="kids-contact"><div className="shell contactGrid"><div><span className="kicker kickerLight">For parents</span><h2>Tell us what your child is curious about.</h2><p>We will propose a first-project direction and explain the format. Contact details must belong to an adult.</p><ContactButtons fallbackHref="#kids-form-en" locale="en"/></div><div id="kids-form-en"><LeadForm defaultAudience="parent" locale="en" program="kids-8-13"/></div></div></section>
  </main><Footer locale="en"/></>;
}
