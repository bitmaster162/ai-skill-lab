import type { Metadata } from "next";
import Link from "next/link";
import { WorkshopEditorial } from "@/components/workshop/WorkshopEditorial";

export const metadata: Metadata = {
  title: { absolute: "Certificate and completion record — AI Skill Lab · Phuket" },
  description: "How AI Skill Lab handles completion records: verifiable project, completion record, separate publication consent and zero public PII for minors.",
  alternates: { canonical: "/en/certificate", languages: { ru: "/certificate", en: "/en/certificate" } },
};

const record = [
  ["01","Completed scope","A record can reflect only an actually completed agreed program or project — not attendance for its own sake."],
  ["02","Verifiable artifact","The outcome remains a project, workflow, research output, prototype or other work the learner can explain and verify."],
  ["03","Personal contribution","AI may assist, but a completion record does not replace checking that the learner understands the decisions and personal contribution."],
  ["04","Boundaries","This is not accreditation, school or university credit, a professional qualification, or a security/compliance certification."],
];

export default function Page(){
  return <WorkshopEditorial locale="en" alternateHref="/certificate" contactHref="/en/start"><main id="main">
    <section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> N25 · COMPLETION RECORD · CONSENT-BOUND</div><h1>Project first.<br/><span>Record second.</span></h1><p className="heroLead">AI Skill Lab may issue a completion record after real work is finished. The certificate is not the primary learning outcome and does not turn the program into accreditation or an external qualification.</p></div></section>
    <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">WHAT IT CAN PROVE</span><h2>Record completion.<br/>Do not manufacture a credential.</h2><p>A completion record is bound to finished work and a verifiable result. It must not claim more than the evidence supports.</p></div><div className="steps">{record.map(([n,t,d])=><article key={n}><span>{n}</span><h2>{t}</h2><p>{d}</p></article>)}</div></div></section>
    <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">TEMPLATE · NOT ISSUED</span><h2>No real learner is<br/>shown on this page.</h2><p>The current public route is policy and template only. No student record has been issued here and no learner identity is claimed.</p></div><div className="steps"><article><span>01</span><h2>Status</h2><p>TEMPLATE · NOT ISSUED</p></article><article><span>02</span><h2>Learner</h2><p>Not published. No real name or identifier appears here.</p></article><article><span>03</span><h2>Basis</h2><p>Project work + the ability to explain the result.</p></article><article><span>04</span><h2>Public verification</h2><p>Not enabled. A real verification record requires a separate owner-approved fact and consent.</p></article></div></div></section>
    <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">CONSENT & YOUTH PRIVACY</span><h2>Private by default.</h2><p>A public record appears only after separate consent to publication. Without that consent, no record is published.</p></div><div className="steps"><article><span>A</span><h2>Adults</h2><p>A name or other identifiers may appear only after separate explicit consent and owner verification of the facts.</p></article><article><span>B</span><h2>Minors</h2><p>A public page must not contain a name, age, photo, school, contact, username, account/repository links or other personal identifiers. Program coordination stays with an adult.</p></article><article><span>C</span><h2>No consent</h2><p>No public student record. Private learning outcomes and project work remain separate from the public website.</p></article><article><span>D</span><h2>Data requests</h2><p>Application data and correction/deletion requests are covered by the privacy policy.</p></article></div><div className="heroActions"><Link className="button buttonPrimary" href="/en/projects">See real projects →</Link><Link className="button buttonGhost" href="/en/privacy">Privacy →</Link></div></div></section>
  </main></WorkshopEditorial>;
}
