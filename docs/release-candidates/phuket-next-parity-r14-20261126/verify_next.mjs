// R14 owner verification: execute generated Next route handler functions and
// the exact pinned pure renderer chain in Node 24+. Not a Next build or deployment.
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createHash } from "node:crypto";
import { stripTypeScriptTypes } from "node:module";
const BASE="b76fbcf4c42104a057c80d6a6a59df9d936b039a";
const REPORT="b0922405e3741470b449e90e5e0e85681170ce6c7e1f4989161d41fe2d029e8e";
const R13="cdeb4a954aa77751b6b776419b93f4f9432d70d28d6a66f86fd4d101e21ccc69";
const sha=b=>createHash("sha256").update(b).digest("hex");
const blob=b=>createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
const need=(ok,msg)=>{if(!ok)throw Error(msg)};
const [candidate,r13,out]=process.argv.slice(2).map(x=>path.resolve(x));
need(candidate&&r13&&out,"usage: node verify_next.mjs <candidate> <R13 output> <new QA dir>");
const within=(p,root)=>p===root||p.startsWith(root+path.sep);
need(!within(out,candidate)&&!within(out,r13),"external output");
const checked=async(p,pin)=>{const b=await fs.readFile(p);need(sha(b)===pin,"SHA256 "+p);return b};
const m=JSON.parse(await checked(path.join(candidate,"NEXT_DRAFT.json"),REPORT));
const prior=JSON.parse(await checked(path.join(r13,"DRAFT_INVENTORY.json"),R13));
need(m.base===BASE&&m.scope==="NEXT_SOURCE_OVERLAY_DRAFT_ONLY"&&m.routes.length===10,"scope");
const inputs={},outputs={};
for(const [n,pin] of Object.entries(m.input_blobs)){
 const b=await fs.readFile(path.join(candidate,"inputs",n));need(blob(b)===pin,"input blob "+n);inputs[n]=b;
}
for(const [n,v] of Object.entries(m.files)){
 const b=await checked(path.join(candidate,"overlay",n),v.sha256);need(b.length===v.bytes,"length "+n);outputs[n]=b;
}
const tests={exact_input_blobs:Object.keys(inputs).length===10,exact_overlay_files:Object.keys(outputs).length===22};
const routeChecks=[];
for(const r of m.routes){
 const mod=await import(pathToFileURL(path.join(candidate,"overlay",r.handler)).href);
 const response=mod.GET();
 const b=Buffer.from(await response.arrayBuffer());
 const expected=await checked(path.join(r13,"overlay",r.static_path),prior.overlay[r.static_path].sha256);
 const local={};
 local["route_handler_exports"]=Object.keys(mod).sort().join(",")==="GET,dynamic"&&mod.dynamic==="force-static";
 local["response_status"]=response.status===200;
 local["exact_body"]=b.equals(expected)&&sha(b)===r.body_sha256;
 local["all_headers"]=Object.entries(r.headers).every(([k,v])=>response.headers.get(k)===v);
 local["noindex_and_no_store"]=response.headers.get("X-Robots-Tag")==="noindex, nofollow"&&response.headers.get("Cache-Control")==="no-store";
 const csp=response.headers.get("Content-Security-Policy")||"";
 local["restrictive_csp"]=csp.includes("default-src 'none'")&&csp.includes("connect-src 'none'")&&csp.includes("form-action 'none'")&&csp.includes("frame-ancestors 'none'")&&csp.includes("worker-src 'none'")&&!csp.includes("unsafe-inline")&&!csp.includes("unsafe-eval");
 local["no_analytics_or_hydration"]=!b.includes(Buffer.from("/_vercel/"))&&!b.includes(Buffer.from("/_next/"));
 local["deterministic_second_response"]=Buffer.from(await mod.GET().arrayBuffer()).equals(b);
 routeChecks.push({route:r.route,checks:local,pass:Object.values(local).every(Boolean)});
 console.log("ROUTE",r.route,Object.values(local).filter(Boolean).length,"/",Object.keys(local).length);
}
// Directly execute original pure renderer helpers with exact input bytes.
// Node does not implement Next's JSON import behavior; replace only that import
// in the in-memory test module with the exact verified JSON object.
const load=async(s)=>import("data:text/javascript;base64,"+Buffer.from(stripTypeScriptTypes(s,{mode:"strip"})).toString("base64"));
const original=n=>inputs["components/"+n].toString("utf8");
const {phuketUniverseMarkup}=await load(original("phuketUniverseMarkup.ts"));
const {withAgencyPilotTerms}=await load(original("phuketUniverseAgencyTerms.ts"));
const {withUniverseU3}=await load(original("phuketUniverseU3.ts"));
let housing=original("phuketHousingCatalog.ts");
const importLine='import sections from "../data/phuket_housing_r6_sections.json";';
need(housing.split(importLine).length===2,"exact JSON import boundary");
housing=housing.replace(importLine,"const sections = "+inputs["data/phuket_housing_r6_sections.json"].toString("utf8").trim()+";");
const {withHousingCatalog}=await load(housing);
const {withRentalJourney}=await import(pathToFileURL(path.join(candidate,"overlay","components/phuketRentalJourney.ts")).href);
const reject=fn=>{try{fn();return false}catch{return true}};
const section=s=>{const i=s.indexOf('id="homes"'),a=s.lastIndexOf("<section ",i),z=s.indexOf("</section>",i)+10;need(i>=0&&a>=0&&z>i,"housing section");return s.slice(a,z)};
for(const l of ["ru","en"]){
 const before=withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[l],l),l),l);
 const after=withRentalJourney(before,l),g=m.gateway[l].fragment;
 const page=l==="en"?"en/phuket-universe.html":"phuket-universe.html";
 const staticBody=(await checked(path.join(r13,"overlay",page),prior.overlay[page].sha256)).toString("utf8");
 tests[l+"_exact_housing_parity"]=section(after)===section(staticBody)&&sha(Buffer.from(section(after)))===m.gateway[l].housing_sha256;
 tests[l+"_only_gateway_changed"]=after.replace(g+"\n","")===before&&after.split(g).length===2;
 tests[l+"_empty_catalogue_preserved"]=!after.includes("data-u2-card")&&after.includes('data-u2-catalog=""');
 tests[l+"_duplicate_rejected"]=reject(()=>withRentalJourney(after,l));
 tests[l+"_missing_section_rejected"]=reject(()=>withRentalJourney(before.replace('id="homes"','id="missing"'),l));
 tests[l+"_drift_rejected"]=reject(()=>withRentalJourney(before.replace(/<p class="pu-s095">(?=[^<]*(?:агентств|agency))/, '<p class="changed">'),l));
 tests[l+"_unknown_locale_rejected"]=reject(()=>withRentalJourney(before,"xx"));
}
const comp=outputs["components/PhuketUniverse.tsx"].toString("utf8");
const prev=inputs["components/PhuketUniverse.tsx"].toString("utf8");
const old="const markup = withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale), locale);";
const replacement="const markup = withRentalJourney(withUniverseU3(withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale), locale), locale);";
tests.component_exact_wrapper=comp==='import { withRentalJourney } from "@/components/phuketRentalJourney";\n'+prev.replace(old,replacement);
tests.nine_shared_assets=Object.keys(outputs).filter(n=>n.startsWith("public/phuket-rental-assets/")).length===9;
tests.guide_css_pin=sha(outputs["public/phuket-universe.css"])==="c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287";
tests.unique_routes=new Set(m.routes.map(r=>r.route)).size===10;
tests.route_groups=m.routes.every(r=>r.route.startsWith("/en/")?r.handler.startsWith("app/(en)/en/"):r.handler.startsWith("app/(ru)/"));
const passed=Object.values(tests).filter(Boolean).length+routeChecks.reduce((n,r)=>n+Object.values(r.checks).filter(Boolean).length,0);
const total=Object.keys(tests).length+routeChecks.reduce((n,r)=>n+Object.keys(r.checks).length,0);
const report={scope:"OWNER_R14_NODE_SOURCE_PARITY_QA",created_utc:new Date().toISOString(),node:process.version,base:BASE,overlay_sha256:REPORT,checks:tests,route_checks:routeChecks,passed,total,all_pass:passed===total,release_approval:false,limitations:"Executed generated handler functions and pinned pure source chain; JSON import substituted with identical verified data in test module. Actual Next build/router, static release admission, production runtime, visual/accessibility and independent review not performed."};
await fs.mkdir(out,{recursive:false});
const raw=Buffer.from(JSON.stringify(report,null,2)+"\n");await fs.writeFile(path.join(out,"QA.json"),raw,{flag:"wx"});
console.log("RESULT",report.all_pass?"PASS":"REVISE",passed,"/",total,"FAIL",Object.keys(tests).filter(k=>!tests[k]),"SHA256",sha(raw));
process.exitCode=report.all_pass?0:1;
