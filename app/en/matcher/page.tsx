import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { ProgramMatcher } from "@/components/ProgramMatcher";

export const metadata: Metadata = {
  title: "Find an AI program",
  description: "Local program matcher for adults, kids, teens or a business pilot. Nothing is sent or stored.",
  alternates: { canonical: "/en/matcher", languages: { ru: "/matcher", en: "/en/matcher" } },
  twitter: { card: "summary_large_image", title: "Find an AI program", description: "Local program matcher for adults, kids, teens or a business pilot. Nothing is sent or stored.", images: ["/opengraph-image"] },
};

export default function Page(){return <><Header locale="en" alternateHref="/matcher"/><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow matcherEyebrow"><span className="dot"/> PROGRAM MATCHER · LOCAL ONLY</div><h1>Find a route<br/><span>without a lead form.</span></h1><p className="heroLead">Three choices produce a starting recommendation for format and package. No answer is sent to a server or stored.</p></div></section><section className="section"><div className="shell"><noscript><div className="matcherNoScript"><strong>JavaScript is disabled.</strong><p>The matcher cannot calculate a recommendation, but every package and price remains available without JavaScript.</p><div className="heroActions"><a className="button buttonPrimary" href="/en/pricing">View pricing</a><a className="button buttonGhost" href="/en/start">Start without matcher</a></div></div></noscript><ProgramMatcher locale="en"/></div></section></main><Footer locale="en"/></>}
