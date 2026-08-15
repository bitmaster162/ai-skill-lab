import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { ProjectStudio } from "@/components/ProjectStudio";

export const metadata: Metadata = {
  title: "Project Studio — example AI projects",
  description: "An interactive gallery of example AI projects showing the goal, AI role, human verification and final artifact. Examples, not client case studies.",
  alternates: { canonical: "/en/projects", languages: { ru: "/projects", en: "/en/projects" } },
};

export default function Page() {
  return <><Header locale="en" contactHref="/en/start" alternateHref="/projects"/><main id="main">
    <section className="projectStudioHero"><div className="shell"><div className="eyebrow"><span className="dot"/> EXAMPLE OUTPUTS · NOT TESTIMONIALS</div><h1>Not a work gallery.<br/><span>Project Studio.</span></h1><p className="heroLead">Nine example formats show not just what can be built, but what good AI work contains: goal → AI role → human check → verifiable artifact. These are not claims about specific clients or learners.</p><div className="actions"><a className="button buttonPrimary" href="#studio">Explore projects ↓</a><Link className="button buttonGhost" href="/en/proof">How we verify AI →</Link></div></div></section>
    <section className="projectStudioSection" id="studio"><div className="shell"><div className="sectionHead projectStudioIntro"><span className="kicker">PROJECT STUDIO / 9 EXAMPLES</span><h2>Filter by type of work.<br/>Inspect the anatomy of the result.</h2><p>All content remains available without JavaScript. The filter runs locally in the browser and sends nothing out.</p></div><ProjectStudio locale="en"/></div></section>
    <section className="section sectionMuted"><div className="shell projectStudioCta"><div className="sectionHead"><span className="kicker">Build yours</span><h2>An example is not a syllabus.<br/>The project follows a real goal.</h2><p>We choose the level, task and depth, then define the success criteria before starting.</p></div><div className="actions"><Link className="button buttonPrimary" href="/en/matcher">Find a route →</Link><Link className="button buttonGhost" href="/en/start">Describe the task →</Link></div></div></section>
  </main><Footer locale="en"/></>;
}
