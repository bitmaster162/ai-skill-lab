import { site } from "@/lib/site";
import styles from "./WorkshopShell.module.css";

export function ChannelLinks({ locale = "ru" }: { locale?: "ru" | "en" }) {
  const en = locale === "en";
  const channels = [
    ["Telegram", site.telegram, en ? "Brief with prefill" : "Brief с автозаполнением"],
    [en ? "Email" : "Почта", `mailto:${site.email}`, site.email],
    ["WhatsApp", site.whatsapp, "+66 64 970 1204"],
    ["LINE", site.line, "iwf555"],
  ];
  return (
    <div className={styles.channelGrid} id="contact-channels">
      {channels.map(([label, href, note]) => (
        <a className={styles.channel} href={href} key={label} target={href.startsWith("http") ? "_blank" : undefined} rel={href.startsWith("http") ? "noopener noreferrer" : undefined}>
          <span>{label}</span><strong>{note}</strong><b aria-hidden="true">↗</b>
        </a>
      ))}
    </div>
  );
}
