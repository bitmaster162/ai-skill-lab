(()=>{"use strict";
const C={
ru:{run:"Проверить промпт",running:"Проверяем…",secret:"Похоже, в тексте есть секрет или ключ. Удалите его: такие данные не передаются модели.",rate:"Лимит AI-проверок временно исчерпан. Попробуйте позже.",error:"Prompt Auditor сейчас недоступен. Исходный текст AI Skill Lab дополнительно не сохраняет.",copy:"Скопировать улучшенный промпт",copied:"Скопировано",copyError:"Не удалось скопировать"},
en:{run:"Audit prompt",running:"Auditing…",secret:"The text appears to contain a secret or credential. Remove it; those values are not sent to the model.",rate:"The AI audit limit is temporarily reached. Try again later.",error:"Prompt Auditor is unavailable right now. AI Skill Lab does not additionally store the original text.",copy:"Copy improved prompt",copied:"Copied",copyError:"Copy failed"}
};
for(const root of document.querySelectorAll("[data-prompt-auditor]")){
 const locale=root.dataset.locale==="en"?"en":"ru",t=C[locale];
 const input=root.querySelector("[data-pa-input]"),run=root.querySelector("[data-pa-run]"),message=root.querySelector("[data-pa-message]"),result=root.querySelector("[data-pa-result]"),score=root.querySelector("[data-pa-score]"),explanation=root.querySelector("[data-pa-explanation]"),improved=root.querySelector("[data-pa-improved]"),copy=root.querySelector("[data-pa-copy]");
 if(!input||!run||!message||!result||!score||!explanation||!improved||!copy)continue;
 const reset=()=>{run.disabled=!input.value.trim();run.textContent=t.run;message.textContent="";result.hidden=true;copy.textContent=t.copy;};
 input.addEventListener("input",reset);reset();
 run.addEventListener("click",async()=>{
  const prompt=input.value.trim();if(!prompt||run.disabled)return;
  run.disabled=true;run.textContent=t.running;message.textContent="";result.hidden=true;
  try{
   const response=await fetch("/api/route",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({mode:"prompt_audit",locale,prompt})});
   const body=await response.json().catch(()=>null);
   if(body?.status==="secret_detected"){message.textContent=t.secret;return;}
   if(response.status===429){message.textContent=t.rate;return;}
   if(response.ok&&body?.status==="ok"&&Number.isInteger(body.score)&&body.score>=1&&body.score<=10&&typeof body.improved==="string"&&typeof body.explanation==="string"){
    score.textContent=String(body.score);explanation.textContent=body.explanation;improved.textContent=body.improved;result.hidden=false;return;
   }
   message.textContent=t.error;
  }catch{message.textContent=t.error;}
  finally{run.disabled=!input.value.trim();run.textContent=t.run;}
 });
 copy.addEventListener("click",async()=>{try{await navigator.clipboard.writeText(improved.textContent||"");copy.textContent=t.copied;}catch{copy.textContent=t.copyError;}});
}
})();