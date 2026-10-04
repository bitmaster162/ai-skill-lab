import Link from "next/link";
import { JsonLd } from "@/components/JsonLd";
import { WorkshopShell, type WorkshopLocale } from "@/components/workshop/WorkshopShell";
import { formatGuideDate, renderGuideMarkdown, type Guide } from "@/lib/guides";
import styles from "./GuidePages.module.css";

const ORIGIN = "https://aiskillab.work";
const ORG_ID = `${ORIGIN}/#organization`;

function guideSchema(guide: Guide) {
  const { meta } = guide;
  return {
    article: {
      "@context": "https://schema.org",
      "@type": "Article",
      "@id": `${ORIGIN}${meta.path}#article`,
      headline: meta.title,
      description: meta.description,
      url: `${ORIGIN}${meta.path}`,
      mainEntityOfPage: `${ORIGIN}${meta.path}`,
      image: `${ORIGIN}/og.png`,
      inLanguage: meta.lang,
      dateModified: meta.reviewed,
      publisher: { "@id": ORG_ID },
    },
    breadcrumbs: {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "@id": `${ORIGIN}${meta.path}#breadcrumbs`,
      itemListElement: [
        { "@type": "ListItem", position: 1, name: meta.lang === "en" ? "Home" : "Главная", item: `${ORIGIN}${meta.lang === "en" ? "/en" : "/"}` },
        { "@type": "ListItem", position: 2, name: meta.lang === "en" ? "Guides" : "Гайды", item: `${ORIGIN}${meta.lang === "en" ? "/en/guides" : "/guides"}` },
        { "@type": "ListItem", position: 3, name: meta.title, item: `${ORIGIN}${meta.path}` },
      ],
    },
  };
}

export function GuideListing({ locale, guides }: { locale: WorkshopLocale; guides: Guide[] }) {
  const en = locale === "en";
  return <WorkshopShell locale={locale} alternateHref={en ? "/guides" : "/en/guides"}>
    <main id="main" className={styles.listingMain}>
      <section className={styles.listingHero}>
        <span>{en ? "GUIDES · CHECKED SOURCES" : "ГАЙДЫ · ПРОВЕРЕННЫЕ ИСТОЧНИКИ"}</span>
        <h1>{en ? "Guides" : "Гайды"}</h1>
        <p>{en
          ? "Short, checked guides for parents, adult learners and teams. Each one shows when it was checked and its sources."
          : "Короткие проверенные материалы для родителей, взрослых учеников и команд. У каждого — дата проверки и источники."}</p>
      </section>
      <section className={styles.cardGrid} aria-label={en ? "Published guides" : "Опубликованные гайды"}>
        {guides.map((guide) => <article className={styles.card} key={guide.meta.path}>
          <span>{en ? `Checked ${formatGuideDate(guide.meta.reviewed, "en")}` : `Проверено ${formatGuideDate(guide.meta.reviewed, "ru")}`}</span>
          <h2><Link href={guide.meta.path}>{guide.meta.title}</Link></h2>
          <p>{guide.meta.description}</p>
          <Link className={styles.cardLink} href={guide.meta.path}>{en ? "Open guide →" : "Открыть гайд →"}</Link>
        </article>)}
      </section>
    </main>
  </WorkshopShell>;
}

export function GuideArticle({ guide }: { guide: Guide }) {
  const en = guide.meta.lang === "en";
  const doc = renderGuideMarkdown(guide.markdown);
  if (doc.h1 !== guide.meta.title) throw new Error(`guide H1/title mismatch: ${guide.meta.path}`);
  const schema = guideSchema(guide);
  return <>
    <JsonLd data={schema.article} />
    <JsonLd data={schema.breadcrumbs} />
    <WorkshopShell locale={guide.meta.lang} alternateHref={guide.meta.alternate}>
      <main id="main" className={styles.articleMain}>
        <article className={styles.article}>
          <nav className={styles.breadcrumbs} aria-label={en ? "Breadcrumbs" : "Хлебные крошки"}>
            <Link href={en ? "/en" : "/"}>{en ? "Home" : "Главная"}</Link><span> / </span>
            <Link href={en ? "/en/guides" : "/guides"}>{en ? "Guides" : "Гайды"}</Link>
          </nav>
          <header className={styles.articleHeader}>
            <span>{en ? "GUIDE · AI SKILL LAB" : "ГАЙД · AI SKILL LAB"}</span>
            <h1>{doc.h1}</h1>
            <p className={styles.lead} dangerouslySetInnerHTML={{ __html: doc.leadHtml }} />
            <p className={styles.reviewMeta}>
              {en
                ? `Checked ${formatGuideDate(guide.meta.reviewed, "en")} · next review ${formatGuideDate(guide.meta.next_review, "en")}`
                : `Проверено ${formatGuideDate(guide.meta.reviewed, "ru")} · следующий пересмотр ${formatGuideDate(guide.meta.next_review, "ru")}`}
            </p>
          </header>
          <nav className={styles.toc} aria-label={en ? "Table of contents" : "Оглавление"}>
            <strong>{en ? "Contents" : "Оглавление"}</strong>
            <ol>{doc.toc.map((item) => <li key={item.id}><a href={`#${item.id}`}>{item.label}</a></li>)}</ol>
          </nav>
          <div className={styles.body} dangerouslySetInnerHTML={{ __html: doc.bodyHtml }} />
        </article>
      </main>
    </WorkshopShell>
  </>;
}
