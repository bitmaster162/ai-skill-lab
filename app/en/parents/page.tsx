import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "For parents",
  description: "How one-to-one AI learning works for ages 8–18: visible progress, age rules, youth tracks and a separate family layer.",
  alternates: { canonical: "/en/parents", languages: { ru: "/parents", en: "/en/parents" } },
};

export default function Page() {
  return <>
    <Header locale="en" contactHref="/en/start" alternateHref="/parents" />
    <main id="main">
      <section className="kidsHero"><div className="shell kidsHeroGrid"><div>
        <div className="eyebrow eyebrowLight"><span className="dot dotLight" /> FOR PARENTS · 8–18</div>
        <h1>Not “AI did it.”<br/><span>The learner can do it.</span></h1>
        <p>Progress is visible through the ability to define a task, verify the output, explain personal contribution and defend the final project.</p>
        <div className="heroActions"><Link className="button buttonLight" href="/en/start">Discuss a route →</Link><Link className="button buttonGhost buttonOnDark" href="/en/projects">Example projects →</Link></div>
      </div></div></section>

      <section className="section"><div className="shell">
        <div className="sectionHead"><span className="kicker">PROGRESS RUBRIC</span><h2>Capability should be visible.</h2></div>
        <div className="kidsPrinciples">
          <article><span>01</span><h3>Defines the goal</h3><p>The learner can explain what they are trying to produce and why.</p></article>
          <article><span>02</span><h3>Checks claims</h3><p>An AI answer is not treated as fact just because it sounds confident.</p></article>
          <article><span>03</span><h3>Explains personal contribution</h3><p>The learner can separate their own decisions from AI assistance.</p></article>
          <article><span>04</span><h3>Defends the final project</h3><p>The output must be explainable, reviewable and improvable.</p></article>
        </div>
      </div></section>

      <section className="section sectionMuted"><div className="shell">
        <div className="sectionHead"><span className="kicker">What the family buys</span><h2>Not tool access. A learning system.</h2></div>
        <div className="pricingGrid">
          <article className="priceCard"><span className="cardMeta">ROUTE</span><h3>Personal route</h3><p>Topics and the project are selected around the learner’s interests, not a generic prompt list.</p></article>
          <article className="priceCard"><span className="cardMeta">VISIBLE PROGRESS</span><h3>Checkable output</h3><p>Sessions leave artifacts and a final project the learner must be able to explain.</p></article>
          <article className="priceCard"><span className="cardMeta">PARENT LOOP</span><h3>Adult in the loop</h3><p>Coordination, age requirements and tool selection are discussed with an adult.</p></article>
        </div>
      </div></section>

      <section className="section"><div className="shell"><div className="sectionHead">
        <span className="kicker">Age rules</span><h2>ChatGPT and age.</h2>
        <p>ChatGPT is not meant for children under 13. Users ages 13–18 need permission from a parent or legal guardian. In an educational context for a child under 13, the actual interaction with ChatGPT is conducted by an adult.</p>
        <div className="heroActions"><a className="textLink" href="https://help.openai.com/en/articles/8313401" target="_blank" rel="noopener noreferrer">Official OpenAI guidance →</a><Link className="textLink" href="/en/safety">Our safety approach →</Link></div>
      </div></div></section>

      <section className="section sectionMuted"><div className="shell">
        <div className="sectionHead"><span className="kicker">Formats 8–13</span><h2>Three levels of depth.</h2></div>
        <div className="pricingGrid">
          <article className="priceCard"><span className="cardMeta">Mini</span><h3>4 sessions</h3><div className="price">$290</div><p>Introduction to the method and a small project.</p></article>
          <article className="priceCard featuredPrice"><span className="cardMeta">Creator</span><h3>10 sessions</h3><div className="price">$890</div><p>Core program and an independent final presentation.</p></article>
          <article className="priceCard"><span className="cardMeta">Studio</span><h3>12 sessions</h3><div className="price">$1,190</div><p>More time for a complex, visual or technical project.</p></article>
        </div>
      </div></section>

      <section className="section"><div className="shell">
        <div className="sectionHead"><span className="kicker">Formats 14–18</span><h2>From literacy to portfolio.</h2></div>
        <div className="pricingGrid">
          <article className="priceCard"><span className="cardMeta">Explorer</span><h3>6 sessions</h3><div className="price">$490</div><p>AI literacy, research and a small project.</p></article>
          <article className="priceCard featuredPrice"><span className="cardMeta">Portfolio</span><h3>10 sessions</h3><div className="price">$890</div><p>Full route with a finished project.</p></article>
          <article className="priceCard"><span className="cardMeta">Builder</span><h3>12 sessions</h3><div className="price">$1,290</div><p>More code, automation and product thinking.</p></article>
        </div>
      </div></section>

      <section className="section sectionMuted"><div className="shell premiumParentGrid"><div>
        <span className="kicker">Family Concierge</span><h2>12 learner sessions + 2 parent sessions</h2>
        <p>Expanded route, separate parent loop, a final project and family AI-use rules.</p>
      </div><article className="premiumPriceCard"><div className="price">$1,490</div><Link className="button buttonPrimary buttonWide" href="/en/start">Discuss Family</Link></article></div></section>

      <section className="section"><div className="shell"><div className="sectionHead">
        <span className="kicker">First brief</span><h2>Age + interest + goal is enough.</h2>
        <p>You do not need to choose tools in advance or send unnecessary personal data about the learner.</p>
        <Link className="button buttonPrimary" href="/en/start">How to start →</Link>
      </div></div></section>
    </main>
    <Footer locale="en" />
  </>;
}
