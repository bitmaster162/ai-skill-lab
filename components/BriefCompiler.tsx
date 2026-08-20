"use client";

import { useCallback, useMemo, useState } from "react";

type Locale="ru"|"en";
type Group="goal"|"context"|"output"|"verify";
type Choice={key:string;label:string;value:string};

const DATA:Record<Locale,Record<Group,Choice[]>>={
  ru:{
    goal:[
      {key:"research",label:"Research",value:"Разобраться и принять решение"},
      {key:"build",label:"Build",value:"Собрать работающий AI-прототип"},
      {key:"automate",label:"Automate",value:"Автоматизировать повторяемый процесс"},
      {key:"learn",label:"Learn",value:"Освоить навык и повторить процесс"},
    ],
    context:[
      {key:"solo",label:"Solo",value:"Личная работа · один owner"},
      {key:"team",label:"Team",value:"Команда · общий workflow"},
      {key:"business",label:"Business",value:"Бизнес-процесс · owner"},
      {key:"family",label:"Family",value:"Обучение · adult safety"},
    ],
    output:[
      {key:"brief",label:"Brief",value:"Decision brief + source map"},
      {key:"prototype",label:"Prototype",value:"Working prototype + known limits"},
      {key:"workflow",label:"Workflow",value:"Workflow + fallback + handoff"},
      {key:"project",label:"Project",value:"Project + explanation + checklist"},
    ],
    verify:[
      {key:"sources",label:"Sources",value:"Проверить источники / допущения"},
      {key:"qa",label:"Human QA",value:"Human QA до выпуска"},
      {key:"tests",label:"Tests",value:"Acceptance tests + stop condition"},
      {key:"explain",label:"Explain",value:"Объяснить результат и повторить процесс"},
    ],
  },
  en:{
    goal:[
      {key:"research",label:"Research",value:"Understand a question and make a decision"},
      {key:"build",label:"Build",value:"Build a working AI prototype"},
      {key:"automate",label:"Automate",value:"Automate a repeatable process"},
      {key:"learn",label:"Learn",value:"Learn a skill and repeat the process independently"},
    ],
    context:[
      {key:"solo",label:"Solo",value:"Personal work · one decision owner"},
      {key:"team",label:"Team",value:"Team · shared workflow"},
      {key:"business",label:"Business",value:"Business process · named owner"},
      {key:"family",label:"Family",value:"Learning · adult safety layer"},
    ],
    output:[
      {key:"brief",label:"Brief",value:"Decision brief + source map"},
      {key:"prototype",label:"Prototype",value:"Working prototype + known limits"},
      {key:"workflow",label:"Workflow",value:"Workflow + fallback + handoff"},
      {key:"project",label:"Project",value:"Project + explanation + checklist"},
    ],
    verify:[
      {key:"sources",label:"Sources",value:"Check sources and assumptions"},
      {key:"qa",label:"Human QA",value:"Human QA before release"},
      {key:"tests",label:"Tests",value:"Acceptance tests + stop condition"},
      {key:"explain",label:"Explain",value:"Explain the result and repeat the process"},
    ],
  }
};

const defaults={goal:"build",context:"solo",output:"prototype",verify:"qa"} as const;

export function BriefCompiler({locale="ru"}:{locale?:Locale}){
  const [state,setState]=useState<Record<Group,string>>({...defaults});
  const [copyState,setCopyState]=useState<"idle"|"copied"|"failed">("idle");
  const d=DATA[locale];
  const selected=useCallback((group:Group)=>d[group].find(x=>x.key===state[group])!,[d,state]);
  const brief=useMemo(()=>{
    const lines=locale==="ru"?[
      `GOAL: ${selected("goal").value}`,
      `CONTEXT: ${selected("context").value}`,
      `OUTPUT: ${selected("output").value}`,
      `VERIFY: ${selected("verify").value}`,
      "HUMAN GATE: не выпускать без подтверждённой человеком проверки.",
    ]:[
      `GOAL: ${selected("goal").value}`,
      `CONTEXT: ${selected("context").value}`,
      `OUTPUT: ${selected("output").value}`,
      `VERIFY: ${selected("verify").value}`,
      "HUMAN GATE: do not ship until the verification criterion is confirmed by a person.",
    ];
    return lines.join("\n");
  },[locale,selected]);
  const labels=locale==="ru"?{goal:"01 · GOAL",context:"02 · CONTEXT",output:"03 · OUTPUT",verify:"04 · VERIFY",telegram:"Открыть Telegram с brief →",copy:"Скопировать brief",copied:"Скопировано",failed:"Не удалось скопировать",local:"Локальный compiler · ничего не отправляется"}:{goal:"01 · GOAL",context:"02 · CONTEXT",output:"03 · OUTPUT",verify:"04 · VERIFY",telegram:"Open Telegram with brief →",copy:"Copy brief",copied:"Copied",failed:"Copy failed",local:"Local compiler · nothing is sent"};
  const choose=(group:Group,key:string)=>{setState(s=>({...s,[group]:key}));setCopyState("idle")};
  const copy=async()=>{try{await navigator.clipboard.writeText(brief);setCopyState("copied")}catch{setCopyState("failed")}};
  const telegramHref=`https://t.me/BiTFormer?text=${encodeURIComponent(brief)}`;
  return <div className="proofLab" data-brief-compiler>
    <div className="proofLabSignal"><i/>{labels.local}</div>
    {(["goal","context","output","verify"] as Group[]).map(group=><div key={group}>
      <span className="cardMeta">{labels[group]}</span>
      <div className="proofLabTabs" role="group" aria-label={labels[group]}>{d[group].map(x=><button key={x.key} type="button" className={`proofLabTab ${state[group]===x.key?"isActive":""}`} data-brief-group={group} data-brief-key={x.key} aria-pressed={state[group]===x.key} onClick={()=>choose(group,x.key)}>{x.label}</button>)}</div>
    </div>)}
    <div className="proofLabStage" aria-live="polite"><div className="proofLabTitleRow"><div><span>COMPILED / BRIEF</span><h2>{locale==="ru"?"Намерение → спецификация":"Intent → specification"}</h2></div><strong>HUMAN-GATED</strong></div><div className="proofFlow"><article><span>01 · GOAL</span><b id="brief-goal">{selected("goal").label}</b><p>{selected("goal").value}</p></article><article><span>02 · CONTEXT</span><b id="brief-context">{selected("context").label}</b><p>{selected("context").value}</p></article><article><span>03 · OUTPUT</span><b id="brief-output">{selected("output").label}</b><p>{selected("output").value}</p></article><article><span>04 · VERIFY</span><b id="brief-verify">{selected("verify").label}</b><p>{selected("verify").value}</p></article></div><div className="heroActions"><a className="button buttonPrimary" href={telegramHref} target="_blank" rel="noopener noreferrer">{labels.telegram}</a><button className="button buttonGhost" type="button" onClick={copy}>{labels.copy}</button><span className="finePrint" aria-live="polite">{copyState==="copied"?labels.copied:copyState==="failed"?labels.failed:""}</span></div></div>
  </div>
}
