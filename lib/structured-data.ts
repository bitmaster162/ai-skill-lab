import { site } from "@/lib/site";

export const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": `${site.url}/#website`,
  url: site.url,
  name: site.name,
  inLanguage: ["ru", "en"],
};

export const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "@id": `${site.url}/#organization`,
  name: site.name,
  url: site.url,
  description:
    "Практическое персональное обучение AI для взрослых, бизнеса, детей и подростков — online worldwide и в Phuket по договорённости.",
  sameAs: [site.telegram],
};
