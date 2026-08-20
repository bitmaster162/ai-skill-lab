import type { Metadata } from "next";
import Link from "next/link";
import { LegalPage } from "@/components/LegalPage";

export const metadata: Metadata = { title: "Learning terms", description: "Baseline terms for AI Skill Lab education programs." };

export default function TermsPageEn() {
  return <LegalPage locale="en" path="terms" title="Learning terms" intro="Baseline rules for using the site and arranging one-to-one AI training. Final commercial terms are confirmed before payment.">
    <h2>1. Service</h2><p>AI Skill Lab provides practical AI education through one-to-one sessions, project-based programs and team training. The site is not an official product of OpenAI, Google, Anthropic or other AI providers.</p>
    <h2>2. Program and outcomes</h2><p>Content adapts to the learner&apos;s level and goal. Project descriptions are examples of deliverable formats, not guarantees of a particular academic, professional or financial outcome.</p>
    <h2>3. Pricing and payment</h2><p>Website prices are indicative for the stated format. Final scope, currency, payment method, schedule, rescheduling and refund terms are confirmed with the adult customer before payment. Written individual terms take priority if they differ from the website.</p>
    <h2>4. Minors</h2><p>An adult arranges training for anyone under 18. Third-party AI tools are used according to their current age rules. For children under 13 we do not base the program on an independent ChatGPT account; if ChatGPT is used in an education context, the actual interaction is conducted by an adult. See <Link href="/en/safety">Youth AI safety</Link>.</p>
    <h2>5. Responsible AI use</h2><p>Learners must follow applicable law, service rules, school/university requirements and third-party rights. Training emphasizes fact-checking, transparent AI contribution and avoiding unnecessary personal or confidential data.</p>
    <h2>6. Third-party services</h2><p>AI platforms, messaging, video calls and other external products operate under their own terms and may change features or availability. AI Skill Lab does not control those changes.</p>
    <h2>7. Privacy</h2><p>Application data practices are described in the <Link href="/en/privacy">Privacy page</Link>.</p>
  </LegalPage>;
}
