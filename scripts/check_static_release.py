#!/usr/bin/env python3
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy' / 'live'

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.anchors=set(); self.forms=0; self.canonical=[]; self.jsonld=[]
        self._jsonld=False; self._buf=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag == 'a':
            if 'href' in a: self.links.append(a['href'])
            if 'id' in a: self.anchors.add(a['id'])
        if 'id' in a: self.anchors.add(a['id'])
        if tag == 'form': self.forms += 1
        if tag == 'link' and a.get('rel') == 'canonical' and a.get('href'): self.canonical.append(a['href'])
        if tag == 'script' and a.get('type') == 'application/ld+json': self._jsonld=True; self._buf=[]
    def handle_endtag(self, tag):
        if tag == 'script' and self._jsonld:
            self.jsonld.append(''.join(self._buf)); self._jsonld=False; self._buf=[]
    def handle_data(self, data):
        if self._jsonld: self._buf.append(data)

def route_for(path: Path) -> str:
    rel=path.relative_to(LIVE).as_posix()
    if rel == 'index.html': return '/'
    if rel.endswith('/index.html'): return '/' + rel[:-11]
    if rel.endswith('.html'): return '/' + rel[:-5]
    raise ValueError(rel)

def page_for_route(route: str, routes: dict[str, Path]):
    return routes.get(route.rstrip('/') or '/')

def main():
    html_files=sorted(LIVE.rglob('*.html'))
    if not html_files: raise SystemExit('FAIL: no static HTML pages')
    routes={route_for(p):p for p in html_files if p.name != '404.html'}
    parsed={}
    problems=[]; link_count=0; forms=0; jsonld_count=0
    for route,path in routes.items():
        parser=PageParser(); parser.feed(path.read_text(encoding='utf-8'))
        parsed[route]=parser; forms += parser.forms
        for raw in parser.jsonld:
            jsonld_count += 1
            try: json.loads(raw)
            except Exception as e: problems.append(f'{route}: invalid JSON-LD: {e}')
        for href in parser.links:
            if href.startswith(('http://','https://','mailto:','tel:','javascript:')): continue
            link_count += 1
            if href.startswith('#'):
                target_route=route; anchor=href[1:]
            else:
                u=urlparse(href); target_route=u.path.rstrip('/') or '/'; anchor=u.fragment
            target=page_for_route(target_route,routes)
            if not target:
                problems.append(f'{route}: missing route {href}')
                continue
            if anchor and anchor not in parsed.get(target_route, PageParser()).anchors:
                tp=parsed.get(target_route)
                if tp is None:
                    tp=PageParser(); tp.feed(target.read_text(encoding='utf-8'))
                if anchor not in tp.anchors: problems.append(f'{route}: missing anchor {href}')
    if forms: problems.append(f'public static forms present: {forms}')

    sitemap=LIVE/'sitemap.xml'
    if not sitemap.exists(): problems.append('missing sitemap.xml')
    else:
        locs=re.findall(r'<loc>https?://[^/]+([^<]*)</loc>', sitemap.read_text(encoding='utf-8'))
        sm={x.rstrip('/') or '/' for x in locs}
        if sm != set(routes):
            problems.append(f'sitemap mismatch: routes={len(routes)} sitemap={len(sm)} missing={sorted(set(routes)-sm)} extra={sorted(sm-set(routes))}')

    secret_rx=re.compile(r'(sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY)')
    for p in LIVE.rglob('*'):
        if p.is_file() and p.suffix.lower() in {'.html','.css','.js','.json','.xml','.txt','.svg','.webmanifest'}:
            try: text=p.read_text(encoding='utf-8')
            except UnicodeDecodeError: continue
            if secret_rx.search(text): problems.append(f'secret-like pattern in {p.relative_to(ROOT)}')

    print(f'pages={len(html_files)} public_routes={len(routes)} internal_links={link_count} forms={forms} jsonld={jsonld_count}')
    if problems:
        for x in problems: print('FAIL:',x)
        return 1
    print('STATIC_RELEASE_QA_PASS')
    return 0

if __name__ == '__main__': sys.exit(main())
