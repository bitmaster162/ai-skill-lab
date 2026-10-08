"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import { IntroCallCta } from "@/components/IntroCallCta";
import { commercialFacts, type WorkshopLocale } from "@/lib/commercial";
import { diagnosticCtaSummary, introCall } from "@/lib/e1_4";

export type MatcherLocale = "ru" | "en";
type Audience = "adult" | "kids" | "teens" | "business";
type Goal = "research" | "create" | "automate" | "team";
type Depth = "intro" | "core" | "deep";
type RouteState = "idle" | "loading" | "ready" | "error" | "secret";
type LeadState = "idle" | "sending" | "sent" | "error";

type RoutePackage = { id: string; name: string; price: string; sessions: string };
type RouteResult = { status: "ok" | "fallback"; package: RoutePackage; steps: [string,string,string]; brief: string; requestId?: string };

const copy = {
  ru: {
    privacy: "ИИ-подбор запускается только по кнопке · ввод подбор программы не хранит",
    audience: "1. Для кого маршрут?",
    goal: "2. Что важнее всего?",
    depth: "3. Насколько глубоко хотите зайти?",
    goalText: "4. Коротко опишите цель",
    goalPlaceholder: "Например: хочу собрать ИИ-агента для исследование и научиться проверять его выводы.",
    audienceOptions: [["adult","Взрослый"],["kids","Ребёнок 8–13"],["teens","Подросток 14–18"],["business","Команда / бизнес"]],
    goalOptions: [["research","Исследования и решения"],["create","Контент и проекты"],["automate","Автоматизация / агенты"],["team","Рабочий процесс команды"]],
    depthOptions: [["intro","Понять и попробовать"],["core","Собрать рабочую систему"],["deep","Сделать сильный финальный проект"]],
    run: "Подобрать маршрут с ИИ",
    running: "Подбираем…",
    resultLabel: "Стартовая рекомендация",
    noResult: "Выберите три варианта и опишите цель. До нажатия кнопки ничего не отправляется.",
    why: "Следующие шаги",
    note: "Результат автоматический: это не обещание результата и не подтверждение соответствие. Объём работ и условия сверяются человеком.",
    unavailable: "ИИ-маршрут сейчас недоступен. Показана локальная рекомендация по той же таблице пакетов.",
    secret: "Похоже, в цели есть секрет или ключ. Удалите его: такие данные не передаются модели.",
    copy: "Скопировать короткое описание задачи", copied: "Скопировано", copyError: "Не удалось скопировать", reset: "Сбросить",
    leadTitle: "Отправить этот короткое описание задачи",
    leadName: "Имя", leadContact: "Как связаться", leadConsent: "Согласен(на) на обработку этой заявки по правилам конфиденциальности.",
    adult: "Я совершеннолетний взрослый, организующий обучение; контакт принадлежит взрослому.",
    send: "Отправить короткое описание задачи", sending: "Отправляем…", sent: "Короткое описание задачи отправлен. Ответим в течение 1–2 рабочих дней.", sendError: "Не удалось отправить короткое описание задачи. Можно использовать прямой канал связи.",
  },
  en: {
    privacy: "AI routing runs only after you press the button · matcher input is not stored",
    audience: "1. Who is the route for?",
    goal: "2. What matters most?",
    depth: "3. How deep do you want to go?",
    goalText: "4. Describe the goal briefly",
    goalPlaceholder: "For example: build a research AI agent and learn how to verify its conclusions.",
    audienceOptions: [["adult","Adult"],["kids","Child 8–13"],["teens","Teen 14–18"],["business","Team / business"]],
    goalOptions: [["research","Research and decisions"],["create","Content and projects"],["automate","Automation / agents"],["team","Team workflow"]],
    depthOptions: [["intro","Understand and try"],["core","Build a working system"],["deep","Ship a strong final project"]],
    run: "Find a route with AI",
    running: "Finding a route…",
    resultLabel: "Starting recommendation",
    noResult: "Choose three options and describe the goal. Nothing is sent until you press the button.",
    why: "Next steps",
    note: "The result is automatic: it is not a promised outcome or an automatic fit approval. Scope and terms are confirmed by a human.",
    unavailable: "AI routing is unavailable right now. A local recommendation from the same package table is shown.",
    secret: "The goal appears to contain a secret or credential. Remove it; those values are not sent to the model.",
    copy: "Copy brief", copied: "Copied", copyError: "Copy failed", reset: "Reset",
    leadTitle: "Send this brief",
    leadName: "Name", leadContact: "How should we contact you?", leadConsent: "I agree to the processing of this application as described in the Privacy notice.",
    adult: "I am an adult organizing the learner's training and the contact belongs to an adult.",
    send: "Send brief", sending: "Sending…", sent: "Brief sent. We reply within 1–2 business days.", sendError: "Brief could not be sent. You can use a direct contact channel instead.",
  },
} as const;

