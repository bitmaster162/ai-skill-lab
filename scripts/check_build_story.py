#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
errors=[];checks=0
surfaces=[
 ('app/build/page.tsx',False),('app/en/build/page.tsx',True),
 ('deploy/live/build.html',False),('deploy/live/en/build.html',True),
]
required_common=['BUILD STORY / OPEN PROVENANCE','R8','R24','R31','R38','R49','R60','R65','R66','CHATGPT','WEB RESEARCH','LOCAL TEST STACK','GIT / BUNDLES','VERCEL','HUMAN REVIEW','STATIC JS BROKE','METADATA DRIFT','WRAPPER CORRUPTED','SANDBOX DISAPPEARED','DEPLOYMENT BLOCKED','/_release.json']
for rel,en in surfaces:
    text=(ROOT/rel).read_text(encoding='utf-8')
    for marker in required_common:
        checks+=1
        if marker not in text: errors.append(f'{rel}: missing {marker}')
    locale_markers=(['AI did','Human owned','We can govern an AI build.'] if en else ['AI did','Human owned','Мы умеем управлять AI-сборкой.'])
    for marker in locale_markers:
        checks+=1
        if marker not in text: errors.append(f'{rel}: missing {marker}')
    for forbidden in ['client revenue guaranteed','guaranteed ROI','Manus used','Antigravity used']:
        checks+=1
        if forbidden.lower() in text.lower(): errors.append(f'{rel}: forbidden unsupported claim {forbidden}')

# Discoverability must exist in source/static home, proof hub and shared command.
checks_to_markers={
 'app/page.tsx':['/build','Build log'],
 'app/en/page.tsx':['/en/build','Build log'],
 'deploy/live/index.html':['/build','Build log'],
 'deploy/live/en.html':['/en/build','Build log'],
 'app/proof/page.tsx':['/build','Build Log','PROVENANCE'],
 'app/en/proof/page.tsx':['/en/build','Build Log','PROVENANCE'],
 'deploy/live/proof.html':['/build','Build Log','PROVENANCE'],
 'deploy/live/en/proof.html':['/en/build','Build Log','PROVENANCE'],
 'components/LabCommand.tsx':['/build','/en/build','Build Log','PROVENANCE'],
 'deploy/live/lab-command.js':["b+'/build'",'Build Log','PROVENANCE'],
}
for rel,markers in checks_to_markers.items():
    text=(ROOT/rel).read_text(encoding='utf-8')
    for marker in markers:
        checks+=1
        if marker not in text: errors.append(f'{rel}: missing discoverability marker {marker}')

print(f'build_story_checks={checks} surfaces={len(surfaces)}')
if errors:
    for e in errors: print('FAIL:',e)
    sys.exit(1)
print('BUILD_STORY_PROVENANCE_PASS')
