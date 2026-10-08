import Image from "next/image";
import { mentorProfile } from "@/lib/mentor";
import type { WorkshopLocale } from "./WorkshopShell";
import styles from "./WorkshopShell.module.css";

export function MentorCard({ locale = "ru" }: { locale?: WorkshopLocale }) {
  const en = locale === "en";
  return (
    <section className={styles.mentorSection} data-a5-mentor="true">
      <div className={styles.mentorCard}>
        <div className={styles.mentorPhoto}>
          <Image
            src={mentorProfile.image}
            alt={en ? "Robert Dumanyan — founder and instructor at AI Skill Lab" : "Роберт Думанян — основатель и преподаватель AI Skill Lab"}
            width={mentorProfile.imageWidth}
            height={mentorProfile.imageHeight}
            priority={false}
          />
        </div>
        <div className={styles.mentorCopy}>
          <span className={styles.mentorEyebrow}>{en ? "MENTOR · HUMAN IN THE LOOP" : "НАСТАВНИК · ПРОВЕРКА ЧЕЛОВЕКОМ"}</span>
          <h2>{mentorProfile.name[locale]}</h2>
          <strong>{mentorProfile.role[locale]}</strong>
          <p>{mentorProfile.summary[locale]}</p>
          <div className={styles.mentorFocus} aria-label={en ? "Areas of practice" : "Направления практики"}>
            {mentorProfile.focus.map((item) => <span key={item}>{item}</span>)}
          </div>
          <div className={styles.mentorLinks}>
            <a href={mentorProfile.github} target="_blank" rel="noopener noreferrer">GitHub ↗</a>
            <a href={mentorProfile.linkedin} target="_blank" rel="noopener noreferrer">LinkedIn ↗</a>
          </div>
        </div>
      </div>
    </section>
  );
}
