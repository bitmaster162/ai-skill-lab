import type { Metadata } from "next";
import { WorkshopInteractive } from "@/components/workshop/WorkshopInteractive";
import { ProgramMatcher } from "@/components/ProgramMatcher";

export const metadata: Metadata = {
  title: { absolute: "Find an AI program — AI Skill Lab · Phuket" },
  description: "AI-assisted route finder grounded in the published program table with a local fallback. Matcher input is not stored; a brief is sent only with consent.",
  alternates: { canonical: "/en/matcher", languages: { ru: "/matcher", en: "/en/matcher" } },
  twitter: { card: "summary_large_image", title: "Find an AI program", description: "AI-assisted route finder grounded in the published program table with a local fallback.", images: ["/og.png"] },
};

export default function Page(){return <WorkshopInteractive locale="en" alternateHref="/matcher"><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow matcherEyebrow"><span className="dot"/> PROGRAM MATCHER · AI + FALLBACK</div><h1>Find a route<br/><span>without invented prices.</span></h1><p className="heroLead">Three choices plus your goal produce a starting recommendation only from the published program table. AI runs on button press; a local fallback remains available.</p></div></section><section className="section"><div className="shell"><noscript><div className="matcherNoScript"><strong>JavaScript is disabled.</strong><p>The matcher cannot calculate a recommendation, but every package and price remains available without JavaScript.</p><div className="heroActions"><a className="button buttonPrimary" href="/en/pricing">View pricing</a><a className="button buttonGhost" href="/en/start">Start without matcher</a></div></div></noscript><ProgramMatcher locale="en"/></div></section></main></WorkshopInteractive>}
