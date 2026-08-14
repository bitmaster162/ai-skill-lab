import type { Metadata } from "next";
import Link from "next/link";
import { LegalPage } from "@/components/LegalPage";
import { site } from "@/lib/site";

export const metadata: Metadata = { title: "Privacy", description: "How AI Skill Lab handles application data and protects minors' privacy." };

export default function PrivacyPageEn() {
  return <LegalPage locale="en" path="privacy" title="Privacy" intro="How the site handles data in the current launch mode and what changes if the built-in application form is enabled.">
    <h2>1. Data controller / operator</h2>
    <p>Education service operator: <strong>{site.legalOperator}</strong>. {site.legalJurisdiction ? <>Jurisdiction/place of operation: {site.legalJurisdiction}. </> : null}{site.legalEmail ? <>Privacy contact: <a href={`mailto:${site.legalEmail}`}>{site.legalEmail}</a>.</> : <>A dedicated privacy email must be configured before the built-in application form is enabled.</>}</p>

    <h2>2. Current site mode</h2>
    <p>{site.leadFormEnabled ? <>The built-in application form is enabled. It may transmit the adult&apos;s name, contact method, selected audience/program, learning goal, page locale, application source and a technical timestamp.</> : <>The built-in application form is currently disabled. The site does not ask for a name, phone number, email address or a child&apos;s contact details; the primary contact action opens external Telegram.</>}</p>

    <h2>3. If the form is enabled</h2>
    <p>Form information is used only to answer the inquiry, recommend a program, organize an introductory conversation and communicate about the selected training. The form is not designed for advertising profiling.</p>

    <h2>4. Kids and teens</h2>
    <p>For learners under 18, the form contact must belong to a parent, guardian or another adult organizing the training. We do not ask a child to submit a personal phone number, email, Telegram or WhatsApp account. Learning activities follow a data-minimization approach.</p>

    <h2>5. Lead delivery</h2>
    <p>{site.leadFormEnabled ? <>The site sends an application only to the HTTPS webhook configured by the operator. The final destination — for example a CRM, n8n, Make or another system — must use appropriate access controls and retention practices.</> : <>In the current contact-only mode, the website does not transmit an application itself: opening Telegram hands the conversation to an external service operating under its own terms.</>}</p>

    <h2>6. Third-party AI services</h2>
    <p>Training may use third-party AI products. Each provider has its own terms, age requirements and data practices. The current rule for the specific service is checked before it is used with a minor. See <Link href="/en/safety">Youth AI safety</Link>.</p>

    <h2>7. Technical data</h2>
    <p>Hosting and network providers may process standard technical logs required to deliver and protect the website. The current site code does not include advertising pixels or third-party behavioural analytics.</p>

    <h2>8. Data requests</h2>
    <p>{site.leadFormEnabled ? <>Requests to correct or delete application information should be sent to the operator&apos;s privacy contact.</> : <>In contact-only mode, conversation data is handled by external Telegram; before the built-in form is enabled, the operator must configure its legal name, privacy email and lead-retention rules.</>}</p>
  </LegalPage>;
}