function localPackage(audience: Audience, goal: Goal, depth: Depth, locale: WorkshopLocale): RoutePackage {
  const en=locale==="en";
  if (audience==="business") {
    const b=commercialFacts.business;
    if (goal==="automate" || depth==="deep") return {id:"business:implementation_pilot",name:en?b.implementation_pilot.name_en:b.implementation_pilot.name_ru,price:en?`from ${b.implementation_pilot.price_from}`:`от ${b.implementation_pilot.price_from}`,sessions:en?`scope cap ${b.implementation_pilot.scope_cap_hours} hours`:`потолок scope ${b.implementation_pilot.scope_cap_hours} часов`};
    if (goal==="team") return {id:"business:team_training",name:en?b.team_training.name_en:b.team_training.name_ru,price:en?`from ${b.team_training.price_from_per_session}/session`:`от ${b.team_training.price_from_per_session}/сессия`,sessions:en?`minimum ${b.team_training.min_sessions} sessions`:`минимум ${b.team_training.min_sessions} занятия`};
    return {id:"business:workflow_audit",name:en?b.workflow_audit.name_en:b.workflow_audit.name_ru,price:b.workflow_audit.price,sessions:en?"fixed scope":"фиксированный объём работ"};
  }
  const index=depth==="deep"?2:depth==="core"?1:0;
  const plan=commercialFacts.tracks[audience][index];
  return {id:`${audience}:${plan.id}`,name:plan.name,price:plan.price,sessions:en?plan.sessions_en:plan.sessions_ru};
}

function localRoute(audience: Audience, goal: Goal, depth: Depth, text: string, locale: WorkshopLocale): RouteResult {
  const pkg=localPackage(audience,goal,depth,locale);
  const en=locale==="en";
  return {
    status:"fallback",
    package:pkg,
    steps:[
      introCall.label[locale],
      diagnosticCtaSummary(locale),
      en?`Start ${pkg.name} with one bounded project and a review checkpoint.`:`Начать ${pkg.name} с одного ограниченного проекта и контрольной точки проверки.`,
    ],
    brief:(en?`Route request: ${pkg.name}. Goal: ${text || "route selection"}`:`Запрос на маршрут: ${pkg.name}. Цель: ${text || "подбор маршрута"}`).slice(0,600),
  };
}

