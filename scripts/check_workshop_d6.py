#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]; LIVE=ROOT/'deploy/live'; errors=[]; checks=0
def source_path(rel):
 grouped=(ROOT/'app'/'(ru)'/'layout.tsx').exists() and (ROOT/'app'/'(en)'/'layout.tsx').exists()
 if not grouped or not rel.startswith('app/') or not rel.endswith('page.tsx'):return ROOT/rel
 if rel.startswith('app/en/'):return ROOT/('app/(en)/en/'+rel.removeprefix('app/en/'))
 return ROOT/('app/(ru)/'+rel.removeprefix('app/'))
def req(c,m):
 global checks; checks+=1
 if not c: errors.append(m)
def read(rel): return source_path(rel).read_text(encoding='utf-8')
source=read('components/workshop/WorkshopStart.tsx')
for marker in ['import { LeadForm } from "@/components/LeadForm";','<LeadForm locale={locale}/>','START · APPLICATION + CONTACT','START · ЗАЯВКА + КОНТАКТ']:
 req(marker in source,f'WorkshopStart missing {marker}')
for marker in ['The application form requires JavaScript. Contact us directly instead — Telegram, WhatsApp, LINE or email, all listed below on this page.','Форма заявки работает только с включённым JavaScript. Напишите напрямую — Telegram, WhatsApp, LINE или email, контакты ниже на этой странице.']:
 req(marker in read('components/LeadForm.tsx'),f'LeadForm missing no-JS fallback {marker}')
for rel,en in [('deploy/live/start.html',False),('deploy/live/en/start.html',True)]:
 t=read(rel); prefix='/en' if en else ''
 req(t.lower().count('<form')==1,f'{rel}: exactly one form')
 for marker in ['id="application-form"','name="name"','name="audience"','name="contact"','name="goal"','name="privacyConsent"','name="adultConfirmation"','name="website"','data-adult-confirmation','data-lead-message','<script src="/start-brief.js"></script>']:
  req(marker in t,f'{rel}: missing {marker}')
 req(f'name="locale" value="{"en" if en else "ru"}"' in t,f'{rel}: locale')
 req(f'name="sourcePath" value="{prefix}/start"' in t,f'{rel}: sourcePath')
 expected_notice='The application form requires JavaScript. Contact us directly instead — Telegram, WhatsApp, LINE or email, all listed below on this page.' if en else 'Форма заявки работает только с включённым JavaScript. Напишите напрямую — Telegram, WhatsApp, LINE или email, контакты ниже на этой странице.'
 req(t.count('<noscript><p class="formNote">'+expected_notice+'</p></noscript>')==1,f'{rel}: exact no-JS application fallback')
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
redirects=obj.get('redirects',[]); expected_redirects=[{'source':'/:path*','has':[{'type':'host','value':'ai-skill-lab.vercel.app'}],'destination':'https://aiskillab.work/:path*','permanent':True}]
req(redirects==expected_redirects,'exact legacy public host redirect')
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
# R109B: public truth must match the enabled first-party form.
for rel,marker in [('app/faq/page.tsx','/start доступна собственная форма заявки'),('deploy/live/faq.html','/start доступна собственная форма заявки'),('app/en/faq/page.tsx','/en/start includes a first-party application form'),('deploy/live/en/faq.html','/en/start includes a first-party application form')]:
 t=read(rel); req(marker in t,f'{rel}: current form truth'); req('contact-only' not in t,f'{rel}: stale contact-only claim')
for rel,marker in [('deploy/live/terms.html','На сайте доступна форма заявки'),('deploy/live/en/terms.html','The website provides an application form')]:
 t=read(rel); req(marker in t,f'{rel}: application-form truth'); req('contact-only' not in t,f'{rel}: stale contact-only claim')
for rel,marker,stale in [('app/safety/page.tsx','Публичная форма заявки использует контакт взрослого','нет формы'),('deploy/live/safety.html','Публичная форма заявки использует контакт взрослого','На текущем сайте нет формы'),('app/en/safety/page.tsx','The public application form uses an adult contact','no form asking'),('deploy/live/en/safety.html','The public application form uses an adult contact','The current website has no form')]:
 t=read(rel); req(marker in t,f'{rel}: adult-contact form truth'); req(stale not in t,f'{rel}: stale no-form claim')
manifest=json.loads(read('deploy/live/_release.json')); req(manifest.get('schema')=='ai-skill-lab.static-release.v1','manifest schema'); req(manifest.get('release_id') in {'R101B_D6_PUBLIC_FORM','R102_D7_CUSTOM_DOMAIN_CANONICAL','R103_D8_LEGACY_PUBLIC_HOST_REDIRECT','R109A_CRITICAL_VISUAL_FIX','R109A_REVIEW_REPAIR','R109D_404_LEGACY_HOST','R109B_TRUTH_FORM_ALIGNMENT','R109E_GLYPH_SPACING_VISUAL','R109F_STRUCTURED_DATA','R110A_OPERATOR_LEAD_INBOX','R110B_LEAD_TELEGRAM_NOTIFICATION','R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH'} ,'D6-or-newer release id'); expected_files=61 if manifest.get('release_id') in {'R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH'} else 59 if manifest.get('release_id') in {'R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH'} else 58; req(manifest.get('file_count')==expected_files,f'{expected_files} release files')
actual={p.relative_to(LIVE).as_posix():(len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest()) for p in LIVE.rglob('*') if p.is_file() and p.name!='_release.json'}; listed={x['path']:(x['size'],x['sha256']) for x in manifest.get('files',[])}; req(actual==listed,'manifest exact map'); aggregate=''.join(f'{p}\t{s}\t{h}\n' for p,(s,h) in sorted(actual.items())).encode(); req(hashlib.sha256(aggregate).hexdigest()==manifest.get('payload_sha256'),'manifest payload digest')
workflow=read('.github/workflows/static-qa.yml'); preflight=read('scripts/preflight_release.py')
for target in ['python scripts/check_workshop_d6.py','node scripts/check_public_form_runtime.mjs']:
 req(workflow.count(target)==1,f'workflow once {target}'); req(preflight.count(target.split(' ',1)[1])==1,f'preflight once {target}')
print(f'workshop_d6_checks={checks} files={manifest.get("file_count")} forms=2 rewrite={len(rew)}')
if errors:
 print('WORKSHOP_D6_FAIL'); [print('FAIL:',e) for e in errors]; sys.exit(1)
print('WORKSHOP_D6_PUBLIC_FORM_PASS')
