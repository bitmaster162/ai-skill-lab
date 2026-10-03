import type { Metadata } from "next";
import { LegalPage } from "@/components/LegalPage";

export const metadata: Metadata = {
  title: { absolute: "Privacy policy and data handling | AI Skill Lab · Phuket" },
  description: "AI Skill Lab privacy policy: applications, AI routing, pseudonymous rate limiting, direct channels and data minimization.",
  alternates: { canonical: "/en/privacy", languages: { ru: "/privacy", en: "/en/privacy" } },
};

export default function PrivacyPageEn() {
  return <LegalPage locale="en" path="privacy" title="Privacy" intro="How AI Skill Lab handles application data, AI routing and technical data used to protect the service.">
    <h2>1. What the form collects</h2>
    <p>The form may transmit the name of the adult applicant or adult arranging the learning, contact details, selected audience, learning goal, page locale and application source path. The service also creates a technical request ID and timestamp.</p>

    <h2>2. Where the application goes</h2>
    <p>The browser submits to same-origin /api/lead. Vercel proxies that path to the isolated AI Skill Lab ingress; the ingress checks Origin and input, signs the request and forwards it to the operator-configured HTTPS webhook. After confirmed storage, the service may send the operator a technical Telegram notification containing only the request ID, application time, selected audience and page locale. The applicant name, contact, learning goal, program and source path are not included in that notification. The signing secret is not stored in the public site.</p>

    <h2>3. Operator and retention</h2>
    <p>Operator: Dumanyan Robert. Jurisdiction: Thailand. Privacy contact: robert@aiskillab.work. Configured lead retention is 30 days.</p>

    <h2>4. AI routing and OpenRouter</h2>
    <p>If AI routing is enabled, it runs only after the user presses the route button. /api/route receives the selected audience, three matcher answers and the goal text. Before any model call, the server checks the input for secret and credential patterns; detected secrets are blocked before the model is called. For AI routing, the server may send this data to the configured free model through the OpenRouter API. AI Skill Lab code does not write the goal text or matcher answers into its route-limit table.</p>

    <h2>5. AI-route abuse prevention</h2>
    <p>For exact rate limiting, the ingress receives the client network IP from the hosting platform and immediately converts it to an HMAC token. The raw IP is not written to AI Skill Lab&apos;s route-limit table. That table stores only a request ID, HMAC token and technical timestamp. Scheduled cleanup deletes rate-limit rows once they are older than 24 hours. The token is used only for rate limiting and AI-route protection, not for advertising profiling.</p>

    <h2>6. Direct channels</h2>
    <p>Telegram, email, WhatsApp and LINE remain alternative contact routes. After leaving this website, further data handling is governed by the external service and the information the user chooses to send.</p>

    <h2>7. Minors</h2>
    <p>We do not ask children to submit contact details independently. Youth applications and organizational communication use an adult contact only; parent/teen scenarios require adult confirmation in the form.</p>

    <h2>8. Technical data</h2>
    <p>Hosting and network providers may process standard technical logs required to deliver and protect the website. The current site code does not include advertising pixels or third-party behavioural analytics.</p>

    <h2>9. Data requests</h2>
    <p>Requests to correct or delete application information should be sent to the privacy contact above. Route-limit records are automatically removed by scheduled cleanup after they become older than 24 hours.</p>

    <div className="notice">Do not send identity documents, passwords, API keys, payment data or a child&apos;s direct contact. The public form has no checkout or advertising pixels.</div>
  </LegalPage>;
}
