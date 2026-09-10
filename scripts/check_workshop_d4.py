#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
ROUTES=['parents','curriculum','phuket','studio','build','matcher','challenge','proof','projects']
TARGET=[r+'.html' for r in ROUTES]+['en/'+r+'.html' for r in ROUTES]
PROTECTED={
'data/commercial_facts.json':'f747296d269fd57940e24a22e7d08f988ede5e43460549afdb39e3ef5857fc77','README.md':'10c11d027870ef87f8a384409207ad8c928c08e168401e35e467637115d52d55','app/sitemap.ts':'612cf6960059a719cfba459c54bbd54fab38711bca3f43875edc8a42ff43509d','deploy/live/sitemap.xml':'13bd4157b2ec5b88ae4f1fb2c361a79614a0c10bf4cc2008c9bd056cd4ff75fe','deploy/live/llms.txt':'b581164e977efe097589024dec3ff95265835b0ae8df216e3dd7494c62b3e1f4','deploy/live/robots.txt':'e4b9d3404c59d087f4cfbcc147771ffbc2d9cdfa9a457937c3cbeaff87ec418c','deploy/live/vercel.json':'b3384aa20e38e505f0a210289227f83a658055af6a8373a889c5bec4f1430dcc','deploy/live/lab-command.js':'16835b5e85db24ef8f97eb2efa2b408221c725bd9334dee940723e3d816a7702','deploy/live/project-filter.js':'9ffbc90afc98556eb1539629ede2876362e2a00f2b84fe20df315fc09997dc28',
'components/ProgramMatcher.tsx':'28ad6aa4f8f9c662a2da491327eca3ca5eff95a539c0916509d0ad4f6b2561d2','components/SystemChallenge.tsx':'953826dad2ffe1ddfe16887d84aec19cd1dd24521a2a1b03592d7741a92de2b4','components/ProofLab.tsx':'ed01fbf773b423f26afe20ba4358fc1991be8968b84c756bb5203f6399169469','components/BriefCompiler.tsx':'156478fa6e9b38af1b2df7b97f460cbeaedb06e28215d7da03d9849db52da89d','components/ProjectStudio.tsx':'68b3fb0d29b584470046e7d742ef6a71f3089f85f5a424fc747c4df30d1bb8b1','components/SkillGraph.tsx':'9145c854d743820752e1b423a2e4f485966c974c0f2e9756f0e6ace32cbf953f','components/Header.tsx':'589c9e9223162fe1f280fb3f49c9a5bf18eca74279de3607f8398d1371fcfec6','components/Footer.tsx':'1f544c0ca63e2b0e1b2309761f9edb38fd292c747279bc8cd5f16f5988a9bb35','components/LabCommand.tsx':'0f9cccaea8dd1d8a1fb2be28aa125f66ec97fe49f83f641fa898afad878ac57a','components/workshop/WorkshopShell.tsx':'24a9fa79c55d5ebfcce38d2e3c16e6aab566fcfc214a773747e5230d1a79c61c'}
def require(c,m):
 global checks;checks+=1
 if not c:errors.append(m)
def read(rel):return (ROOT/rel).read_text(encoding='utf-8')
def sha(rel):return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
manifest=json.loads(read('deploy/live/_release.json'));release=manifest.get('release_id')
R102_PROTECTED_OVERRIDES={
'README.md':'53e1deb7042b138a1f8548f41ef4e8005d8f2c557f8b1087d097634072737bd7',
'deploy/live/sitemap.xml':'81f4f83bce0b84ac79e4c7f0a8913c2b0f6a532d057771a3b802f46c0c2a2486',
'deploy/live/llms.txt':'dfb1f672dd46713ae7e9fd696223a57042dc56eaee0774be3a0323c75fa28042',
'deploy/live/robots.txt':'332cbcca130fa5d82115641450e6b05b939f5a02243a141c7795281b5286af88',
'deploy/live/vercel.json':'fb878a7891f9d5a8d60223ac6ff72a7a3977fafacafa977a32ffc73b4057b19d',
}
protected=dict(PROTECTED)
if release=='R102_D7_CUSTOM_DOMAIN_CANONICAL':protected.update(R102_PROTECTED_OVERRIDES)
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
all_html=list(LIVE.rglob('*.html'));public=[p for p in all_html if p.name!='404.html']
require(len(all_html)==47,'47 static HTML files')
workshop=sum('<header class="workshopHeader">' in p.read_text(encoding='utf-8') for p in public);legacy=sum('<header class="nav">' in p.read_text(encoding='utf-8') for p in public)
require(manifest.get('schema')=='ai-skill-lab.static-release.v1','release schema');states={'R99_D4':(36,10),'R100_D5':(46,0),'R101B_D6_PUBLIC_FORM':(46,0),'R102_D7_CUSTOM_DOMAIN_CANONICAL':(46,0)};require(release in states,f'unsupported release state {release!r}')
if release in states:
 expected_workshop,expected_legacy=states[release];require(workshop==expected_workshop,f'Workshop pages {workshop} != {expected_workshop} for {release}');require(legacy==expected_legacy,f'legacy pages {legacy} != {expected_legacy} for {release}')
require(manifest.get('file_count')==62,'62 release files')
actual={p.relative_to(LIVE).as_posix():(len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest()) for p in LIVE.rglob('*') if p.is_file() and p.name!='_release.json'}
listed={x['path']:(x['size'],x['sha256']) for x in manifest.get('files',[])};require(actual==listed,'manifest exact file bytes');payload=sum(x[0] for x in actual.values());require(payload<=524288,f'payload {payload} > 524288')
require(len({('/' if p.name=='index.html' else '/en' if p.relative_to(LIVE).as_posix()=='en.html' else '/'+p.relative_to(LIVE).as_posix()[:-5]) for p in public})==46,'46 public routes')
css=read('deploy/live/workshop.css');guard='.labDialog :is(p,.proofConsoleTop,.proofConsoleFoot){display:flex;gap:8px;flex-wrap:wrap}.labDialog :is(a,button){padding:13px}'
require(css.count(guard)==1,'C1 Lab spacing guard exactly once');require('@import' not in css and 'fonts.googleapis.com' not in css and 'fonts.gstatic.com' not in css,'Workshop CSS self-contained')
workflow=read('.github/workflows/static-qa.yml');preflight=read('scripts/preflight_release.py');require(workflow.count('python scripts/check_workshop_d4.py')==1,'workflow D4 exactly once');require(preflight.count('scripts/check_workshop_d4.py')==1,'preflight D4 exactly once')
print(f'workshop_d4_checks={checks} target_pages=18 workshop_pages={workshop} legacy_pages={legacy} routes=46 html=47 files=62 payload_bytes={payload} headroom={524288-payload}')
if errors:
 print('WORKSHOP_D4_FAIL');[print('FAIL:',e) for e in errors];sys.exit(1)
print('WORKSHOP_D4_PASS')
