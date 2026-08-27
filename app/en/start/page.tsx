import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { CopyBriefButton } from "@/components/CopyBriefButton";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Start",
  description: "Choose a request type and send a short Telegram brief for an adult, child, teen, AI Studio build or business workflow.",
  alternates: { canonical: "/en/start", languages: { ru: "/start", en: "/en/start" } },
  twitter: { card: "summary_large_image", title: "Start", description: "Choose a request type and send a short Telegram brief for an adult, child, teen, AI Studio build or business workflow.", images: ["/opengraph-image"] },
};

const briefs = [
  { meta:"ADULT", title:"Personal program", href:"/en/personal", lines:["Goal for the next 1–3 months","Which tasks repeat today","Which AI tools you already use","Online / Phuket · RU / EN"] },
  { meta:"KIDS · 8–13", title:"For a child", href:"/en/kids", lines:["Age","What the learner is interested in","Any prior AI experience","What kind of project might be motivating"] },
  { meta:"TEENS · 14–18", title:"For a teen", href:"/en/teens", lines:["Age and current level","Interests: code / design / science / content / business","What they already tried with AI","Which portfolio outcome would be useful"] },
  { meta:"AI STUDIO", title:"AI Studio / build", href:"/en/studio", lines:["What you want to build or change","What happens today / what already exists","Who will use it and who owns the outcome","What counts as done / where failure would be costly"] },
  { meta:"BUSINESS", title:"Workflow pilot", href:"/en/business", lines:["Which process you want to improve","Who performs and owns it","How often it repeats","What good output looks like and what happens if AI is wrong"] },
];

export default function StartPage(){return <>
  <Header locale="en" contactHref={site.telegram} alternateHref="/start"/>
  <main id="main">
    <section className="contactSection"><div className="shell contactGrid"><div><span className="kicker kickerLight">START · no form</span><h2>Fit first.<br/>Program second.</h2><p>Choose a request type below and send a short brief. For a minor, organizational contact stays with an adult.</p><div className="contactButtons"><Link className="button buttonLight" href="/en/matcher">Find my route →</Link><a className="button buttonGhost buttonOnDark" href={site.telegram} target="_blank" rel="noopener noreferrer">Open Telegram →</a></div></div><div className="contactOnlyCard"><span className="cardMeta">What not to send</span><h3>Minimum data.</h3><p>No identity documents, child home/school address, passwords, API keys, payment details or sensitive corporate data are needed.</p><small>Scope, pricing, payment and rescheduling terms are confirmed before any payment.</small></div></div></section>

    <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">Choose a brief</span><h2>Five messages that remove an unnecessary call.</h2><p className="sectionSub">The answers do not need to be perfect. They provide enough context to recommend a sensible route.</p></div><noscript><div className="briefNoScript"><strong>JavaScript is disabled.</strong><p>Copy buttons are unavailable, but you can copy the brief fields manually and open Telegram directly.</p><a className="button buttonGhost" href={site.telegram} target="_blank" rel="noopener noreferrer">Open Telegram →</a></div></noscript><div className="programGrid">{briefs.map((b)=><article className="programCard" key={b.meta}><span className="cardMeta">{b.meta}</span><h3>{b.title}</h3><ol className="numberList">{b.lines.map((x)=><li key={x}>{x}</li>)}</ol><div className="briefCardActions"><CopyBriefButton title={b.title} lines={b.lines} locale="en"/><Link className="textLink" href={b.href}>View the track →</Link></div></article>)}</div></div></section>

    <section className="section sectionMuted"><div className="shell splitHead"><div><span className="kicker">What happens next</span><h2>No hidden checkout.</h2></div><div><ol className="numberList"><li>Confirm the goal and format.</li><li>Recommend a suitable package or a smaller starting point.</li><li>Confirm scope, schedule, payment and rescheduling terms.</li><li>Only then does the program start.</li></ol></div></div></section>
  </main>
  <Footer locale="en"/>
</>}
