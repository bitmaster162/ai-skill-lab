#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import {fileURLToPath} from "node:url";

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const code=fs.readFileSync(path.join(ROOT,"deploy/live/safety-quiz.js"),"utf8");
const correct=["a","a","a","a","b"];

class Button{
  addEventListener(type,fn){if(type!=="click")throw new Error("unexpected event "+type);this.fn=fn}
  click(){if(!this.fn)throw new Error("click handler missing");this.fn()}
}
class Question{
  constructor(answer,index){this.answer=answer;this.dataset={correct:correct[index]}}
  querySelector(sel){
    if(sel!=='input[type="radio"]:checked')throw new Error("unexpected selector "+sel);
    return this.answer?{value:this.answer}:null;
  }
}
class Quiz{
  constructor(locale,answers){
    this.dataset={locale};
    this.questions=answers.map((x,i)=>new Question(x,i));
    this.result={textContent:""};
    this.button=new Button();
  }
  querySelectorAll(sel){if(sel!=="[data-safety-question]")throw new Error("unexpected all "+sel);return this.questions}
  querySelector(sel){
    if(sel==="[data-safety-result]")return this.result;
    if(sel==="[data-safety-check]")return this.button;
    throw new Error("unexpected selector "+sel);
  }
}
function run(locale,answers){
  const quiz=new Quiz(locale,answers);
  const document={querySelectorAll(sel){if(sel!=="[data-safety-quiz]")throw new Error("unexpected root "+sel);return[quiz]}};
  const context={document};
  vm.runInNewContext(code,context,{filename:"safety-quiz.js",timeout:1000});
  quiz.button.click();
  return quiz;
}
let checks=0;
const all=run("ru",["a","a","a","a","b"]);
if(all.result.textContent!=="5/5 ответов совпадают с текущими правилами этой страницы.")throw new Error("RU all-correct result");checks++;
if(all.questions.some(q=>q.dataset.state!=="match"))throw new Error("RU all-correct state");checks+=5;

const one=run("en",["a","a","a","b","b"]);
if(one.result.textContent!=="4/5 answers match. Review the highlighted rules on this page.")throw new Error("EN review result");checks++;
if(one.questions[3].dataset.state!=="review")throw new Error("EN wrong answer not marked review");checks++;
if(one.questions.filter(q=>q.dataset.state==="match").length!==4)throw new Error("EN match count");checks++;

const incomplete=run("ru",["a","a","a","a",null]);
if(incomplete.result.textContent!=="Ответьте на все пять вопросов перед проверкой.")throw new Error("RU incomplete result");checks++;
if(incomplete.questions[4].dataset.state!=="missing")throw new Error("RU missing state");checks++;

console.log(`A7_SAFETY_QUIZ_RUNTIME_CHECKS=${checks} cases=3 network_calls=0 storage_writes=0`);
console.log("A7_SAFETY_QUIZ_RUNTIME_PASS");
