import type { Metadata } from "next";
import Link from "next/link";
import { LegalPage } from "@/components/LegalPage";

export const metadata: Metadata = { title: "Youth AI safety", description: "Age rules, privacy, verification and adult involvement for AI Skill Lab learners ages 8–18." };

export default function SafetyPageEn() {
  return <LegalPage locale="en" path="safety" title="Youth AI safety" intro="Rules for ages 8–18: an adult stays in the loop, personal data is minimized and model outputs are verified.">
    <div className="policyCallout"><strong>Core rule</strong><p>The program does not require an independent ChatGPT account for a child under 13. If ChatGPT is used as a demonstration tool in an education context, the actual interaction with the service is conducted by an adult.</p></div>
    <h2>1. Why</h2><p>OpenAI's current guidance says ChatGPT is not meant for children under 13; users ages 13–17 need permission from a parent or legal guardian. For education use with a child under 13, OpenAI says the actual interaction with ChatGPT must be conducted by an adult.</p>
    <p data-policy-verified="2026-08-15"><a className="inlineExternal" href="https://help.openai.com/en/articles/8313401" target="_blank" rel="noreferrer">Official OpenAI guidance ↗</a> · verified August 15, 2026</p>
    <h2>2. We do not depend on one provider</h2><p>The course teaches transferable skills: defining a task, giving context, comparing sources, checking output and understanding model limits. If a tool is not age-appropriate, it is replaced with an adult-led demonstration or another suitable approach.</p>
    <h2>3. Adult contact only</h2><p>Applications, scheduling, payment and organizational communication go through an adult. A child's phone number, email or messenger account is not needed for the website form.</p>
    <h2>4. Privacy in assignments</h2><p>We avoid home addresses, identity documents, passwords, private conversations, medical information and other unnecessary personal data. Photos, files and school materials are used only when genuinely needed.</p>
    <h2>5. Verification</h2><p>AI can be wrong while sounding confident. Learners practice separating claims from assumptions, finding sources, comparing evidence and correcting the output.</p>
    <h2>6. Authorship and school rules</h2><p>AI is an assistant, not a hidden substitute for the learner's work. The learner should be able to explain their contribution and follow the rules of their school or teacher.</p>
    <h2>7. Parent controls</h2><p>A parent can identify tools, content types or topics that are off-limits. For younger learners, the final project and home practice are framed so the adult can understand how AI is being used.</p>
    <h2>8. ChatGPT parental controls for teens</h2><p>For linked teen accounts, OpenAI offers parental controls that can manage selected settings, quiet hours and limited safety notifications. These controls do not give a parent access to the teen's conversations and are not real-time conversation monitoring.</p><p><a className="inlineExternal" href="https://help.openai.com/en/articles/12315553-parental-controls-on-chatgpt-faq/" target="_blank" rel="noreferrer">Parental controls in ChatGPT ↗</a></p>
    <p className="legalCrosslink">See also: <Link href="/en/privacy">Privacy</Link> · <Link href="/en/terms">Learning terms</Link>.</p>
  </LegalPage>;
}
