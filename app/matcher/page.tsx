import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { ProgramMatcher } from "@/components/ProgramMatcher";

export const metadata: Metadata = {
  title: "Подобрать AI-программу",
  description: "Локальный program matcher: взрослый, ребёнок, подросток или business pilot. Ничего не отправляется и не сохраняется.",
  alternates: { canonical: "/matcher", languages: { ru: "/matcher", en: "/en/matcher" } },
};

export default function Page(){return <><Header alternateHref="/en/matcher"/><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> PROGRAM MATCHER · LOCAL ONLY</div><h1>Подобрать маршрут<br/><span>без анкеты.</span></h1><p className="heroLead">Три выбора дают стартовую рекомендацию по формату и пакету. Никакие ответы не отправляются на сервер и не сохраняются.</p></div></section><section className="section"><div className="shell"><ProgramMatcher/></div></section></main><Footer/></>}
