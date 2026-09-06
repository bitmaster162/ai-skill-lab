#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]; LIVE=ROOT/'deploy/live'; errors=[]; checks=0
LEGAL={'app/safety/page.tsx': 'a87ef90f849331c9ca7337dfbb62902c13406a8e4fbff87dbd2770187cc0a235', 'app/en/safety/page.tsx': 'c7c9cd312876ab66d10525b647d5a890aed7cdd5bd32191a00468c6f036b833d', 'app/privacy/page.tsx': '68baddfb618a25a900ad1792f822523ee0850730bd5ccbe358c555c72fa7f9fd', 'app/en/privacy/page.tsx': '12fe669d9f0481c62519d8e2ca5421f1c0a69ec0c9ee11cfb22e6dd8d87f57d7', 'app/terms/page.tsx': '41f77ed8739c7b139d0e86e5e2affcd2e6db2b2be15af1990695b155f3770949', 'app/en/terms/page.tsx': '0513b79541e543187eeca99a83fc335916c0c44e19a75a85e1b43e41d25ee957'}
PROTECTED={'README.md': 'a2a43727485470a60d3259d6874a0eb2893827ccf2a4cec0c4f0dd14ba778994', 'app/sitemap.ts': '612cf6960059a719cfba459c54bbd54fab38711bca3f43875edc8a42ff43509d', 'deploy/live/sitemap.xml': '13bd4157b2ec5b88ae4f1fb2c361a79614a0c10bf4cc2008c9bd056cd4ff75fe', 'deploy/live/llms.txt': 'b581164e977efe097589024dec3ff95265835b0ae8df216e3dd7494c62b3e1f4', 'deploy/live/robots.txt': 'e4b9d3404c59d087f4cfbcc147771ffbc2d9cdfa9a457937c3cbeaff87ec418c', 'deploy/live/vercel.json': 'b7437ba32e26c367662673e9ece46c476f0c299474a0e9b7c45351bec08281fc', 'deploy/live/lab-command.js': '16835b5e85db24ef8f97eb2efa2b408221c725bd9334dee940723e3d816a7702', 'deploy/live/project-filter.js': '9ffbc90afc98556eb1539629ede2876362e2a00f2b84fe20df315fc09997dc28', 'data/commercial_facts.json': 'f747296d269fd57940e24a22e7d08f988ede5e43460549afdb39e3ef5857fc77', 'components/ProgramMatcher.tsx': '28ad6aa4f8f9c662a2da491327eca3ca5eff95a539c0916509d0ad4f6b2561d2', 'components/SystemChallenge.tsx': '953826dad2ffe1ddfe16887d84aec19cd1dd24521a2a1b03592d7741a92de2b4', 'components/ProofLab.tsx': 'ed01fbf773b423f26afe20ba4358fc1991be8968b84c756bb5203f6399169469', 'components/BriefCompiler.tsx': '156478fa6e9b38af1b2df7b97f460cbeaedb06e28215d7da03d9849db52da89d', 'components/ProjectStudio.tsx': '68b3fb0d29b584470046e7d742ef6a71f3089f85f5a424fc747c4df30d1bb8b1', 'components/SkillGraph.tsx': '9145c854d743820752e1b423a2e4f485966c974c0f2e9756f0e6ace32cbf953f', 'components/workshop/WorkshopShell.tsx': '24a9fa79c55d5ebfcce38d2e3c16e6aab566fcfc214a773747e5230d1a79c61c', 'components/workshop/WorkshopEditorial.tsx': 'ff8e746fa7bf34099351fad9d78a764062837fbcb9c50c0dac0101c75207c051', 'components/LabCommand.tsx': '0f9cccaea8dd1d8a1fb2be28aa125f66ec97fe49f83f641fa898afad878ac57a', 'components/Header.tsx': '589c9e9223162fe1f280fb3f49c9a5bf18eca74279de3607f8398d1371fcfec6', 'components/Footer.tsx': '1f544c0ca63e2b0e1b2309761f9edb38fd292c747279bc8cd5f16f5988a9bb35'}
STATIC_MAIN={'about.html': '7057e865bac6a71f4f851724e487f31043bbc2a94f0c1ad2b0cf5b654aef6663', 'method.html': '788999c0c101077f094447ce31ca7f3568e0382f7fac7bdb18eb6f0fec1d441c', 'safety.html': 'bf1235dfbbe4bc3c7d61da750cc2346e65255c1255812a87060b45f1dfb7f2fb', 'privacy.html': 'c9ce04f60b546446d29df5770aa3ca31088a475b45f6f295318d8f4cac8ba1f3', 'terms.html': 'df2424f191281bb772118e6338d1ea27afa78995eba5fd6d9234ba527d1dcdda', 'en/about.html': 'fc62f6b7810d87f584419e8a01b682a8f59fbd881162f5d58e2a5e855a13c4ce', 'en/method.html': '51e6c4f16f2ac5b38f6817304585a725358baff416dadc86dc249714b67eb6b8', 'en/safety.html': 'fcb617b245c895f10a02efaba01fb1d20e2a2c9c36b6e5ce25567c9e83d0f29f', 'en/privacy.html': '27d146e01c71b50d2a180ad1cd5a4a0d8bd2a65d77bd267143988d9fdd62ca42', 'en/terms.html': '960fc4a824d6fe1af7c798501b2b8fb0018e3ff0e608727db11c435e62accbca'}
SOURCE_MAIN={'app/about/page.tsx': '3cf2e4631519519cc74e196ce72d10dee2fff350770f0b9d9eaaf8225c9e42e2', 'app/en/about/page.tsx': '94f615394b64a50e17fb52683d6b6c626cdd4eef5c47a2d56dabd31c2c7a1971', 'app/method/page.tsx': '80f30e2805b3844fa5ac9606859a5e09240289063b0f80791073809273240070', 'app/en/method/page.tsx': '42566bbf5f9a60cfe61f83734d2ee4631a94f198ab7bf893941e971557606b19'}
TARGET=list(STATIC_MAIN)
def req(c,m):
 global checks; checks+=1
 if not c: errors.append(m)
