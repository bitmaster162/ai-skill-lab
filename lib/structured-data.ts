import { site } from "@/lib/site";
import { commercialFacts, type WorkshopLocale } from "@/lib/commercial";

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
  email: site.email,
  telephone: "+66649701204",
  logo: `${site.url}/logo.png`,
  areaServed: [
    { "@type": "Place", name: "Phuket, Thailand" },
    { "@type": "Place", name: "Worldwide (online)" },
  ],
  founder: { "@id": `${site.url}/about#person` },
  sameAs: [site.telegram, site.whatsapp, site.line],
};
export const organizationSchemaRu = {
  ...baseOrganizationSchema,
  description: "Практическое персональное обучение AI для взрослых, бизнеса, детей и подростков — online worldwide и в Phuket по договорённости.",
};

export const organizationSchemaEn = {
  ...baseOrganizationSchema,
  description: "Practical one-to-one AI education for adults, business, kids and teens — online worldwide and in Phuket by arrangement.",
};

export const personSchema = {
  "@context": "https://schema.org",
  "@type": "Person",
  "@id": `${site.url}/about#person`,
  name: "Dumanyan Robert",
  jobTitle: "Founder / instructor",
  worksFor: { "@id": `${site.url}/#organization` },
  url: `${site.url}/about`,
  email: site.email,
  knowsAbout: [
    "AI systems", "Research workflows", "AI agents",
    "Automation", "Decision workflows", "Digital products",
  ],
  sameAs: [site.telegram],
};
export function courseListSchema(locale: WorkshopLocale) {
  const en = locale === "en";
  const plans = [
    ...commercialFacts.tracks.adult.map(plan => ({ plan, route: "personal" })),
    ...commercialFacts.tracks.kids.map(plan => ({ plan, route: "kids" })),
    ...commercialFacts.tracks.teens.map(plan => ({ plan, route: "teens" })),
  ];
  const pricingPath = en ? "/en/pricing" : "/pricing";
  return {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "@id": `${site.url}${pricingPath}#courses`,
    name: en ? "AI Skill Lab programs" : "Программы AI Skill Lab",
    itemListElement: plans.map(({ plan, route }, index) => ({
      "@type": "ListItem",
      position: index + 1,
      item: {
        "@type": "Course",
        name: plan.name,
        description: en ? plan.summary_en : plan.summary_ru,
        provider: { "@id": `${site.url}/#organization` },
        url: `${site.url}${en ? "/en" : ""}/${route}`,
        inLanguage: locale,
        offers: {
          "@type": "Offer",
          price: plan.price.replace(/[$,]/g, ""),          priceCurrency: commercialFacts.currency,
          category: "Paid",
          availability: "https://schema.org/InStock",
          url: `${site.url}${pricingPath}`,
        },
      },
    })),
  };
}

export function faqPageSchema(items: string[][], locale: WorkshopLocale) {
  const path = locale === "en" ? "/en/faq" : "/faq";
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "@id": `${site.url}${path}#faq`,
    mainEntity: items.map(([question, answer]) => ({
      "@type": "Question",
      name: question,
      acceptedAnswer: {
        "@type": "Answer",
        text: answer,
      },
    })),
  };
}
