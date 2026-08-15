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
        self.links=[]; self.anchors=set(); self.forms=0; self.canonical=[]; self.alternates={}; self.jsonld=[]
        self._jsonld=False; self._buf=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag == 'a':
            if 'href' in a: self.links.append(a['href'])
            if 'id' in a: self.anchors.add(a['id'])
        if 'id' in a: self.anchors.add(a['id'])
        if tag == 'form': self.forms += 1
        if tag == 'link' and a.get('rel') == 'canonical' and a.get('href'): self.canonical.append(a['href'])
        if tag == 'link' and a.get('rel') == 'alternate' and a.get('hreflang') and a.get('href'): self.alternates[a['hreflang']]=a['href']
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
                candidate=(LIVE / u.path.lstrip('/')).resolve() if not href.startswith('#') else None
                live_root=LIVE.resolve()
                if candidate is not None and candidate.is_file() and (candidate == live_root or live_root in candidate.parents):
                    continue
                problems.append(f'{route}: missing route {href}')
                continue
            if anchor and anchor not in parsed.get(target_route, PageParser()).anchors:
                # parse target lazily when it comes later in the walk
                tp=parsed.get(target_route)
                if tp is None:
                    tp=PageParser(); tp.feed(target.read_text(encoding='utf-8'))
                if anchor not in tp.anchors: problems.append(f'{route}: missing anchor {href}')
    if forms: problems.append(f'public static forms present: {forms}')

    canonical_base='https://ai-skill-lab.vercel.app'
    for route,parser in parsed.items():
        expected_canonical=canonical_base + ('/' if route == '/' else route)
        if parser.canonical != [expected_canonical]:
            problems.append(f'{route}: canonical mismatch {parser.canonical!r} != {expected_canonical!r}')
        if route == '/': ru_route, en_route = '/', '/en'
        elif route == '/en': ru_route, en_route = '/', '/en'
        elif route.startswith('/en/'):
            ru_route, en_route = route[3:], route
        else:
            ru_route, en_route = route, '/en' + route
        expected_alt={
            'ru': canonical_base + ('/' if ru_route == '/' else ru_route),
            'en': canonical_base + en_route,
            'x-default': canonical_base + ('/' if ru_route == '/' else ru_route),
        }
        for lang,expected in expected_alt.items():
            if parser.alternates.get(lang) != expected:
                problems.append(f'{route}: hreflang {lang} mismatch {parser.alternates.get(lang)!r} != {expected!r}')

    sitemap=LIVE/'sitemap.xml'
    if not sitemap.exists(): problems.append('missing sitemap.xml')
    else:
        locs=re.findall(r'<loc>https?://[^/]+([^<]*)</loc>', sitemap.read_text(encoding='utf-8'))
        sm={x.rstrip('/') or '/' for x in locs}
        if sm != set(routes):
            problems.append(f'sitemap mismatch: routes={len(routes)} sitemap={len(sm)} missing={sorted(set(routes)-sm)} extra={sorted(sm-set(routes))}')

    release_manifest=LIVE/'_release.json'
    if not release_manifest.exists():
        problems.append('missing _release.json')
    else:
        try:
            manifest=json.loads(release_manifest.read_text(encoding='utf-8'))
            if manifest.get('schema') != 'ai-skill-lab.static-release.v1': problems.append('invalid release manifest schema')
            listed={x['path']:(x['size'],x['sha256']) for x in manifest.get('files',[])}
            actual={}
            import hashlib
            for p in sorted(LIVE.rglob('*')):
                if not p.is_file() or p == release_manifest: continue
                rel=p.relative_to(LIVE).as_posix(); b=p.read_bytes()
                actual[rel]=(len(b),hashlib.sha256(b).hexdigest())
            if listed != actual: problems.append(f'release manifest file map mismatch: listed={len(listed)} actual={len(actual)}')
            aggregate=''.join(f'{path}\t{size}\t{sha}\n' for path,(size,sha) in sorted(actual.items())).encode()
            digest=hashlib.sha256(aggregate).hexdigest()
            if manifest.get('payload_sha256') != digest: problems.append('release manifest payload_sha256 mismatch')
            if manifest.get('file_count') != len(actual): problems.append('release manifest file_count mismatch')
        except Exception as e:
            problems.append(f'invalid _release.json: {e}')

    source_placeholder_rx=re.compile(r'https?://(?:example\.com|localhost(?::\d+)?)', re.I)
    for root_name in ('app','components','lib'):
        root=ROOT/root_name
        if not root.exists(): continue
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.ts','.tsx','.js','.jsx'}:
                try: text=p.read_text(encoding='utf-8')
                except UnicodeDecodeError: continue
                if source_placeholder_rx.search(text):
                    problems.append(f'release placeholder URL in {p.relative_to(ROOT)}')

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
