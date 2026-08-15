import { site } from "@/lib/site";

export const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": `${site.url}/#website`,
  url: site.url,
  name: site.name,
  inLanguage: ["ru", "en"],
  publisher: { "@id": `${site.url}/#organization` },
};

const baseOrganizationSchema = {
  "@context": "https://schema.org",
  "@type": "EducationalOrganization",
  "@id": `${site.url}/#organization`,
  name: site.name,
  url: site.url,
  sameAs: [site.telegram],
};

export const organizationSchemaRu = {
  ...baseOrganizationSchema,
  description:
    "Практическое персональное обучение AI для взрослых, бизнеса, детей и подростков — online worldwide и в Phuket по договорённости.",
};

export const organizationSchemaEn = {
  ...baseOrganizationSchema,
  description:
    "Practical one-to-one AI education for adults, business, kids and teens — online worldwide and in Phuket by arrangement.",
};
