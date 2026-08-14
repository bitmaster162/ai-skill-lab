import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { ProgramMatcher } from "@/components/ProgramMatcher";

export const metadata: Metadata = {
  title: "Find an AI program",
  description: "Local program matcher for adults, kids, teens or a business pilot. Nothing is sent or stored.",
  alternates: { canonical: "/en/matcher", languages: { ru: "/matcher", en: "/en/matcher" } },
};

export default function Page(){return <><Header locale="en" alternateHref="/matcher"/><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> PROGRAM MATCHER · LOCAL ONLY</div><h1>Find a route<br/><span>without a lead form.</span></h1><p className="heroLead">Three choices produce a starting recommendation for format and package. No answer is sent to a server or stored.</p></div></section><section className="section"><div className="shell"><ProgramMatcher locale="en"/></div></section></main><Footer locale="en"/></>}
