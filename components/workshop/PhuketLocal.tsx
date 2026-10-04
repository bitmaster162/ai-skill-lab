import type { WorkshopLocale } from "./WorkshopShell";
import styles from "./WorkshopShell.module.css";

type Area = {
  name: string;
  note: string;
};

const areas: Record<WorkshopLocale, Area[]> = {
  ru: [
    { name: "Rawai / Nai Harn", note: "Юг Phuket. Локальная встреча — только после подтверждения места и времени." },
    { name: "Chalong", note: "Южно-центральная часть острова. Подходит как ориентир для согласования очной сессии." },
    { name: "Kata / Karon", note: "Западное побережье. Доступность конкретного места подтверждаем до бронирования." },
    { name: "Phuket Town", note: "Центральная городская зона. Точка встречи определяется отдельно под конкретную сессию." },
  ],
  en: [
    { name: "Rawai / Nai Harn", note: "South Phuket. An in-person session is confirmed only after venue and timing are agreed." },
    { name: "Chalong", note: "South-central Phuket. Used as a local coordination area for an agreed in-person session." },
    { name: "Kata / Karon", note: "West coast. Availability of a specific venue is confirmed before booking." },
    { name: "Phuket Town", note: "Central urban area. The meeting point is agreed separately for each session." },
  ],
};

const formats: Record<WorkshopLocale, Array<[string,string,string]>> = {
  ru: [
    ["LOCAL 1:1", "Очная персональная сессия", "Место и время согласуем заранее. AI Skill Lab не заявляет постоянный учебный центр или публичный classroom address."],
    ["ONLINE 1:1", "Персональная работа online", "Экран, совместная сборка проектов и персональный маршрут работают независимо от страны."],
    ["HYBRID", "Часть очно, часть online", "Если программе нужен смешанный режим, очные и online-сессии можно сочетать после согласования маршрута."],
  ],
  en: [
    ["LOCAL 1:1", "In-person one-to-one", "Venue and timing are agreed in advance. AI Skill Lab does not claim a permanent school location or public classroom address."],
    ["ONLINE 1:1", "One-to-one online", "Screen sharing, project building and a personal route work regardless of country."],
    ["HYBRID", "Local plus online", "If a program benefits from both, in-person and online sessions can be combined after the route is agreed."],
  ],
};

export function PhuketLocal({ locale = "ru" }: { locale?: WorkshopLocale }) {
  const en = locale === "en";
  return <>
    <section className={styles.phuketLocal} data-a4-phuket-local="true">
      <div className={styles.phuketLocalHead}>
        <span>{en ? "PHUKET · LOCAL COORDINATION" : "PHUKET · ЛОКАЛЬНАЯ КООРДИНАЦИЯ"}</span>
        <h2>{en ? "Real areas, no invented campus." : "Реальные районы, без выдуманного кампуса."}</h2>
        <p>{en
          ? "For local planning we use recognizable Phuket areas. They are coordination areas, not branches or permanent classrooms. The exact venue, availability and travel time are confirmed before booking."
          : "Для локального планирования используем понятные районы Phuket. Это зоны координации, а не филиалы и не постоянные классы. Точное место, доступность и время в пути подтверждаем до бронирования."}</p>
      </div>
      <div className={styles.phuketAreaGrid}>
        {areas[locale].map((area) => <article key={area.name}>
          <strong>{area.name}</strong>
          <p>{area.note}</p>
        </article>)}
      </div>
    </section>
    <section className={styles.phuketFormats}>
      <div className={styles.phuketLocalHead}>
        <span>{en ? "FORMAT" : "ФОРМАТ"}</span>
        <h2>{en ? "Choose geography after the learning route." : "Сначала маршрут обучения, потом география."}</h2>
      </div>
      <div className={styles.phuketFormatGrid}>
        {formats[locale].map(([tag,title,body]) => <article key={tag}>
          <span>{tag}</span>
          <strong className={styles.phuketFormatTitle}>{title}</strong>
          <p>{body}</p>
        </article>)}
      </div>
      <p className={styles.phuketLocalNote}>{en
        ? "For minors, contact, scheduling and service approval remain with a parent or legal guardian."
        : "Для несовершеннолетних контакт, расписание и согласование сервисов остаются за родителем или законным представителем."}</p>
    </section>
  </>;
}
