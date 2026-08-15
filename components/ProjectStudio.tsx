"use client";

import { useMemo, useState } from "react";

type Locale = "ru" | "en";
type Filter = "all" | "research" | "create" | "build" | "automate";
type Project = {
  meta: string;
  title: string;
  summary: string;
  audience: string;
  tags: Filter[];
  goal: string;
  ai: string;
  human: string;
  artifact: string;
};

const projects: Record<Locale, Project[]> = {
  ru: [
    { meta:"01 · RESEARCH", title:"Детектив фактов", summary:"Тема → 3+ источника → таблица утверждений → короткая презентация «что подтвердилось / что нет».", audience:"8–13", tags:["research"], goal:"Отделить проверяемый факт от красивого ответа.", ai:"Помогает сформулировать поисковые запросы, сравнить версии и организовать находки.", human:"Открывает источники, отмечает противоречия и объясняет, почему выводу можно доверять.", artifact:"Source table + claim map + мини-презентация." },
    { meta:"02 · CREATE", title:"Мир и персонаж", summary:"Character bible, визуальные правила, storyboard и итоговая мини-история с явным разделением своей идеи и AI-помощи.", audience:"8–13", tags:["create"], goal:"Превратить идею в последовательную систему мира и персонажей.", ai:"Предлагает варианты, референс-направления и помогает проверять внутреннюю логику.", human:"Выбирает художественные решения и может объяснить, что придумал сам и где использовал AI.", artifact:"Character bible + storyboard + finished story." },
    { meta:"03 · LOGIC", title:"Мини-игра", summary:"Правила, состояния, простая логика и прототип. Ребёнок показывает, почему система работает именно так.", audience:"8–13", tags:["build","create"], goal:"Собрать маленькую работающую систему вместо одноразовой генерации.", ai:"Помогает разложить механику на правила, состояния и тестовые сценарии.", human:"Проверяет причинность, чинит сломанные правила и защищает логику проекта.", artifact:"Game rules + state map + playable prototype." },
    { meta:"04 · STUDY", title:"Research OS", summary:"Шаблон исследования: вопрос, источники, тезисы, проверка, итоговый memo и presentation.", audience:"14–18", tags:["research","build"], goal:"Сделать исследование повторяемым процессом, а не случайным набором вкладок.", ai:"Расширяет поиск, группирует evidence и помогает видеть конфликтующие версии.", human:"Оценивает качество источников и принимает аргументированный вывод.", artifact:"Research template + evidence map + memo + presentation." },
    { meta:"05 · BUILD", title:"AI assistant prototype", summary:"Простой ассистент или workflow под реальную задачу: input, rules, output, failure cases и README.", audience:"14–18", tags:["build","automate"], goal:"Превратить задачу в спецификацию, которую можно протестировать.", ai:"Помогает с декомпозицией, prompt/system rules, glue-code и тестовыми случаями.", human:"Определяет границы, проверяет ошибки и решает, где автоматизация должна остановиться.", artifact:"Prototype + test cases + README + failure map." },
    { meta:"06 · PRODUCT", title:"Mini-product", summary:"Проблема пользователя, прототип, тестовые сценарии, ограничения и короткий demo.", audience:"14–18", tags:["build","create"], goal:"Проверить продуктовую гипотезу работающим артефактом.", ai:"Помогает исследовать варианты, собрать интерфейс и ускорить итерации.", human:"Режет scope, разговаривает с пользователем и принимает продуктовые решения.", artifact:"Working prototype + QA checklist + demo + known limits." },
    { meta:"07 · WORKFLOW", title:"Personal research workflow", summary:"Повторяемая система поиска, сравнения источников, synthesis и проверки.", audience:"Adults", tags:["research","automate"], goal:"Сократить путь от вопроса до решения без потери source discipline.", ai:"Собирает варианты, сравнивает evidence и формирует структуру decision brief.", human:"Проверяет первоисточники, допущения и владеет финальным решением.", artifact:"Reusable workflow + source map + decision brief template." },
    { meta:"08 · AUTOMATION", title:"Process prototype", summary:"Ассистент или automation для одного повторяемого процесса с ownership и fallback.", audience:"Adults / business", tags:["automate","build"], goal:"Автоматизировать один процесс так, чтобы оставался понятный владелец и rollback.", ai:"Выполняет повторяемые трансформации, маршрутизацию и черновую обработку.", human:"Определяет permissions, failure modes, acceptance criteria и fallback.", artifact:"Workflow + acceptance tests + handoff + rollback path." },
    { meta:"09 · PLAYBOOK", title:"AI operating rules", summary:"Шаблоны задач, критерии проверки, data boundaries и инструкции для повторного использования.", audience:"Adults / business", tags:["automate"], goal:"Перевести разрозненные удачные промпты в управляемую операционную систему.", ai:"Помогает формализовать повторяемые шаблоны, проверки и варианты исполнения.", human:"Фиксирует права, данные, ответственность и правила эскалации.", artifact:"Playbook + task templates + verification rules + governance notes." },
  ],
  en: [
    { meta:"01 · RESEARCH", title:"Fact detective", summary:"Topic → 3+ sources → claim table → short presentation of what was verified and what was not.", audience:"8–13", tags:["research"], goal:"Separate a verifiable fact from a convincing-looking answer.", ai:"Helps form search queries, compare versions and organize findings.", human:"Opens the sources, marks contradictions and explains why a conclusion is trustworthy.", artifact:"Source table + claim map + mini presentation." },
    { meta:"02 · CREATE", title:"World & character", summary:"Character bible, visual rules, storyboard and a short final story with clear separation between the learner’s idea and AI assistance.", audience:"8–13", tags:["create"], goal:"Turn an idea into a coherent system of world and character rules.", ai:"Explores alternatives, reference directions and consistency checks.", human:"Owns the creative choices and can explain what came from them versus AI assistance.", artifact:"Character bible + storyboard + finished story." },
    { meta:"03 · LOGIC", title:"Mini game", summary:"Rules, states, simple logic and a prototype the learner can explain.", audience:"8–13", tags:["build","create"], goal:"Build a small working system instead of a one-shot generation.", ai:"Helps decompose mechanics into rules, states and test scenarios.", human:"Checks causality, repairs broken rules and defends the project logic.", artifact:"Game rules + state map + playable prototype." },
    { meta:"04 · STUDY", title:"Research OS", summary:"A reusable research template: question, sources, claims, verification, memo and presentation.", audience:"14–18", tags:["research","build"], goal:"Make research a repeatable process instead of a pile of browser tabs.", ai:"Expands search, groups evidence and surfaces conflicting versions.", human:"Evaluates source quality and owns the argued conclusion.", artifact:"Research template + evidence map + memo + presentation." },
    { meta:"05 · BUILD", title:"AI assistant prototype", summary:"A simple assistant or workflow for a real task: input, rules, output, failure cases and README.", audience:"14–18", tags:["build","automate"], goal:"Turn a task into a specification that can be tested.", ai:"Helps with decomposition, prompt/system rules, glue code and test cases.", human:"Defines boundaries, checks failures and decides where automation must stop.", artifact:"Prototype + test cases + README + failure map." },
    { meta:"06 · PRODUCT", title:"Mini-product", summary:"User problem, prototype, test scenarios, limitations and a short demo.", audience:"14–18", tags:["build","create"], goal:"Test a product hypothesis with a working artifact.", ai:"Explores directions, helps assemble the interface and accelerates iteration.", human:"Cuts scope, talks to users and owns product decisions.", artifact:"Working prototype + QA checklist + demo + known limits." },
    { meta:"07 · WORKFLOW", title:"Personal research workflow", summary:"A repeatable system for search, source comparison, synthesis and verification.", audience:"Adults", tags:["research","automate"], goal:"Shorten the path from question to decision without losing source discipline.", ai:"Collects alternatives, compares evidence and structures a decision brief.", human:"Checks primary sources, assumptions and owns the final decision.", artifact:"Reusable workflow + source map + decision brief template." },
    { meta:"08 · AUTOMATION", title:"Process prototype", summary:"An assistant or automation serving one repeatable process, with ownership and fallback.", audience:"Adults / business", tags:["automate","build"], goal:"Automate one process while keeping an explicit owner and rollback path.", ai:"Runs repeatable transforms, routing and first-pass processing.", human:"Defines permissions, failure modes, acceptance criteria and fallback.", artifact:"Workflow + acceptance tests + handoff + rollback path." },
    { meta:"09 · PLAYBOOK", title:"AI operating rules", summary:"Task templates, verification criteria, data boundaries and repeatable instructions.", audience:"Adults / business", tags:["automate"], goal:"Turn scattered successful prompts into a governed operating system.", ai:"Helps formalize repeatable templates, checks and execution variants.", human:"Defines permissions, data boundaries, accountability and escalation rules.", artifact:"Playbook + task templates + verification rules + governance notes." },
  ],
};