def read(rel): return (ROOT/rel).read_text(encoding='utf-8')
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
def main_digest(text):
 m=re.search(r'<main id="main".*?</main>',text,re.S)
 return hashlib.sha256(m.group(0).encode()).hexdigest() if m else None
for rel,d in LEGAL.items(): req(sha(rel)==d,f'legal source byte drift {rel}')
for rel,d in PROTECTED.items(): req(sha(rel)==d,f'protected byte drift {rel}')
for rel,d in SOURCE_MAIN.items():
 t=read(rel); req(main_digest(t)==d,f'source main drift {rel}'); req('WorkshopEditorial' in t and 'Header' not in t and 'Footer' not in t,f'source Workshop shell {rel}')
legalpage=read('components/LegalPage.tsx'); req('WorkshopEditorial' in legalpage and '<main id="main" className="legalMain">' in legalpage,'LegalPage Workshop shell/id'); req('Header' not in legalpage and 'Footer' not in legalpage,'LegalPage legacy shell')
for rel,d in STATIC_MAIN.items():
 t=read('deploy/live/'+rel); en=rel.startswith('en/'); route=rel.split('/')[-1][:-5]; alt='/'+route if en else '/en/'+route; start='/en/start' if en else '/start'
 req(main_digest(t)==d,f'static main drift {rel}'); req('<header class="workshopHeader">' in t and '<header class="nav">' not in t,f'Workshop header {rel}'); req('<footer class="workshopFooter">' in t,f'Workshop footer {rel}')
 req('<link rel="stylesheet" href="/workshop.css">' in t and 'href="/style.css"' not in t,f'Workshop stylesheet {rel}'); req(t.count('data-lab-command-open')==1 and t.count('src="/lab-command.js"')==1,f'LAB runtime {rel}'); req(f'href="{alt}"' in t and f'href="{start}"' in t,f'alt/start {rel}')
 for bad in ('<form','fetch(','XMLHttpRequest','WebSocket(','localStorage','sessionStorage','document.cookie','sendBeacon('): req(bad not in t,f'forbidden client primitive {rel} {bad}')

