import { site } from "@/lib/site";
import { commercialFacts, type WorkshopLocale } from "@/lib/commercial";
import { mentorProfile } from "@/lib/mentor";

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
  name: mentorProfile.name.en,
  jobTitle: mentorProfile.role.en,
  worksFor: { "@id": `${site.url}/#organization` },
  url: `${site.url}/about`,
  email: site.email,
  image: `${site.url}${mentorProfile.image}`,
  knowsAbout: [
    "AI systems", "Research workflows", "AI agents",
    "Automation", "Decision workflows", "Digital products",
  ],
  sameAs: [site.telegram, mentorProfile.github, mentorProfile.linkedin],
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

export type CoursePageRoute = "kids" | "teens" | "personal" | "business";
const coursePageFacts = {
  ru: {
    kids: { name: "AI для детей 8–13", description: "Занятия по ИИ и нейросетям для детей 8–13 лет: свой творческий проект вместе со взрослым, правила приватности и безопасная практика. Пхукет и онлайн." },
    teens: { name: "AI для подростков 14–18", description: "Подростки 14–18 лет работают с ИИ и нейросетями: исследования, код, портфолио и свои проекты с проверкой результата. Пхукет и онлайн." },
    personal: { name: "Персональное обучение AI", description: "Занятия по ИИ и нейросетям 1-на-1 вокруг вашей реальной задачи: практика, свой проект и разбор инструментов. На Пхукете или онлайн." },
    business: { name: "AI для бизнеса", description: "Обучение команды работе с ИИ, разбор процессов и один пилот — от выбора задачи до проверяемого результата, без лишних обещаний. Пхукет и онлайн." },
  },
  en: {
    kids: { name: "AI for kids 8–13", description: "AI for kids 8–13: creativity and a learner-owned project with adult coordination, privacy rules, verification and safe practice." },
    teens: { name: "AI for teens 14–18", description: "AI for teens 14–18: research, code, portfolio and learner-owned projects with verification, authorship rules and adult coordination." },
    personal: { name: "Personal AI learning", description: "One-to-one AI learning around a real task: hands-on practice, a verifiable project, tool review and work online or in Phuket." },
    business: { name: "AI for business", description: "Business AI: process audit, team training, bounded pilots, QA and handoff from task selection to a verifiable result without inflated promises." },
  },
} as const;

export function coursePageSchema(route: CoursePageRoute, locale: WorkshopLocale) {
  const item = coursePageFacts[locale][route];
  const prefix = locale === "en" ? "/en" : "";
  return {
    "@context": "https://schema.org",
    "@type": "Course",
    "@id": `${site.url}${prefix}/${route}#course`,
    name: item.name,
    description: item.description,
    provider: { "@id": `${site.url}/#organization` },
    url: `${site.url}${prefix}/${route}`,
    inLanguage: locale,
    hasCourseInstance: {
      "@type": "CourseInstance",
      courseMode: "online",
      courseWorkload: "PT60M",
    },
  };
}
