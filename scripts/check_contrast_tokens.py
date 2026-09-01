#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]

def rgb(h):
    h=h.lstrip('#');return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def lum(h):
    vals=[]
    for c in rgb(h): vals.append(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4)
    return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
def ratio(a,b):
    x,y=sorted((lum(a),lum(b)),reverse=True);return (x+.05)/(y+.05)

checks=[
 ('static micro / white','#626b74','#ffffff',4.5),('static micro / paper','#626b74','#f6f7f3',4.5),
 ('dark micro / dark','#89919a','#101317',4.5),('dark micro / dark2','#89919a','#171b20',4.5),
 ('muted / paper','#687079','#f6f7f3',4.5),('acid micro','#526337','#b9ff3f',4.5),
 ('proof ghost / proof hero','#ffffff','#10211d',4.5),
 ('proof lab heading / dark panel','#f2f4f7','#101419',3.0),
 ('static proof gate index / white','#626b74','#ffffff',4.5),
 ('source proof gate index / warm card','#626b74','#fbf7f1',4.5),
]
errors=[]
for name,fg,bg,minr in checks:
    r=ratio(fg,bg)
    if r<minr:errors.append(f'{name}: {r:.2f} < {minr}')

from css_graph import read_local_css_graph

LIVE=ROOT/'deploy/live'
static=read_local_css_graph(LIVE/'style.css', LIVE)
source_files=('globals.css','r69.css','r70.css','commercial-mobile.css','proof-contrast.css')
nextcss='\n'.join((ROOT/'app'/name).read_text() for name in source_files)
layout=(ROOT/'app/layout.tsx').read_text()
if 'import "./proof-contrast.css";' not in layout:
    errors.append('source: proof-contrast.css not imported after existing global CSS')

for name,css in [('static',static),('next',nextcss)]:
    if '--micro:#626b74' not in css.replace(' ','') and '--micro: #626b74' not in css:
        errors.append(f'{name}: missing --micro token')
    if '--micro-dark:#89919a' not in css.replace(' ','') and '--micro-dark: #89919a' not in css:
        errors.append(f'{name}: missing --micro-dark token')

# Guard the known light-background microcopy selectors that previously failed 4.5:1.
required_static=['.kicker',' .meta',' .lesson b','.foot','.breadcrumb','.program>span','.program small','.fine','.methodgrid span','.projectcard>span']
for marker in required_static:
    token=marker.strip()
    pos=static.find(token)
    if pos<0 or 'var(--micro)' not in static[pos:pos+260]: errors.append(f'static selector {token} not bound to --micro')

# Guard independently reproduced Proof contrast regressions.
proof_rules=[
    ('static proof ghost', static, r'\.btn\.ghost\.ghostOnDark\s*\{[^}]*color\s*:\s*#fff'),
    ('static proof lab heading', static, r'\.proofLabStage\s+\.proofLabTitleRow\s+h2\s*\{[^}]*color\s*:\s*#f2f4f7'),
    ('source proof dark button', nextcss, r'\.buttonOnDark\s*\{[^}]*color\s*:\s*#fff'),
    ('source proof lab heading', nextcss, r'\.proofLabStage\s+\.proofLabTitleRow\s+h2\s*\{[^}]*color\s*:\s*#f2f4f7'),
]
for name,css,pattern in proof_rules:
    if not re.search(pattern, css): errors.append(f'{name}: missing explicit contrast rule')

# The Proof Gate backgrounds currently differ between static and source presentation
# layers, so guard both actual background assumptions independently.
background_rules=[
    ('static proof gate card', static, '.proofGateGrid article{', 'background:#fff'),
    ('source proof gate card', nextcss, '.proofGateGrid article{', 'background:#fbf7f1'),
]
for name,css,marker,expected in background_rules:
    pos=css.rfind(marker)
    if pos<0 or expected not in css[pos:pos+220].replace(' ',''):
        errors.append(f'{name}: effective background drift')

# The earlier R50 declaration may remain, but the effective last declaration must use
# the verified --micro token on both source and static CSS graphs.
for name,css in [('static proof gate index',static),('source proof gate index',nextcss)]:
    marker='.proofGateGrid article>span'
    pos=css.rfind(marker)
    if pos<0 or 'color:var(--micro)' not in css[pos:pos+180].replace(' ',''):
        errors.append(f'{name}: effective rule not bound to --micro')

print('contrast_ratios '+ ' '.join(f'{n}={ratio(f,b):.2f}' for n,f,b,_ in checks))
if errors:
    print('CONTRAST_TOKEN_FAIL');[print('-',e) for e in errors];sys.exit(1)
print('CONTRAST_TOKEN_PASS')
