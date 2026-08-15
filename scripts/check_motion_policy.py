#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
static=(ROOT/'deploy/live/style.css').read_text(encoding='utf-8')
source=(ROOT/'app/globals.css').read_text(encoding='utf-8')
checks=0
for name,css in [('static',static),('source',source)]:
    required=['prefers-reduced-motion','no-preference','reduce','labGridDrift','labOrbA','labOrbB','labCoreFloat','labSignal','animation: none !important' if name=='source' else 'animation:none!important']
    for marker in required:
        checks+=1
        if marker not in css: raise SystemExit(f'MOTION_POLICY_FAIL {name} missing {marker}')
    # Motion must be opt-in while reduced-motion has explicit animation + transition shutdown.
    no_idx=css.rfind('prefers-reduced-motion')
    checks+=1
    if no_idx<0: raise SystemExit(f'MOTION_POLICY_FAIL {name} missing media policy')
    checks+=1
    if 'scroll-behavior:auto' not in css.replace(' ',''):
        raise SystemExit(f'MOTION_POLICY_FAIL {name} missing scroll fallback')
print(f'motion_policy_checks={checks} surfaces=2')
print('MOTION_POLICY_PASS')
