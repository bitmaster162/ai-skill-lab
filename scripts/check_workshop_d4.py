#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
ROUTES=['parents','curriculum','phuket','studio','build','matcher','challenge','proof','projects']
TARGET=[r+'.html' for r in ROUTES]+['en/'+r+'.html' for r in ROUTES]
def source_path(rel):
 grouped=(ROOT/'app'/'(ru)'/'layout.tsx').exists() and (ROOT/'app'/'(en)'/'layout.tsx').exists()
 if not grouped or not rel.startswith('app/') or not rel.endswith('page.tsx'):return ROOT/rel
 if rel.startswith('app/en/'):return ROOT/('app/(en)/en/'+rel.removeprefix('app/en/'))
 return ROOT/('app/(ru)/'+rel.removeprefix('app/'))
PROTECTED={
'data/commercial_facts.json':'f747296d269fd57940e24a22e7d08f988ede5e43460549afdb39e3ef5857fc77','README.md':'10c11d027870ef87f8a384409207ad8c928c08e168401e35e467637115d52d55','app/sitemap.ts':'612cf6960059a719cfba459c54bbd54fab38711bca3f43875edc8a42ff43509d','deploy/live/sitemap.xml':'13bd4157b2ec5b88ae4f1fb2c361a79614a0c10bf4cc2008c9bd056cd4ff75fe','deploy/live/llms.txt':'b581164e977efe097589024dec3ff95265835b0ae8df216e3dd7494c62b3e1f4','deploy/live/robots.txt':'e4b9d3404c59d087f4cfbcc147771ffbc2d9cdfa9a457937c3cbeaff87ec418c','deploy/live/vercel.json':'b3384aa20e38e505f0a210289227f83a658055af6a8373a889c5bec4f1430dcc','deploy/live/lab-command.js':'16835b5e85db24ef8f97eb2efa2b408221c725bd9334dee940723e3d816a7702','deploy/live/project-filter.js':'9ffbc90afc98556eb1539629ede2876362e2a00f2b84fe20df315fc09997dc28',
'components/ProgramMatcher.tsx':'28ad6aa4f8f9c662a2da491327eca3ca5eff95a539c0916509d0ad4f6b2561d2','components/SystemChallenge.tsx':'953826dad2ffe1ddfe16887d84aec19cd1dd24521a2a1b03592d7741a92de2b4','components/ProofLab.tsx':'ed01fbf773b423f26afe20ba4358fc1991be8968b84c756bb5203f6399169469','components/BriefCompiler.tsx':'156478fa6e9b38af1b2df7b97f460cbeaedb06e28215d7da03d9849db52da89d','components/ProjectStudio.tsx':'68b3fb0d29b584470046e7d742ef6a71f3089f85f5a424fc747c4df30d1bb8b1','components/SkillGraph.tsx':'9145c854d743820752e1b423a2e4f485966c974c0f2e9756f0e6ace32cbf953f','components/Header.tsx':'589c9e9223162fe1f280fb3f49c9a5bf18eca74279de3607f8398d1371fcfec6','components/Footer.tsx':'1f544c0ca63e2b0e1b2309761f9edb38fd292c747279bc8cd5f16f5988a9bb35','components/LabCommand.tsx':'0f9cccaea8dd1d8a1fb2be28aa125f66ec97fe49f83f641fa898afad878ac57a','components/workshop/WorkshopShell.tsx':'24a9fa79c55d5ebfcce38d2e3c16e6aab566fcfc214a773747e5230d1a79c61c'}
def require(c,m):
 global checks;checks+=1
 if not c:errors.append(m)
