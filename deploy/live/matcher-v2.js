(function(){"use strict";
const FACTS={"schema":"ai-skill-lab.commercial-facts.v2","version":2,"currency":"USD","session_duration_minutes":60,"tracks":{"adult":[{"id":"start","name":"Start","price":"$390","sessions_ru":"4 занятия","sessions_en":"4 sessions","summary_ru":"Базовый AI-процесс и первый полезный результат.","summary_en":"A practical AI workflow and a first useful result."},{"id":"personal","name":"Personal","price":"$890","sessions_ru":"10 занятий","sessions_en":"10 sessions","summary_ru":"Персональная траектория, шаблоны и итоговый проект.","summary_en":"A tailored route, reusable templates and a final project."},{"id":"intensive","name":"Intensive","price":"$1,290","sessions_ru":"12 занятий + проект","sessions_en":"12 sessions + project","summary_ru":"Автоматизация, AI-агент, продукт или portfolio.","summary_en":"Automation, an AI agent, product or portfolio project."}],"kids":[{"id":"mini","name":"Mini","price":"$290","sessions_ru":"4 занятия","sessions_en":"4 sessions","summary_ru":"Знакомство с AI и небольшой проект.","summary_en":"An introduction to AI and a small project."},{"id":"creator","name":"Creator","price":"$890","sessions_ru":"10 занятий","sessions_en":"10 sessions","summary_ru":"Полный маршрут с самостоятельной презентацией.","summary_en":"A full route with an independent final presentation."},{"id":"studio","name":"Studio","price":"$1,190","sessions_ru":"12 занятий","sessions_en":"12 sessions","summary_ru":"Больше времени на сложный проект.","summary_en":"More time for a complex project."}],"teens":[{"id":"explorer","name":"Explorer","price":"$490","sessions_ru":"6 занятий","sessions_en":"6 sessions","summary_ru":"AI literacy, research и небольшой проект.","summary_en":"AI literacy, research and a small project."},{"id":"portfolio","name":"Portfolio","price":"$890","sessions_ru":"10 занятий","sessions_en":"10 sessions","summary_ru":"Полный маршрут с законченной работой.","summary_en":"A full route with a finished artifact."},{"id":"builder","name":"Builder","price":"$1,290","sessions_ru":"12 занятий","sessions_en":"12 sessions","summary_ru":"Больше кода, automation и product thinking.","summary_en":"More code, automation and product thinking."}]},"family":{"id":"family","name":"Family Concierge","price":"$1,490","sessions_ru":"12 занятий + 2 сессии родителю","sessions_en":"12 learner sessions + 2 parent sessions","summary_ru":"Обучение плюс семейные правила безопасного использования AI.","summary_en":"Learning plus a practical family AI-safety framework."},"diagnostic":{"name_ru":"Диагностическая сессия","name_en":"Diagnostic session","price":"$120","credit_days":14,"credit_ru":"Зачтём в стоимость пакета при покупке в течение 14 дней.","credit_en":"Credited toward a package purchased within 14 days."},"business":{"display":"Custom scope","workflow_audit":{"name_ru":"Workflow audit","name_en":"Workflow audit","price":"$890","price_mode":"fixed"},"team_training":{"name_ru":"Обучение команды","name_en":"Team training","price_from_per_session":"$390","max_people":5,"min_sessions":4,"total_from":"$1,560"},"implementation_pilot":{"name_ru":"Implementation pilot","name_en":"Implementation pilot","price_from":"$4,900","scope_cap_hours":35}},"recurring":{"operating_support":{"name_ru":"Operating support","name_en":"Operating support","price_monthly":"$490","hours":4},"operating_partner":{"name_ru":"Operating partner","name_en":"Operating partner","price_monthly":"$890","hours":8},"office_hours":{"name_ru":"Office hours","name_en":"Office hours","price_monthly":"$178","sessions":2}},"pair":{"name_ru":"Парный формат","name_en":"Pair format","multiplier":1.6,"participant_discount_percent":20}};
const en=document.documentElement.lang==="en";
const locale=en?"en":"ru";
const base=en?"/en":"";
const intro=en?"Free 15-minute intro call":"Бесплатный звонок-знакомство · 15 минут";
const diagnostic=en
  ? `Diagnostic session ${FACTS.diagnostic.price} · ${FACTS.session_duration_minutes} minutes · ${FACTS.diagnostic.credit_en}`
  : `Диагностика ${FACTS.diagnostic.price} · ${FACTS.session_duration_minutes} минут · ${FACTS.diagnostic.credit_ru}`;
const copy=en?{
  empty:"Choose three options and describe the goal. Nothing is sent until you press the button.",
  running:"Finding a route…",run:"Find a route with AI",steps:"Next steps",
  note:"The result is automatic: it is not a promised outcome or an automatic fit approval. Scope and terms are confirmed by a human.",
  unavailable:"AI routing is unavailable right now. A local recommendation from the same package table is shown.",
  secret:"The goal appears to contain a secret or credential. Remove it; those values are not sent to the model.",
  copy:"Copy brief",copied:"Copied",copyError:"Copy failed",reset:"Reset",
  leadTitle:"Send this brief",name:"Name",contact:"How should we contact you?",
  consent:'I agree to the processing of this application as described in the <a href="/en/privacy">Privacy notice</a>.',
  adult:'I am an adult organizing the learner\'s training and the contact belongs to an adult. <a href="/en/safety">Youth AI safety</a>.',
  send:"Send brief",sending:"Sending…",sent:"Brief sent. We reply within 1–2 business days.",
  sendError:"Brief could not be sent. You can use a direct contact channel instead."
}:{
  empty:"Выберите три варианта и опишите цель. До нажатия кнопки ничего не отправляется.",
  running:"Подбираем…",run:"Подобрать маршрут с AI",steps:"Следующие шаги",
  note:"Результат автоматический: это не обещание результата и не подтверждение fit. Scope и условия сверяются человеком.",
  unavailable:"AI-маршрут сейчас недоступен. Показана локальная рекомендация по той же таблице пакетов.",
  secret:"Похоже, в цели есть секрет или ключ. Удалите его: такие данные не передаются модели.",
  copy:"Скопировать brief",copied:"Скопировано",copyError:"Не удалось скопировать",reset:"Сбросить",
  leadTitle:"Отправить этот brief",name:"Имя",contact:"Как связаться",
  consent:'Согласен(на) на обработку этой заявки по правилам <a href="/privacy">конфиденциальности</a>.',
  adult:'Я совершеннолетний взрослый, организующий обучение; контакт принадлежит взрослому. <a href="/safety">Безопасность детей и AI</a>.',
  send:"Отправить brief",sending:"Отправляем…",sent:"Brief отправлен. Ответим в течение 1–2 рабочих дней.",
  sendError:"Не удалось отправить brief. Можно использовать прямой канал связи."
};
const S={audience:null,goal:null,depth:null,result:null,state:"idle"};
const output=document.getElementById("matcher-output");
const goalInput=document.getElementById("matcher-goal");
const runButton=document.getElementById("matcher-run");
const secretPatterns=[/\bsk-[A-Za-z0-9_-]{8,}/i,/\bghp_[A-Za-z0-9]{8,}/i,/\bgithub_pat_[A-Za-z0-9_]{8,}/i,/\bxox[A-Za-z]-[A-Za-z0-9-]{8,}/i,/\bAKIA[A-Z0-9]{8,}/,/-----BEGIN [A-Z0-9 ]+-----/,/\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/,/\b[0-9a-f]{32,}\b/i];

function esc(x){return String(x).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]))}
function hasSecret(x){return secretPatterns.some(p=>p.test(String(x)))}
function planTable(audience){
  if(audience!=="business")return FACTS.tracks[audience].map(p=>({id:audience+":"+p.id,name:p.name,price:p.price,sessions:en?p.sessions_en:p.sessions_ru}));
  const b=FACTS.business;
  return [
    {id:"business:workflow_audit",name:en?b.workflow_audit.name_en:b.workflow_audit.name_ru,price:b.workflow_audit.price,sessions:en?"fixed scope":"фиксированный scope"},
    {id:"business:team_training",name:en?b.team_training.name_en:b.team_training.name_ru,price:(en?"from ":"от ")+b.team_training.price_from_per_session+(en?"/session":"/сессия"),sessions:en?"minimum "+b.team_training.min_sessions+" sessions":"минимум "+b.team_training.min_sessions+" занятия"},
    {id:"business:implementation_pilot",name:en?b.implementation_pilot.name_en:b.implementation_pilot.name_ru,price:(en?"from ":"от ")+b.implementation_pilot.price_from,sessions:en?"scope cap "+b.implementation_pilot.scope_cap_hours+" hours":"потолок scope "+b.implementation_pilot.scope_cap_hours+" часов"}
  ];
}
function localResult(){
  if(!S.audience||!S.goal||!S.depth)return null;
  const table=planTable(S.audience);let pkg;
  if(S.audience==="business"){
    pkg=S.goal==="automate"||S.depth==="deep"?table[2]:S.goal==="team"?table[1]:table[0];
  }else pkg=table[S.depth==="deep"?2:S.depth==="core"?1:0];
  const third=en?"Start "+pkg.name+" with one bounded project and a review checkpoint.":"Начать "+pkg.name+" с одного ограниченного проекта и контрольной точки проверки.";
  const brief=(en?"Route request: ":"Запрос на маршрут: ")+pkg.name+(en?". Goal provided in matcher.":". Цель описана в matcher.");
  return {status:"fallback",package:pkg,steps:[intro,diagnostic,third],brief};
}
async function copyText(text){
  try{await navigator.clipboard.writeText(text);return true}catch{
    try{const ta=document.createElement("textarea");ta.value=text;ta.setAttribute("readonly","");ta.style.position="fixed";ta.style.opacity="0";document.body.appendChild(ta);ta.select();const ok=document.execCommand("copy");ta.remove();return ok}catch{return false}
  }
}
function renderEmpty(message){
  output.innerHTML='<p class="mempty">'+esc(message||copy.empty)+'</p>';
}
function leadFormHtml(){
  const youth=S.audience==="kids"||S.audience==="teens";
  return '<form class="leadForm matcherLeadForm" id="matcher-lead-form"><h3>'+esc(copy.leadTitle)+'</h3><div class="formRow"><label>'+esc(copy.name)+'<input id="matcher-lead-name" required maxlength="80"></label><label>'+esc(copy.contact)+'<input id="matcher-lead-contact" required maxlength="120"></label></div><label class="consentRow"><input id="matcher-lead-consent" type="checkbox" required><span>'+copy.consent+'</span></label>'+(youth?'<label class="consentRow consentYouth"><input id="matcher-lead-adult" type="checkbox" required><span>'+copy.adult+'</span></label>':'')+'<button class="btn light" id="matcher-lead-submit" type="submit">'+esc(copy.send)+'</button><p class="formMessage" id="matcher-lead-message"></p></form>';
}
function renderResult(result,notice){
  S.result=result;
  output.innerHTML=(notice?'<p class="matcherNotice">'+esc(notice)+'</p>':'')+
    '<div class="mrtop"><div><h2>'+esc(result.package.name)+'</h2><p>'+esc(result.package.sessions)+'</p></div><strong>'+esc(result.package.price)+'</strong></div>'+
    '<div class="mreason"><b>'+esc(copy.steps)+'</b><ol>'+result.steps.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ol></div>'+
    '<p class="mnote">'+esc(copy.note)+'</p><div class="actions"><button class="btn ghost" id="mcopy" type="button">'+esc(copy.copy)+'</button><button class="mreset" id="mreset" type="button">'+esc(copy.reset)+'</button></div>'+
    leadFormHtml();
  document.getElementById("mreset").addEventListener("click",reset);
  document.getElementById("mcopy").addEventListener("click",async function(){const ok=await copyText(S.result.brief);this.textContent=ok?copy.copied:copy.copyError});
  document.getElementById("matcher-lead-form").addEventListener("submit",sendLead);
}
async function runRoute(){
  const goalText=(goalInput.value||"").trim();
  if(!S.audience||!S.goal||!S.depth||!goalText)return;
  if(hasSecret(goalText)){S.state="secret";S.result=null;renderEmpty(copy.secret);return}
  S.state="loading";runButton.disabled=true;runButton.textContent=copy.running;
  try{
    const response=await fetch("/api/route",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({audience:S.audience,answers:[S.audience,S.goal,S.depth],goal:goalText,locale,adultConfirmed:false})});
    const body=await response.json().catch(()=>null);
    if(body&&body.status==="secret_detected"){S.state="secret";S.result=null;renderEmpty(copy.secret);return}
    if(response.ok&&body&&(body.status==="ok"||body.status==="fallback")&&body.package&&Array.isArray(body.steps)&&body.steps.length===3){S.state="ready";renderResult(body,"");return}
    S.state="error";renderResult(localResult(),copy.unavailable);
  }catch{S.state="error";renderResult(localResult(),copy.unavailable)}
  finally{runButton.disabled=false;runButton.textContent=copy.run}
}
async function sendLead(event){
  event.preventDefault();
  if(!S.result)return;
  const youth=S.audience==="kids"||S.audience==="teens";
  const name=document.getElementById("matcher-lead-name").value.trim();
  const contact=document.getElementById("matcher-lead-contact").value.trim();
  const consent=document.getElementById("matcher-lead-consent").checked;
  const adult=!youth||document.getElementById("matcher-lead-adult").checked;
  const button=document.getElementById("matcher-lead-submit");
  const message=document.getElementById("matcher-lead-message");
  if(!name||!contact||!consent||!adult)return;
  button.disabled=true;button.textContent=copy.sending;message.textContent="";
  const audience=S.audience==="kids"?"parent":S.audience==="teens"?"teen":S.audience;
  try{
    const response=await fetch("/api/lead",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,contact,goal:S.result.brief.slice(0,600),program:String(S.result.package.id).replace(":","-"),audience,locale,privacyConsent:"yes",adultConfirmation:youth?"yes":"",website:"",sourcePath:base+"/matcher"})});
    message.textContent=response.ok?copy.sent:copy.sendError;message.className="formMessage "+(response.ok?"success":"error");
  }catch{message.textContent=copy.sendError;message.className="formMessage error"}
  finally{button.disabled=false;button.textContent=copy.send}
}
function reset(){
  S.audience=S.goal=S.depth=S.result=null;S.state="idle";goalInput.value="";
  document.querySelectorAll(".mopt").forEach(b=>b.setAttribute("aria-pressed","false"));
  renderEmpty();runButton.disabled=true;runButton.textContent=copy.run;
}
document.querySelectorAll(".mopt").forEach(b=>b.addEventListener("click",()=>{
  const k=b.dataset.kind;S[k]=b.dataset.value;
  document.querySelectorAll('.mopt[data-kind="'+k+'"]').forEach(x=>x.setAttribute("aria-pressed",String(x===b)));
  S.result=null;S.state="idle";renderEmpty();
  runButton.disabled=!(S.audience&&S.goal&&S.depth&&(goalInput.value||"").trim());
}));
goalInput.addEventListener("input",()=>{S.result=null;S.state="idle";renderEmpty();runButton.disabled=!(S.audience&&S.goal&&S.depth&&(goalInput.value||"").trim())});
runButton.addEventListener("click",runRoute);
renderEmpty();runButton.disabled=true;
})();
