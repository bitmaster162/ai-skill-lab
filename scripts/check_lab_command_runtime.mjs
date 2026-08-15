#!/usr/bin/env node
import fs from 'node:fs';import path from 'node:path';import vm from 'node:vm';import process from 'node:process';
const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const js=fs.readFileSync(path.join(root,'deploy/live/lab-command.js'),'utf8');
class E{constructor(){this.listeners={}}addEventListener(t,f){this.listeners[t]=f}trigger(t='click',event={}){if(!this.listeners[t])throw new Error(`listener ${t} missing`);return this.listeners[t].call(this,event)}}
class D extends E{constructor(){super();this.open=false;this.closeButton=new E()}showModal(){this.open=true}close(){this.open=false}querySelector(s){return s==='[data-lab-command-close]'?this.closeButton:null}}
const dialog=new D(),openA=new E(),openB=new E(),globals={};
const document={getElementById:id=>id==='lab-command'?dialog:null,querySelectorAll:s=>s==='[data-lab-command-open]'?[openA,openB]:[]};
const ctx={document,console,addEventListener:(t,f)=>globals[t]=f};ctx.window=ctx;
let checks=0;const assert=(c,m)=>{checks++;if(!c)throw new Error(m)};
try{
 vm.runInNewContext(js,ctx,{timeout:1000});
 assert(!dialog.open,'closed by default');
 openA.trigger();assert(dialog.open,'trigger opens dialog');
 dialog.close();assert(!dialog.open,'native close closes');
 let prevented=false;globals.keydown({metaKey:false,ctrlKey:true,key:'k',preventDefault(){prevented=true}});assert(dialog.open,'Ctrl+K opens');assert(prevented,'Ctrl+K prevents default');
 dialog.close();prevented=false;globals.keydown({metaKey:true,ctrlKey:false,key:'K',preventDefault(){prevented=true}});assert(dialog.open,'Meta+K opens');assert(prevented,'Meta+K prevents default');
 dialog.closeButton.trigger();assert(!dialog.open,'close control closes');
 console.log(`lab_command_runtime_checks=${checks}`);console.log('LAB_COMMAND_RUNTIME_PASS');
}catch(e){console.error('FAIL:',e?.stack||e);process.exit(1)}
