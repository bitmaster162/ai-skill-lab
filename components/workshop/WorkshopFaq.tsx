import Link from "next/link";
import { WorkshopShell, type WorkshopLocale } from "./WorkshopShell";
import styles from "./WorkshopShell.module.css";
export function WorkshopFaq({locale="ru",items}:{locale?:WorkshopLocale;items:string[][]}) {
 const en=locale==="en",start=en?"/en/start":"/start";
 return <WorkshopShell locale={locale} alternateHref={en?"/faq":"/en/faq"}><main id="main" data-workshop-faq>
 <section className={styles.audienceHero}><div><span className={styles.audienceEyebrow}>FAQ · BEFORE YOU START</span><h1>{en?"Eleven answers":"Одиннадцать ответов"}<br/><em>{en?"before the call.":"до разговора."}</em></h1><p>{en?"The format, boundaries and terms before choosing a package.":"Формат, границы и условия до выбора пакета."}</p><Link className="workshopButton workshopButtonPrimary" href={start}>{en?"Discuss the goal →":"Обсудить задачу →"}</Link></div></section>
 <section className={`${styles.section} ${styles.paper}`}><div className={styles.faqList}>{items.map(([q,a])=><details key={q}><summary>{q}</summary><p>{a}</p></details>)}</div></section>
 </main></WorkshopShell>;
}
