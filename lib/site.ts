export const site = {
  name: "AI Skill Lab",
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://example.com",
  telegram: process.env.NEXT_PUBLIC_TELEGRAM_URL || "https://t.me/BiTFormer",
  whatsapp: process.env.NEXT_PUBLIC_WHATSAPP_URL || "",
  legalOperator: process.env.NEXT_PUBLIC_LEGAL_OPERATOR_NAME || "AI Skill Lab",
  legalEmail: process.env.NEXT_PUBLIC_LEGAL_CONTACT_EMAIL || "",
  legalJurisdiction: process.env.NEXT_PUBLIC_LEGAL_JURISDICTION || "",
};

export function absoluteUrl(path = "/") {
  return new URL(path, site.url).toString();
}