def read(rel):return source_path(rel).read_text(encoding='utf-8')
def sha(rel):return hashlib.sha256(source_path(rel).read_bytes()).hexdigest()
manifest=json.loads(read('deploy/live/_release.json'));release=manifest.get('release_id')
R102_PROTECTED_OVERRIDES={
'README.md':'53e1deb7042b138a1f8548f41ef4e8005d8f2c557f8b1087d097634072737bd7',
'deploy/live/sitemap.xml':'81f4f83bce0b84ac79e4c7f0a8913c2b0f6a532d057771a3b802f46c0c2a2486',
'deploy/live/llms.txt':'dfb1f672dd46713ae7e9fd696223a57042dc56eaee0774be3a0323c75fa28042',
'deploy/live/robots.txt':'332cbcca130fa5d82115641450e6b05b939f5a02243a141c7795281b5286af88',
'deploy/live/vercel.json':'fb878a7891f9d5a8d60223ac6ff72a7a3977fafacafa977a32ffc73b4057b19d',
}
R103_PROTECTED_OVERRIDES={
'README.md':'da13c9fe649f2a2f6b9a4a31d178c2d77f0c5c0f34c79bfb6113152cceaf9f0f',
'deploy/live/vercel.json':'96c9a11a515a00ae45ff61baa88ac7dd51291b3aaf058166a6ea8a0ec2736919',
}
R109D_PROTECTED_OVERRIDES={
'deploy/live/vercel.json':'9f8fcc3e5970b44f1fdb0aadfaad31fbf0109624f176b3fbcd9b57bb02e2a6c3',
}
R109F_PROTECTED_OVERRIDES={
'deploy/live/vercel.json':'c65f4ad6c49ee7e40b7f2eff9fcb96cfb69893222e179148218e408df260e0ac',
}
R110C_PROTECTED_OVERRIDES={
'deploy/live/vercel.json':'0cc0517ab4581253c944148a5f6573353ed9159db030fa864fdaee408aca2316',
}
R111B_PROTECTED_OVERRIDES={
'components/workshop/WorkshopShell.tsx':'ec60729cf919f2a343089db39d7e60385e7531c07dca2ebfa87af0c81e63b04c',
}
R111D_PROTECTED_OVERRIDES={
'app/sitemap.ts':'05d7359e632e82c93fdc4aa45aba452a02f665508e061a74d45b45a81127322b',
'deploy/live/sitemap.xml':'094adc77931971aaacf7fea64fb6d04f5220b11b5b38762a55d9656af60ec9cf',
}
R112_PROTECTED_OVERRIDES={
'components/LabCommand.tsx':'df86be0e2d04607b556e3295d3c3a38d46f58f8afae5a78025ba086188b21fb0',
'deploy/live/lab-command.js':'b2fd0fb60a8801e25b032c98c6add5137d12cfc73f24b70a32e407a6c08357c1',
}
R117_PROTECTED_OVERRIDES={
'components/ProgramMatcher.tsx':'6dd5749560e13dcb32847117435f1f9c07f2212373f7494fb1e869b0f0a9c947',
}
R121_PROTECTED_OVERRIDES={
'app/sitemap.ts':'4a38a7f87e2c81194b24467878903fc83a33521db313902c222bc53802cf52c3',
'deploy/live/sitemap.xml':'c6090e1980b6dc31b71eff57013ee67dec109089ba71859e3b83e8f30bb9f214',
}
R142_PROTECTED_OVERRIDES={
'app/sitemap.ts':'2f175bab35aeca4d997b4c5d7ff64e6002355f9bef3c0b5dc111ed22ff9c69df',
'deploy/live/sitemap.xml':'b32fa651933b895f43627be9dd9f83a39b1f118642b7ed92bbb700eaf74d1c6a',
'components/workshop/WorkshopShell.tsx':'74b1f9d11cec16ac91080152294123823ddb08b5d249c166dd2055d0685d4c02',
}
R140_SOURCE_ONLY_PROTECTED_OVERRIDES={
'README.md':'96b922598c14e0ed3ae0c4e38c51d77b3657320e8a11a9c59f968a274bb54a42',
}
protected=dict(PROTECTED)
if release in {'R102_D7_CUSTOM_DOMAIN_CANONICAL','R103_D8_LEGACY_PUBLIC_HOST_REDIRECT','R109A_CRITICAL_VISUAL_FIX','R109A_REVIEW_REPAIR','R109D_404_LEGACY_HOST','R109B_TRUTH_FORM_ALIGNMENT','R109E_GLYPH_SPACING_VISUAL','R109F_STRUCTURED_DATA','R110A_OPERATOR_LEAD_INBOX','R110B_LEAD_TELEGRAM_NOTIFICATION','R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R102_PROTECTED_OVERRIDES)
if release in {'R103_D8_LEGACY_PUBLIC_HOST_REDIRECT','R109A_CRITICAL_VISUAL_FIX','R109A_REVIEW_REPAIR','R109D_404_LEGACY_HOST','R109B_TRUTH_FORM_ALIGNMENT','R109E_GLYPH_SPACING_VISUAL','R109F_STRUCTURED_DATA','R110A_OPERATOR_LEAD_INBOX','R110B_LEAD_TELEGRAM_NOTIFICATION','R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R103_PROTECTED_OVERRIDES)
if release in {'R109D_404_LEGACY_HOST','R109B_TRUTH_FORM_ALIGNMENT','R109E_GLYPH_SPACING_VISUAL','R109F_STRUCTURED_DATA','R110A_OPERATOR_LEAD_INBOX','R110B_LEAD_TELEGRAM_NOTIFICATION','R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R109D_PROTECTED_OVERRIDES)
if release in {'R109F_STRUCTURED_DATA','R110A_OPERATOR_LEAD_INBOX','R110B_LEAD_TELEGRAM_NOTIFICATION','R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R109F_PROTECTED_OVERRIDES)
if release in {'R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R110C_PROTECTED_OVERRIDES)
if release in {'R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R111B_PROTECTED_OVERRIDES)
if release in {'R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R111D_PROTECTED_OVERRIDES)
if release in {'R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R112_PROTECTED_OVERRIDES)
if release in {'R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R117_PROTECTED_OVERRIDES)
if release in {'R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:protected.update(R121_PROTECTED_OVERRIDES)
protected.update(R140_SOURCE_ONLY_PROTECTED_OVERRIDES)
if release == 'R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH':protected.update(R142_PROTECTED_OVERRIDES)
for rel,digest in protected.items():require(sha(rel)==digest,f'protected byte drift {rel}')
for locale in ('ru','en'):
 en=locale=='en'; prefix='en/' if en else ''
 for route in ROUTES:
  rel=f'app/{prefix}{route}/page.tsx'; t=read(rel); wrapper='WorkshopEditorial' if route in {'parents','phuket','studio','build'} else 'WorkshopInteractive'
  require(f'<{wrapper} locale="{locale}" alternateHref="' in t,f'{rel}: Workshop wrapper')
  require('Header' not in t and 'Footer' not in t,f'{rel}: legacy shell import/mount')
  require('<main id="main"' in t,f'{rel}: main preserved')
for rel in TARGET:
 t=read('deploy/live/'+rel); en=rel.startswith('en/'); route=rel.split('/')[-1][:-5]; alt='/'+route if en else '/en/'+route; start='/en/start' if en else '/start'
 require('<header class="workshopHeader">' in t and '<header class="nav">' not in t,f'{rel}: static Workshop shell')
 require('<link rel="stylesheet" href="/workshop.css">' in t and 'href="/style.css"' not in t,f'{rel}: static Workshop stylesheet')
 require(t.count('data-lab-command-open')==1 and t.count('src="/lab-command.js"')==1,f'{rel}: LAB runtime')
 require(f'href="{alt}"' in t and f'href="{start}' in t,f'{rel}: alternate/start')
 require(t.count('<h1')==1,f'{rel}: one h1')
 require('fonts.googleapis.com' not in t and 'fonts.gstatic.com' not in t and '[response time]' not in t and '[срок ответа]' not in t,f'{rel}: forbidden design residue')
semantic={
'parents.html':['FOR PARENTS · 8–18','Сам формулирует цель','ChatGPT и возраст','Family Concierge','https://help.openai.com/en/articles/8313401','/safety'],
'en/parents.html':['FOR PARENTS · 8–18','Defines the goal','ChatGPT and age','Family Concierge','https://help.openai.com/en/articles/8313401','/en/safety'],
'phuket.html':['PHUKET · ONLINE WORLDWIDE','по предварительной договорённости','Работа из любой страны'],
'en/phuket.html':['PHUKET · ONLINE WORLDWIDE','prior arrangement','regardless of country'],
'studio.html':['AI STUDIO / BUILD WITH US','CUSTOM SCOPE','Ship / Revise / Stop','гарантированного ROI'],
'en/studio.html':['AI STUDIO / BUILD WITH US','CUSTOM SCOPE','Ship / Revise / Stop','guaranteed ROI'],
'build.html':['BUILD STORY / OPEN PROVENANCE','/_release.json','Failure log','BLOCKED'],
'en/build.html':['BUILD STORY / OPEN PROVENANCE','/_release.json','Failure log','BLOCKED']}
for rel,tokens in semantic.items():
 text=read('deploy/live/'+rel)
 for token in tokens:require(token.lower() in text.lower(),f'{rel}: semantic {token}')
interactive={
'curriculum.html':['data-skill-graph','data-skill-key="adult"','INDEPENDENT','GOVERNED'],'en/curriculum.html':['data-skill-graph','data-skill-key="adult"','INDEPENDENT','GOVERNED'],
'matcher.html':['data-kind="audience"','data-kind="goal"','data-kind="depth"','matcher-output'],'en/matcher.html':['data-kind="audience"','data-kind="goal"','data-kind="depth"','matcher-output'],
'challenge.html':['data-system-challenge','data-challenge-key','DEFINE','SHIP'],'en/challenge.html':['data-system-challenge','data-challenge-key','DEFINE','SHIP'],
'proof.html':['data-proof-key','data-brief-compiler','id="brief-compiler"','HUMAN GATE:'],'en/proof.html':['data-proof-key','data-brief-compiler','id="brief-compiler"','HUMAN GATE:'],
'projects.html':['data-project-studio','data-project-filter','data-project-tags','/project-filter.js'],'en/projects.html':['data-project-studio','data-project-filter','data-project-tags','/project-filter.js']}
for rel,tokens in interactive.items():
 text=read('deploy/live/'+rel)
 for token in tokens:require(token in text,f'{rel}: interactive {token}')
if release in {'R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:
 brand_path='M12 1 23 23H1Zm-1 9h2L16 14H8Zm-1.5 6h5L19 23H5Z'
 source_shell=read('components/workshop/WorkshopShell.tsx')
 source_mark=f'<span className={{styles.mark}} aria-hidden="true"><svg viewBox="0 0 24 24"><path fillRule="evenodd" d="{brand_path}" /></svg></span><span>AI SKILL LAB</span>'
 require(source_shell.count(source_mark)==1,'R111B source mark exact once')
 require('aria-hidden="true">A</span><span>AI SKILL LAB' not in source_shell,'R111B source legacy A absent')
 source_css='.mark{display:flex;width:30px;height:30px;color:var(--acid);flex:none}.mark svg{display:block;width:100%;height:100%;fill:currentColor}'
 require(source_css in read('components/workshop/WorkshopShell.module.css'),'R111B source mark CSS')
 static_mark=f'<span class="workshopMark" aria-hidden="true"><svg viewBox="0 0 24 24"><path fill-rule="evenodd" d="{brand_path}"/></svg></span><span>AI SKILL LAB</span>'
 brand_html=list(LIVE.rglob('*.html'))
 require(len(brand_html)==47,'R111B brand 47 HTML')
 for hp in brand_html:
  ht=hp.read_text(encoding='utf-8'); require(ht.count(static_mark)==1,f'R111B static mark {hp.relative_to(LIVE)}'); require('aria-hidden="true">A</span><span>AI SKILL LAB' not in ht,f'R111B legacy A {hp.relative_to(LIVE)}')
 static_css='.workshopMark{display:inline-flex;width:26px;height:26px;margin-right:10px;flex:none;color:var(--acid)}.workshopMark svg{display:block;width:100%;height:100%;fill:currentColor}'
 require(static_css in read('deploy/live/workshop.css'),'R111B static mark CSS')
 fav='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><style>path{fill:#b9ff3f}@media(prefers-color-scheme:light){path{fill:#0b0d10}}</style><path fill-rule="evenodd" d="'+brand_path+'"/></svg>'+chr(10)
 require(not (ROOT/'app/icon.svg').exists(),'R126 file-based source favicon absent')
 require(read('public/favicon.svg')==fav,'R126 source favicon exact')
 require(read('deploy/live/favicon.svg')==fav,'R111B static favicon exact')
all_html=list(LIVE.rglob('*.html'));public=[p for p in all_html if p.name!='404.html']
require(len(all_html)==47,'47 static HTML files')
workshop=sum('<header class="workshopHeader">' in p.read_text(encoding='utf-8') for p in public);legacy=sum('<header class="nav">' in p.read_text(encoding='utf-8') for p in public)
require(manifest.get('schema')=='ai-skill-lab.static-release.v1','release schema');states={'R99_D4':(36,10),'R100_D5':(46,0),'R101B_D6_PUBLIC_FORM':(46,0),'R102_D7_CUSTOM_DOMAIN_CANONICAL':(46,0),'R103_D8_LEGACY_PUBLIC_HOST_REDIRECT':(46,0),'R109A_CRITICAL_VISUAL_FIX':(46,0),'R109A_REVIEW_REPAIR':(46,0),'R109D_404_LEGACY_HOST':(46,0),'R109B_TRUTH_FORM_ALIGNMENT':(46,0),'R109E_GLYPH_SPACING_VISUAL':(46,0),'R109F_STRUCTURED_DATA':(46,0),'R110A_OPERATOR_LEAD_INBOX':(46,0),'R110B_LEAD_TELEGRAM_NOTIFICATION':(46,0),'R110C_BRAND_LOGO':(46,0),'R111A_NOSCRIPT_FORM_FALLBACK':(46,0),'R111B_BRAND_MARK_FAVICON':(46,0),'R111C_RU_TITLE_LOCALIZATION':(46,0),'R111D_SITEMAP_LASTMOD':(46,0),'R112_PLATFORM_SHORTCUT_TITLES':(46,0),'R114_BRAND_TOUCH_TARGET':(46,0),'R115_WORKSHOP_TYPOGRAPHY':(46,0),'R116_MONETARY_TYPOGRAPHY':(46,0),'R117_GLYPH_FALLBACK':(46,0),'R121_SITEMAP_LASTMOD_REFRESH':(46,0),'R130_STATIC_H2_OVERFLOW_GUARD':(46,0),'R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH':(46,0)};require(release in states,f'unsupported release state {release!r}')
if release in states:
 expected_workshop,expected_legacy=states[release];require(workshop==expected_workshop,f'Workshop pages {workshop} != {expected_workshop} for {release}');require(legacy==expected_legacy,f'legacy pages {legacy} != {expected_legacy} for {release}')
expected_files=61 if release in {'R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'} else 59 if release in {'R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'} else 58;require(manifest.get('file_count')==expected_files,f'{expected_files} release files')
actual={p.relative_to(LIVE).as_posix():(len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest()) for p in LIVE.rglob('*') if p.is_file() and p.name!='_release.json'}
listed={x['path']:(x['size'],x['sha256']) for x in manifest.get('files',[])};require(actual==listed,'manifest exact file bytes');payload=sum(x[0] for x in actual.values());payload_limit=618*1024 if release=='R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH' else 608*1024 if release in {'R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD'} else 528384;require(payload<=payload_limit,f'payload {payload} > {payload_limit}')
require(len({('/' if p.name=='index.html' else '/en' if p.relative_to(LIVE).as_posix()=='en.html' else '/'+p.relative_to(LIVE).as_posix()[:-5]) for p in public})==46,'46 public routes')
css=read('deploy/live/workshop.css');guard='.labDialog :is(p,.proofConsoleTop,.proofConsoleFoot){display:flex;gap:8px;flex-wrap:wrap}.labDialog :is(a,button){padding:13px}'
require(css.count(guard)==1,'C1 Lab spacing guard exactly once');require('@import' not in css and 'fonts.googleapis.com' not in css and 'fonts.gstatic.com' not in css,'Workshop CSS self-contained')
r109e_guards=['.workshopFooter>div{display:flex;flex-direction:column}','.workshopFooter nav{display:flex;flex-wrap:wrap;gap:16px}','.workshopFooter{border-bottom:0;border-top:1px solid var(--b)}','.bandSteps{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--b)}','.heroActions,.sectionActions{display:flex;flex-wrap:wrap;gap:10px}','.proofFlow article>span,.proofFlow article>b{display:block}','.projectStudioStatus>strong,.projectStudioStatus>span{display:block}']
if release in {'R109E_GLYPH_SPACING_VISUAL','R109F_STRUCTURED_DATA','R110A_OPERATOR_LEAD_INBOX','R110B_LEAD_TELEGRAM_NOTIFICATION','R110C_BRAND_LOGO','R111A_NOSCRIPT_FORM_FALLBACK','R111B_BRAND_MARK_FAVICON','R111C_RU_TITLE_LOCALIZATION','R111D_SITEMAP_LASTMOD','R112_PLATFORM_SHORTCUT_TITLES','R114_BRAND_TOUCH_TARGET','R115_WORKSHOP_TYPOGRAPHY','R116_MONETARY_TYPOGRAPHY','R117_GLYPH_FALLBACK','R121_SITEMAP_LASTMOD_REFRESH','R130_STATIC_H2_OVERFLOW_GUARD','R142_A9_A11_FOOTER_TOOLCHAIN_PROOF_TRUTH'}:
 for visual_guard in r109e_guards:require(visual_guard in css,f'R109E visual guard {visual_guard}')
workflow=read('.github/workflows/static-qa.yml');preflight=read('scripts/preflight_release.py');require(workflow.count('python scripts/check_workshop_d4.py')==1,'workflow D4 exactly once');require(preflight.count('scripts/check_workshop_d4.py')==1,'preflight D4 exactly once')
print(f'workshop_d4_checks={checks} target_pages=18 workshop_pages={workshop} legacy_pages={legacy} routes=46 html=47 files={expected_files} payload_bytes={payload} headroom={payload_limit-payload}')
if errors:
 print('WORKSHOP_D4_FAIL');[print('FAIL:',e) for e in errors];sys.exit(1)
print('WORKSHOP_D4_PASS')
