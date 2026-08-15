"use client";
import { useState } from "react";
type Locale="ru"|"en"; type Key="research"|"build"|"automate"|"verify";
type State={label:string;signal:string;human:string;ship:string;focus:string;output:string};
const states:Record<Locale,Record<Key,State>>={
ru:{
research:{label:"RESEARCH",signal:"● SOURCE-BACKED",human:"SOURCES",ship:"DECISION BRIEF",focus:"Вопрос → источники → synthesis",output:"Source-backed brief"},
build:{label:"BUILD",signal:"● SHIPPABLE",human:"QA",ship:"PROTOTYPE",focus:"Spec → prototype → tests",output:"Working prototype"},
automate:{label:"AUTOMATE",signal:"● REPEATABLE",human:"OWNER",ship:"WORKFLOW",focus:"Process → logic → fallback",output:"Repeatable workflow"},
verify:{label:"VERIFY",signal:"● RELEASE-GATED",human:"GATE",ship:"RECEIPT",focus:"Claim → evidence → gate",output:"Release receipt"}},
en:{
research:{label:"RESEARCH",signal:"● SOURCE-BACKED",human:"SOURCES",ship:"DECISION BRIEF",focus:"Question → sources → synthesis",output:"Source-backed brief"},
build:{label:"BUILD",signal:"● SHIPPABLE",human:"QA",ship:"PROTOTYPE",focus:"Spec → prototype → tests",output:"Working prototype"},
automate:{label:"AUTOMATE",signal:"● REPEATABLE",human:"OWNER",ship:"WORKFLOW",focus:"Process → logic → fallback",output:"Repeatable workflow"},
verify:{label:"VERIFY",signal:"● RELEASE-GATED",human:"GATE",ship:"RECEIPT",focus:"Claim → evidence → gate",output:"Release receipt"}}
};
const keys:Key[]=["research","build","automate","verify"];
export function HeroEngine({locale="ru"}:{locale?:Locale}){
 const[active,setActive]=useState<Key>("build"),s=states[locale][active];
 const l=locale==="ru"?{mode:"РЕЖИМ",human:"HUMAN",ship:"SHIP",active:"ACTIVE WORKFLOW",define:"Цель + ограничения",build:"AI-assisted draft",verify:"Human gate"}:{mode:"MODE",human:"HUMAN",ship:"SHIP",active:"ACTIVE WORKFLOW",define:"Goal + constraints",build:"AI-assisted draft",verify:"Human gate"};
 return <div className="heroVisual engineScene" aria-label={locale==="ru"?"Интерактивная схема AI Skill Engine":"Interactive AI Skill Engine"} data-hero-engine>
  <div className="visualTop"><span>AI SKILL ENGINE / LIVE SCENE</span><span className="livePill">{s.signal}</span></div>
  <div className="engineLayout">
   <div className="engineModes" aria-label={locale==="ru"?"Режим AI Skill Engine":"AI Skill Engine mode"}>{keys.map(key=><button type="button" key={key} className={`engineMode ${active===key?"isActive":""}`} data-engine-key={key} aria-pressed={active===key} onClick={()=>setActive(key)}>{states[locale][key].label}</button>)}</div>
   <div className="engineWorkbench">
    <div className="engineTask"><span>{l.active}</span><strong id="engine-focus">{s.focus}</strong></div>
    <div className="engineTrack">
     <article><span>01</span><b>DEFINE</b><small>{l.define}</small></article>
     <article className="isLive"><span>02</span><b>BUILD</b><small>{l.build}</small></article>
     <article><span>03</span><b>VERIFY</b><small>{l.verify}</small></article>
     <article><span>04</span><b>SHIP</b><small id="engine-output">{s.output}</small></article>
    </div>
    <div className="engineReceipt"><span>human gate</span><b>{s.human}</b><i/><span>artifact</span><b>{s.ship}</b></div>
   </div>
  </div>
  <div className="visualBottom" aria-live="polite"><div><span>01 · {l.mode}</span><b>{s.label}</b></div><i/><div><span>02 · {l.human}</span><b>{s.human}</b></div><i/><div><span>03 · {l.ship}</span><b>{s.ship}</b></div></div>
 </div>
}
