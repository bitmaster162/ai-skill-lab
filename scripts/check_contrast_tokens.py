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
]
errors=[]
for name,fg,bg,minr in checks:
    r=ratio(fg,bg)
    if r<minr:errors.append(f'{name}: {r:.2f} < {minr}')

static=(ROOT/'deploy/live/style.css').read_text()
nextcss=(ROOT/'app/globals.css').read_text()
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

print('contrast_ratios '+ ' '.join(f'{n}={ratio(f,b):.2f}' for n,f,b,_ in checks))
if errors:
    print('CONTRAST_TOKEN_FAIL');[print('-',e) for e in errors];sys.exit(1)
print('CONTRAST_TOKEN_PASS')
