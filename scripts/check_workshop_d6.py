#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]; LIVE=ROOT/'deploy/live'; errors=[]; checks=0
def req(c,m):
 global checks; checks+=1
 if not c: errors.append(m)
def read(rel): return (ROOT/rel).read_text(encoding='utf-8')
source=read('components/workshop/WorkshopStart.tsx')
for marker in ['import { LeadForm } from "@/components/LeadForm";','<LeadForm locale={locale}/>','START · APPLICATION + CONTACT','START · ЗАЯВКА + КОНТАКТ']:
 req(marker in source,f'WorkshopStart missing {marker}')
for rel,en in [('deploy/live/start.html',False),('deploy/live/en/start.html',True)]:
 t=read(rel); prefix='/en' if en else ''
 req(t.lower().count('<form')==1,f'{rel}: exactly one form')
 for marker in ['id="application-form"','name="name"','name="audience"','name="contact"','name="goal"','name="privacyConsent"','name="adultConfirmation"','name="website"','data-adult-confirmation','data-lead-message','<script src="/start-brief.js"></script>']:
  req(marker in t,f'{rel}: missing {marker}')
 req(f'name="locale" value="{"en" if en else "ru"}"' in t,f'{rel}: locale')
 req(f'name="sourcePath" value="{prefix}/start"' in t,f'{rel}: sourcePath')
 req('action=' not in t.lower(),f'{rel}: native action forbidden')
 for url in ['https://t.me/BiTFormer','mailto:robert@aiskillab.work','https://wa.me/66649701204','https://line.me/ti/p/~iwf555']:
  req(url in t,f'{rel}: direct fallback {url}')
brief=read('deploy/live/start-brief.js')
req(brief.count('fetch("/api/lead"')==1,'exact one same-origin fetch')
for marker in ['new FormData(form)','"Content-Type":"application/json"','data-adult-confirmation']:
 req(marker in brief,f'start runtime missing {marker}')
for bad in ['https://ai-skill-lab-ingress','XMLHttpRequest','localStorage','sessionStorage','document.cookie','sendBeacon(','WebSocket(']: req(bad not in brief,f'start runtime forbidden {bad}')
obj=json.loads(read('deploy/live/vercel.json')); rew=obj.get('rewrites',[])
req(rew==[{'source':'/api/lead','destination':'https://ai-skill-lab-ingress.vercel.app/api/lead'}],'exact /api/lead rewrite')
root=next((x for x in obj.get('headers',[]) if x.get('source')=='/(.*)'),{}); hdr={x.get('key'):x.get('value') for x in root.get('headers',[])}; csp=hdr.get('Content-Security-Policy','')
req("connect-src 'self'" in csp,'CSP connect self'); req("connect-src 'none'" not in csp,'CSP old connect none removed'); req("form-action 'none'" in csp,'CSP native form submit blocked'); req('*' not in csp,'CSP wildcard forbidden')
for rel in ['deploy/live/privacy.html','deploy/live/en/privacy.html']:
 t=read(rel)
 for marker in ['Dumanyan Robert','Thailand','robert@aiskillab.work','30 days' if rel.startswith('deploy/live/en/') else '30 дней','/api/lead']:
  req(marker in t,f'{rel}: privacy marker {marker}')
readme=read('README.md')
for marker in ['current public static release exposes two deliberate contact paths','First-party application form (current public mode)','same-origin `/api/lead`','NEXT_PUBLIC_LEAD_FORM_ENABLED=true` remains an ENV-bound Next-runtime capability']:
 req(marker in readme,f'README marker {marker}')
req('current public routes are contact-only' not in readme,'stale current contact-only README')
manifest=json.loads(read('deploy/live/_release.json')); req(manifest.get('schema')=='ai-skill-lab.static-release.v1','manifest schema'); req(manifest.get('release_id') in {'R101B_D6_PUBLIC_FORM','R102_D7_CUSTOM_DOMAIN_CANONICAL'},'D6-or-newer release id'); req(manifest.get('file_count')==62,'62 release files')
actual={p.relative_to(LIVE).as_posix():(len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest()) for p in LIVE.rglob('*') if p.is_file() and p.name!='_release.json'}; listed={x['path']:(x['size'],x['sha256']) for x in manifest.get('files',[])}; req(actual==listed,'manifest exact map'); aggregate=''.join(f'{p}\t{s}\t{h}\n' for p,(s,h) in sorted(actual.items())).encode(); req(hashlib.sha256(aggregate).hexdigest()==manifest.get('payload_sha256'),'manifest payload digest')
workflow=read('.github/workflows/static-qa.yml'); preflight=read('scripts/preflight_release.py')
for target in ['python scripts/check_workshop_d6.py','node scripts/check_public_form_runtime.mjs']:
 req(workflow.count(target)==1,f'workflow once {target}'); req(preflight.count(target.split(' ',1)[1])==1,f'preflight once {target}')
print(f'workshop_d6_checks={checks} files={manifest.get("file_count")} forms=2 rewrite={len(rew)}')
if errors:
 print('WORKSHOP_D6_FAIL'); [print('FAIL:',e) for e in errors]; sys.exit(1)
print('WORKSHOP_D6_PUBLIC_FORM_PASS')