export function ProgramMatcher({ locale="ru" }: { locale?: MatcherLocale }) {
  const t=copy[locale];
  const en=locale==="en";
  const base=en?"/en":"";
  const [audience,setAudience]=useState<Audience|null>(null);
  const [goal,setGoal]=useState<Goal|null>(null);
  const [depth,setDepth]=useState<Depth|null>(null);
  const [goalText,setGoalText]=useState("");
  const [route,setRoute]=useState<RouteResult|null>(null);
  const [routeState,setRouteState]=useState<RouteState>("idle");
  const [copyState,setCopyState]=useState<"idle"|"done"|"error">("idle");
  const [name,setName]=useState("");
  const [contact,setContact]=useState("");
  const [privacy,setPrivacy]=useState(false);
  const [adultConfirmed,setAdultConfirmed]=useState(false);
  const [leadState,setLeadState]=useState<LeadState>("idle");
  const youth=audience==="kids" || audience==="teens";

  const local=useMemo(()=>audience&&goal&&depth?localRoute(audience,goal,depth,goalText,locale):null,[audience,goal,depth,goalText,locale]);
  const display=route || local;

  async function runRoute() {
    if(!audience||!goal||!depth||!goalText.trim()) return;
    setRouteState("loading"); setRoute(null); setLeadState("idle"); setCopyState("idle");
    try {
      const response=await fetch("/api/route",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({audience,answers:[audience,goal,depth],goal:goalText,locale,adultConfirmed})});
      const body=await response.json().catch(()=>null);
      if(body?.status==="secret_detected"){setRouteState("secret");return}
      if(response.ok && body && (body.status==="ok"||body.status==="fallback") && body.package && Array.isArray(body.steps) && body.steps.length===3){
        setRoute(body as RouteResult);setRouteState("ready");return;
      }
      setRoute(local);setRouteState("error");
    } catch { setRoute(local);setRouteState("error"); }
  }

  async function copyBrief(){
    if(!display?.brief)return;
    try{await navigator.clipboard.writeText(display.brief);setCopyState("done")}catch{setCopyState("error")}
  }

  async function sendBrief(event:FormEvent<HTMLFormElement>){
    event.preventDefault();
    if(!display||!audience||!privacy||(youth&&!adultConfirmed))return;
    setLeadState("sending");
    const leadAudience=audience==="kids"?"parent":audience==="teens"?"teen":audience;
    try{
      const response=await fetch("/api/lead",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
        name:name.trim(),contact:contact.trim(),goal:display.brief.slice(0,600),program:display.package.id.replace(":","-"),audience:leadAudience,locale,
        privacyConsent:"yes",adultConfirmation:youth?"yes":"",website:"",sourcePath:`${base}/matcher`,
      })});
      setLeadState(response.ok?"sent":"error");
    }catch{setLeadState("error")}
  }

  const choose=<T extends string>(value:T,current:T|null,setter:(v:T)=>void,label:string)=>(
    <button type="button" className={`matcherOption ${current===value?"isSelected":""}`} aria-pressed={current===value} onClick={()=>{setter(value);setRoute(null);setRouteState("idle");setLeadState("idle");setCopyState("idle")}}>{label}</button>
  );

  return <div className="matcherShell">
    <div className="matcherPrivacy statusDot">{t.privacy}</div>
    <section className="matcherQuestion"><h2>{t.audience}</h2><div className="matcherOptions">{t.audienceOptions.map(([v,l])=>choose(v as Audience,audience,setAudience,l))}</div></section>
    <section className="matcherQuestion"><h2>{t.goal}</h2><div className="matcherOptions">{t.goalOptions.map(([v,l])=>choose(v as Goal,goal,setGoal,l))}</div></section>
    <section className="matcherQuestion"><h2>{t.depth}</h2><div className="matcherOptions">{t.depthOptions.map(([v,l])=>choose(v as Depth,depth,setDepth,l))}</div></section>
    <section className="matcherQuestion"><h2>{t.goalText}</h2><textarea className="matcherGoalInput" value={goalText} maxLength={2000} rows={4} placeholder={t.goalPlaceholder} onChange={(e)=>{setGoalText(e.target.value);setRoute(null);setRouteState("idle")}}/><button className="button buttonPrimary" type="button" disabled={!audience||!goal||!depth||!goalText.trim()||routeState==="loading"} onClick={runRoute}>{routeState==="loading"?t.running:t.run}</button></section>
    <IntroCallCta locale={locale}/>
    <section className="matcherResult" aria-live="polite">
      <span className="cardMeta">{t.resultLabel}</span>
      {routeState==="secret"?<p className="matcherEmpty">{t.secret}</p>:!display?<p className="matcherEmpty">{t.noResult}</p>:<>
        {routeState==="error"?<p className="matcherNotice">{t.unavailable}</p>:null}
        <div className="matcherResultTop"><div><h2>{display.package.name}</h2><p>{display.package.sessions}</p></div><strong>{display.package.price}</strong></div>
        <div className="matcherReason"><b>{t.why}</b><ol>{display.steps.map((step,i)=><li key={i}>{step}</li>)}</ol></div>
        <p className="matcherNote">{t.note}</p>
        <div className="heroActions"><button type="button" className="button buttonGhost" onClick={copyBrief}>{copyState==="done"?t.copied:copyState==="error"?t.copyError:t.copy}</button><button type="button" className="matcherReset" onClick={()=>{setAudience(null);setGoal(null);setDepth(null);setGoalText("");setRoute(null);setRouteState("idle");setLeadState("idle")}}>{t.reset}</button></div>
        <form className="leadForm matcherLeadForm" onSubmit={sendBrief}>
          <h3>{t.leadTitle}</h3>
          <div className="formRow"><label>{t.leadName}<input required maxLength={80} value={name} onChange={e=>setName(e.target.value)}/></label><label>{t.leadContact}<input required maxLength={120} value={contact} onChange={e=>setContact(e.target.value)}/></label></div>
          <label className="consentRow"><input type="checkbox" checked={privacy} onChange={e=>setPrivacy(e.target.checked)} required/><span>{t.leadConsent} <Link href={`${base}/privacy`}>{en?"Privacy notice":"Конфиденциальность"}</Link>.</span></label>
          {youth?<label className="consentRow consentYouth"><input type="checkbox" checked={adultConfirmed} onChange={e=>setAdultConfirmed(e.target.checked)} required/><span>{t.adult} <Link href={`${base}/safety`}>{en?"Youth AI safety":"Безопасность детей и ИИ"}</Link>.</span></label>:null}
          <button className="button buttonPrimary" type="submit" disabled={leadState==="sending"||!privacy||(youth&&!adultConfirmed)}>{leadState==="sending"?t.sending:t.send}</button>
          {leadState==="sent"?<p className="formMessage success">{t.sent}</p>:leadState==="error"?<p className="formMessage error">{t.sendError}</p>:null}
        </form>
      </>}
    </section>
  </div>;
}
