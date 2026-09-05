export const site = {
  name: "AI Skill Lab",
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://ai-skill-lab.vercel.app",
  telegram: process.env.NEXT_PUBLIC_TELEGRAM_URL || "https://t.me/BiTFormer",
  email: "robert@aiskillab.work",
  whatsapp: process.env.NEXT_PUBLIC_WHATSAPP_URL || "https://wa.me/66649701204",
  line: "https://line.me/ti/p/~iwf555",
  legalOperator: process.env.NEXT_PUBLIC_LEGAL_OPERATOR_NAME || "AI Skill Lab",
  legalEmail: process.env.NEXT_PUBLIC_LEGAL_CONTACT_EMAIL || "",
  legalJurisdiction: process.env.NEXT_PUBLIC_LEGAL_JURISDICTION || "",
  leadFormEnabled: process.env.NEXT_PUBLIC_LEAD_FORM_ENABLED === "true",
};

export function absoluteUrl(path = "/") {
  return new URL(path, site.url).toString();
}
