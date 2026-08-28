#!/usr/bin/env python3
from pathlib import Path
from css_graph import read_local_css_graph

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy/live'
static=read_local_css_graph(LIVE/'style.css', LIVE)
static_r68=(LIVE/'style-r68.css').read_text(encoding='utf-8')
source=(ROOT/'app/globals.css').read_text(encoding='utf-8')

def structural_view(css: str) -> str:
    out=list(css)
    i=0
    while i < len(css):
        if css.startswith('/*', i):
            end=css.find('*/', i+2)
            if end < 0:
                raise SystemExit('MOTION_POLICY_FAIL static-r68 unterminated comment')
            for j in range(i, end+2):
                out[j]=' '
            i=end+2
            continue
        if css[i] in {'"', "'"}:
            quote=css[i]
            out[i]=' '
            i+=1
            while i < len(css):
                ch=css[i]
                out[i]=' '
                if ch=='\\':
                    i+=1
                    if i < len(css):
                        out[i]=' '
                        i+=1
                    continue
                i+=1
                if ch==quote:
                    break
            else:
                raise SystemExit('MOTION_POLICY_FAIL static-r68 unterminated string')
            continue
        i+=1
    return ''.join(out)

def validate_braces(view: str) -> None:
    depth=0
    for i,ch in enumerate(view):
        if ch=='{':
            depth+=1
        elif ch=='}':
            depth-=1
            if depth < 0:
                raise SystemExit(f'MOTION_POLICY_FAIL static-r68 unexpected closing brace at {i}')
    if depth:
        raise SystemExit(f'MOTION_POLICY_FAIL static-r68 unclosed brace depth={depth}')

def top_level_count(view: str, token: str) -> int:
    depth=0
    count=0
    for i,ch in enumerate(view):
        if depth==0 and view.startswith(token, i):
            count+=1
        if ch=='{':
            depth+=1
        elif ch=='}':
            depth-=1
    return count

checks=0
for name,css in [('static',static),('source',source)]:
    required=['prefers-reduced-motion','no-preference','reduce','labGridDrift','labOrbA','labOrbB','labCoreFloat','labSignal','animation: none !important' if name=='source' else 'animation:none!important']
    for marker in required:
        checks+=1
        if marker not in css:
            raise SystemExit(f'MOTION_POLICY_FAIL {name} missing {marker}')
    checks+=1
    if 'scroll-behavior:auto' not in css.replace(' ',''):
        raise SystemExit(f'MOTION_POLICY_FAIL {name} missing scroll fallback')

view=structural_view(static_r68)
validate_braces(view)
checks+=1

for token,expected in [
    ('@keyframes labOrbA{',1),
    ('@keyframes labOrbB{',1),
    ('@media(prefers-reduced-motion:no-preference){',1),
    ('.engineMode.isActive{',1),
]:
    checks+=1
    actual=top_level_count(view, token)
    if actual != expected:
        raise SystemExit(f'MOTION_POLICY_FAIL static-r68 top-level {token} count={actual}, expected={expected}')

checks+=1
max850=top_level_count(view, '@media(max-width:850px){')
if max850 < 2:
    raise SystemExit(f'MOTION_POLICY_FAIL static-r68 top-level max-width:850px count={max850}, expected>=2')

for marker in [
    '.orbA{animation:labOrbA 9s ease-in-out infinite alternate}',
    '.orbB{animation:labOrbB 11s ease-in-out infinite alternate}',
    '.visualbar b{animation:labSignal 2.6s ease-in-out infinite}',
]:
    checks+=1
    if marker not in static_r68:
        raise SystemExit(f'MOTION_POLICY_FAIL static-r68 missing {marker}')

print(f'motion_policy_checks={checks} surfaces=2 structural=style-r68.css')
print('MOTION_POLICY_PASS')
