"use client";
import { useState } from "react";
type Locale="ru"|"en"; type Key="research"|"build"|"automate"|"verify";
type State={label:string;signal:string;human:string;ship:string};
const states:Record<Locale,Record<Key,State>>={
ru:{research:{label:"RESEARCH",signal:"● SOURCE-BACKED",human:"SOURCES",ship:"DECISION BRIEF"},build:{label:"BUILD",signal:"● SHIPPABLE",human:"QA",ship:"PROTOTYPE"},automate:{label:"AUTOMATE",signal:"● REPEATABLE",human:"OWNER",ship:"WORKFLOW"},verify:{label:"VERIFY",signal:"● RELEASE-GATED",human:"GATE",ship:"RECEIPT"}},
en:{research:{label:"RESEARCH",signal:"● SOURCE-BACKED",human:"SOURCES",ship:"DECISION BRIEF"},build:{label:"BUILD",signal:"● SHIPPABLE",human:"QA",ship:"PROTOTYPE"},automate:{label:"AUTOMATE",signal:"● REPEATABLE",human:"OWNER",ship:"WORKFLOW"},verify:{label:"VERIFY",signal:"● RELEASE-GATED",human:"GATE",ship:"RECEIPT"}}
};
const keys:Key[]=["research","build","automate","verify"];
const cls=["nodeA","nodeB","nodeC","nodeD"];
export function HeroEngine({locale="ru"}:{locale?:Locale}){const[active,setActive]=useState<Key>("build"),s=states[locale][active];const l=locale==="ru"?{mode:"РЕЖИМ",human:"HUMAN",ship:"SHIP"}:{mode:"MODE",human:"HUMAN",ship:"SHIP"};return <div className="heroVisual" aria-label={locale==="ru"?"Интерактивная схема AI Skill Engine":"Interactive AI Skill Engine"} data-hero-engine><div className="visualTop"><span>AI SKILL ENGINE</span><span className="livePill">{s.signal}</span></div><div className="visualCore"><div className="coreRing ring1"/><div className="coreRing ring2"/><div className="coreCenter">AI</div>{keys.map((key,i)=><button type="button" key={key} className={`node ${cls[i]} ${active===key?"isActive":""}`} data-engine-key={key} aria-pressed={active===key} onClick={()=>setActive(key)}>{states[locale][key].label}</button>)}</div><div className="visualBottom" aria-live="polite"><div><span>01 · {l.mode}</span><b>{s.label}</b></div><i/><div><span>02 · {l.human}</span><b>{s.human}</b></div><i/><div><span>03 · {l.ship}</span><b>{s.ship}</b></div></div></div>}
