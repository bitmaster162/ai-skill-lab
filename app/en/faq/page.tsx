import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "FAQ",
  description: "Answers about AI Skill Lab: one-to-one format, online / Phuket, pricing, projects, youth programs and contact-only start.",
  alternates: { canonical: "/en/faq", languages: { ru: "/faq", en: "/en/faq" } },
};

const items = [
  ["Is this a recorded course?", "No. The core format is one-to-one and built around a concrete goal and a finished artifact."],
  ["Can the program be fully online?", "Yes. Online is the geography-independent core format. In-person sessions in Phuket are possible by prior arrangement."],
  ["How do I choose a package?", "Start with a short brief: learner, goal, current level, language and format. Depth is selected after that, not before."],
  ["Can I pay directly on the website?", "No. The public site runs in contact-only mode: no checkout and no first-party lead form."],
  ["What is the learning outcome?", "A finished project, workflow, research output, prototype or another artifact that the learner can explain and verify."],
  ["How do youth programs work?", "For minors, program coordination goes through an adult. The age rules of each AI service are checked before use."],
  ["Does AI do the learner's homework?", "No. The method emphasizes task definition, verification, iteration and the learner's ability to explain personal contribution."],
  ["Can the program focus on a business problem?", "Yes. Adult and team routes can focus on research, automation, an AI assistant, workflows or an internal mini-product."],
  ["What happens after I message on Telegram?", "First we confirm the goal and format. Then we recommend a suitable package or a smaller starting point, confirm scope, schedule, payment and rescheduling terms in writing, and only then does the program start."],
  ["When do I pay, and on what terms?", "Payment is accepted only after the specific service is agreed. Final scope and price, payment method and provider details, plus rescheduling, cancellation and refund terms must be documented before payment."],
  ["How long is one session?", "The package fixes the number of sessions, not a hidden standard duration. The exact duration of each session and the schedule are agreed and documented before payment as part of the specific scope."],
];

export default function FaqPage() {
  return <><Header locale="en" contactHref="/en/start" alternateHref="/faq"/><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> FAQ · BEFORE YOU START</div><h1>Questions first.<br/><span>Package second.</span></h1><p className="heroLead">Short answers to the things worth understanding before the first conversation.</p><div className="heroActions"><Link className="button buttonPrimary" href="/en/start">Discuss the goal →</Link><Link className="textLink" href="/en/pricing">Pricing →</Link></div></div></section><section className="section"><div className="shell"><div className="faqGrid"><div className="sectionHead stickyHead"><span className="kicker">FAQ</span><h2>11 short answers</h2></div><div className="faqList">{items.map(([q,a])=><details key={q}><summary>{q}<span>+</span></summary><p>{a}</p></details>)}</div></div></div></section></main><Footer locale="en"/></>;
}
