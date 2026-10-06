import type { Metadata } from "next";
import { WorkshopInteractive } from "@/components/workshop/WorkshopInteractive";
import Link from "next/link";
import { ProjectStudio } from "@/components/ProjectStudio";
import { RealProjectGallery } from "@/components/RealProjectGallery";

export const metadata: Metadata = {
  title: { absolute: "Projects — real AI builds — AI Skill Lab · Phuket" },
  description: "Publicly verifiable AI projects by Robert Dumanyan plus 9 example learning formats: evidence, claim boundaries, AI role and human verification.",
  alternates: { canonical: "/en/projects", languages: { ru: "/projects", en: "/en/projects" } },
};

export default function Page() {
  return <WorkshopInteractive locale="en" alternateHref="/projects"><main id="main">
    <section className="projectStudioHero"><div className="shell"><div className="eyebrow"><span className="dot"/> REAL BUILDS · PUBLIC PROVENANCE</div><h1>Real builds.<br/><span>And Project Studio.</span></h1><p className="heroLead">First: Robert’s public projects with verifiable repositories and explicit claim boundaries. Below: nine learning examples; they are not client case studies or student work.</p><div className="actions"><a className="button buttonPrimary" href="#real-projects">See real projects ↓</a><Link className="button buttonGhost" href="/en/proof">How we verify AI →</Link></div></div></section>
    <section className="projectStudioSection" id="real-projects"><div className="shell"><div className="sectionHead projectStudioIntro"><span className="kicker">REAL BUILDS / 5 PUBLIC REPOS</span><h2>Public code.<br/>Explicit claim boundaries.</h2><p>Five projects by Robert Dumanyan with public repositories and inspectable scope. These are mentor builds, not student work or client case studies.</p></div><RealProjectGallery locale="en"/></div></section>
    <section className="projectStudioSection" id="studio"><div className="shell"><div className="sectionHead projectStudioIntro"><span className="kicker">EXAMPLE OUTPUTS · NOT TESTIMONIALS / 9 EXAMPLES</span><h2>Filter by type of work.<br/>Inspect the anatomy of the result.</h2><p>Below are learning examples, not claims about specific clients or learners. All content remains available without JavaScript; the filter runs locally in the browser and sends nothing out.</p></div><ProjectStudio locale="en"/></div></section>
    <section className="section sectionMuted"><div className="shell projectStudioCta"><div className="sectionHead"><span className="kicker">Build yours</span><h2>An example is not a syllabus.<br/>The project follows a real goal.</h2><p>We choose the level, task and depth, then define the success criteria before starting.</p></div><div className="actions"><Link className="button buttonPrimary" href="/en/matcher">Find a route →</Link><Link className="button buttonGhost" href="/en/start">Describe the task →</Link></div></div></section>
  </main></WorkshopInteractive>;
}