const filterKeys: Filter[] = ["all","research","create","build","automate"];

export function ProjectStudio({ locale = "ru" }: { locale?: Locale }) {
  const [active, setActive] = useState<Filter>("all");
  const list = projects[locale];
  const visible = useMemo(() => active === "all" ? list : list.filter(p => p.tags.includes(active)), [active, list]);
  const labels = locale === "ru"
    ? { all:"Все", research:"Research", create:"Create", build:"Build", automate:"Automate", goal:"Задача", ai:"AI role", human:"Human check", artifact:"Artifact", count:"проектов показано", local:"Локальный фильтр · данные не отправляются" }
    : { all:"All", research:"Research", create:"Create", build:"Build", automate:"Automate", goal:"Goal", ai:"AI role", human:"Human check", artifact:"Artifact", count:"projects shown", local:"Local filter · no data is sent" };
  return <div className="projectStudio" data-project-studio>
    <div className="projectStudioTop">
      <div className="projectFilters" role="group" aria-label={locale === "ru" ? "Фильтр проектов" : "Project filter"}>
        {filterKeys.map(key => <button key={key} type="button" className={`projectFilter ${active===key?"isActive":""}`} aria-pressed={active===key} onClick={()=>setActive(key)}>{labels[key]}</button>)}
      </div>
      <div className="projectStudioStatus" aria-live="polite"><i/>{visible.length} / {list.length} {labels.count}<span>{labels.local}</span></div>
    </div>
    <div className="projectStudioGrid">
      {list.map((p, index) => {
        const hidden = !visible.includes(p);
        return <article className="projectStudioCard" key={p.meta} hidden={hidden} data-project-tags={p.tags.join(" ")}>
          <div className="projectCardTop"><span>{p.meta}</span><b>{p.audience}</b></div>
          <h2><small>0{index+1}</small>{p.title}</h2><p className="projectSummary">{p.summary}</p>
          <div className="projectAnatomy"><p><span>01</span><b>{labels.goal}</b><em>{p.goal}</em></p><p><span>02</span><b>{labels.ai}</b><em>{p.ai}</em></p><p><span>03</span><b>{labels.human}</b><em>{p.human}</em></p><p><span>04</span><b>{labels.artifact}</b><em>{p.artifact}</em></p></div>
        </article>;
      })}
    </div>
    <noscript><p className="projectNoJs">{locale === "ru" ? "JavaScript выключен — все примеры проектов показаны без фильтра." : "JavaScript is disabled — all project examples remain visible without filtering."}</p></noscript>
  </div>;
}