for rel in ['app/safety/page.tsx','app/en/safety/page.tsx','deploy/live/safety.html','deploy/live/en/safety.html']:
 t=read(rel); req(t.count('data-policy-verified="2026-08-15"')==1,f'policy date {rel}'); req('https://help.openai.com/en/articles/8313401' in t,f'age source {rel}'); req('https://help.openai.com/en/articles/12315553-parental-controls-on-chatgpt-faq/' in t,f'parental source {rel}')
for rel in ['app/privacy/page.tsx','app/en/privacy/page.tsx']:
 t=read(rel).lower(); req('contact-only' in t,f'privacy contact-only {rel}'); req(('рекламные пиксели' in t) or ('advertising pixels' in t),f'privacy no-ad-pixels {rel}')
for rel in ['deploy/live/privacy.html','deploy/live/en/privacy.html']:
 req('contact-only' in read(rel).lower(),f'privacy contact-only {rel}')
for rel in ['app/about/page.tsx','app/en/about/page.tsx','deploy/live/about.html','deploy/live/en/about.html']:
 t=read(rel); req('Proof by artifact' in t,f'about proof {rel}'); req(('Claims discipline' in t) or ('claims discipline' in t),f'about claims {rel}')
for rel in ['app/method/page.tsx','app/en/method/page.tsx','deploy/live/method.html','deploy/live/en/method.html']:
 req('HUMAN IN THE LOOP' in read(rel),f'method human-in-loop {rel}')
all_html=list(LIVE.rglob('*.html')); public=[p for p in all_html if p.name!='404.html']; req(len(all_html)==47,'47 html including 404')
workshop=sum('<header class="workshopHeader">' in p.read_text(encoding='utf-8') for p in public); legacy=sum('<header class="nav">' in p.read_text(encoding='utf-8') for p in public); req(workshop==46,f'Workshop pages {workshop} != 46'); req(legacy==0,f'legacy pages {legacy} != 0')
routes={('/' if p.name=='index.html' else '/en' if p.relative_to(LIVE).as_posix()=='en.html' else '/'+p.relative_to(LIVE).as_posix()[:-5]) for p in public}; req(len(routes)==46,'46 public routes')
manifest=json.loads(read('deploy/live/_release.json')); req(manifest.get('schema')=='ai-skill-lab.static-release.v1','release schema'); req(manifest.get('release_id')=='R100_D5','R100_D5 release'); req(manifest.get('file_count')==62,'62 release files')
actual={p.relative_to(LIVE).as_posix():(len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest()) for p in LIVE.rglob('*') if p.is_file() and p.name!='_release.json'}; listed={x['path']:(x['size'],x['sha256']) for x in manifest.get('files',[])}; req(actual==listed,'manifest exact bytes'); payload=sum(x[0] for x in actual.values()); req(payload<=524288,f'payload {payload} > 524288')
workflow=read('.github/workflows/static-qa.yml'); preflight=read('scripts/preflight_release.py'); req(workflow.count('python scripts/check_workshop_d5.py')==1,'workflow D5 once'); req(preflight.count('scripts/check_workshop_d5.py')==1,'preflight D5 once')
print(f'workshop_d5_checks={checks} target_pages=10 workshop_pages={workshop} legacy_pages={legacy} routes={len(routes)} html={len(all_html)} files={manifest.get("file_count")} payload_bytes={payload} headroom={524288-payload}')
if errors:
 print('WORKSHOP_D5_FAIL'); [print('FAIL:',e) for e in errors]; sys.exit(1)
print('WORKSHOP_D5_PASS')
