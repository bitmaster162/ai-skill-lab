"""Create-only local U2 preview, reproducing the immutable R5 parent.
The published R5 payload and release profile are never written or resealed.
"""
from __future__ import annotations
import argparse
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
from catalog import AREAS, HEADERS, TERMS_SHA, card, canonical, compile_catalog, need, read_values, sha

MODULE = Path(__file__).resolve().parent
ROOT = MODULE.parents[1]
BASE = 'e61387d816bff7d0b8c9de3317f25914dab88c06'
TREE = '10a75780ef0a6e6e3a6d138af0ac34a0dc15becf'
MANIFEST_SHA = '07a73c34164905d37167ed594b51547a2add12cc2e00f42c631853d8266949de'
RELEASE = 'PHUKET_UNIVERSE_U2_LOCAL_R1_20261014'
BRANCH = 'agent/phuket-universe-u2-local-r1'


def git(*args: str) -> bytes:
    p = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, timeout=40)
    need(p.returncode == 0, 'Git read failed')
    return p.stdout


def parent_payload() -> dict[str, bytes]:
    need(git('rev-parse', BASE + '^{tree}').decode().strip() == TREE, 'Wrong Git parent')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(git('archive', '--format=tar', BASE, 'deploy/live'))) as stream:
        for item in stream:
            if item.isdir():
                continue
            need(item.isfile() and item.name.startswith('deploy/live/'), 'Unexpected parent entry')
            name = item.name.removeprefix('deploy/live/')
            need(name and '..' not in PurePosixPath(name).parts and '\\' not in name and name not in files, 'Unsafe parent path')
            data = stream.extractfile(item)
            need(data is not None, 'Missing parent bytes')
            files[name] = data.read()
    need(sha(files['_release.json']) == MANIFEST_SHA, 'Parent manifest changed')
    manifest = json.loads(files['_release.json'])
    need(len(manifest['files']) == manifest['file_count'] == 104 and len(files) == 105, 'Parent inventory')
    for row in manifest['files']:
        data = files[row['path']]
        need(len(data) == row['size'] and sha(data) == row['sha256'], 'Parent payload mismatch')
    return files


def section_bounds(document: str) -> tuple[int, int]:
    need(document.count('id="homes"') == 1, 'Homes boundary')
    pos = document.index('id="homes"')
    start = document.rfind('<section ', 0, pos)
    end = document.index('</section>', pos) + len('</section>')
    need(start >= 0 and document[start:end].count('<section ') == 1, 'Nested homes section')
    return start, end


class Controls(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.parts = []
        self.area_index = 0
        self.select = None
        self.option_index = 0
        self.island_path = ''
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); changed = False
        classes = set((a.get('class') or '').split())
        if tag == 'section' and a.get('id') == 'homes':
            a['data-u2-catalog'] = ''; changed = True
        if tag == 'path' and 'pu-s065' in classes:
            self.island_path = a['d']
        if tag == 'button':
            if 'pu-s061' in classes or 'pu-s062' in classes:
                a['data-u2-deal'] = 'rent' if 'pu-s061' in classes else 'sale'; changed = True
            elif classes & {'pu-s068', 'pu-s069'}:
                a['data-u2-area'] = ([''] + list(AREAS))[self.area_index]
                self.area_index += 1; changed = True
            elif 'pu-s076' in classes:
                a['data-u2-apply'] = ''; changed = True
        if tag == 'select':
            self.select = a.get('id'); self.option_index = 0
        if tag == 'option' and self.select in ('pu-type', 'pu-beds'):
            values = ['', 'condo', 'villa', 'house'] if self.select == 'pu-type' else ['', '0', '1', '2', '3', '4+']
            a['value'] = values[self.option_index]; self.option_index += 1; changed = True
        if tag == 'input' and a.get('id') == 'pu-price':
            a.update({'min': '0', 'step': '0.01'}); changed = True
        if changed:
            self.parts.append('<' + tag + ''.join(' ' + k + ('' if v is None else '="' + html.escape(v, quote=True) + '"') for k, v in a.items()) + '>')
        else:
            self.parts.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        self.parts.append('</' + tag + '>')
        if tag == 'select':
            self.select = None

    def handle_data(self, data): self.parts.append(data)
    def handle_entityref(self, name): self.parts.append('&' + name + ';')
    def handle_charref(self, name): self.parts.append('&#' + name + ';')
    def handle_comment(self, data): self.parts.append('<!--' + data + '-->')


def homes_page(document: str, catalog: dict, locale: str) -> str:
    start, end = section_bounds(document)
    source = document[start:end]
    need(source.count('<article class="pu-s083"') == 1, 'Demo card boundary')
    a = source.index('<article class="pu-s083"'); b = source.index('</article>', a) + len('</article>')
    source = source[:a] + '<!--U2_LISTINGS-->' + source[b:]
    if catalog['listings']:
        a = source.index('<div class="pu-s077">'); b = source.index('</div>', a) + len('</div>')
        source = source[:a] + source[b:]
    controls = Controls(source)
    need(controls.island_path and controls.area_index == 8, 'Map/control parity')
    rendered = ''.join(controls.parts)
    cards = ''.join(card(entry, locale, controls.island_path) for entry in catalog['listings'])
    nojs = 'Без JavaScript показаны все объекты; фильтры недоступны.' if locale == 'ru' else 'All listings are visible without JavaScript; filters are unavailable.'
    status = ('Объектов' if locale == 'ru' else 'Listings') + ': ' + str(len(catalog['listings']))
    listing_block = ('<p data-u2-status role="status" aria-live="polite">' + status + '</p>'
                     + '<noscript><p id="u2-nojs">' + nojs + '</p></noscript><div data-u2-list>' + cards + '</div>')
    need(rendered.count('<!--U2_LISTINGS-->') == 1, 'Duplicate listing insertion')
    rendered = rendered.replace('<!--U2_LISTINGS-->', listing_block, 1)
    return document[:start] + rendered + document[end:]


def render(values: list, policy: dict, *, policy_sha: str, as_of: str) -> tuple[dict[str, bytes], dict]:
    catalog = compile_catalog(values, policy, policy_sha=policy_sha, as_of=as_of)
    files = parent_payload()
    for locale, name in (('ru', 'phuket-universe.html'), ('en', 'en/phuket-universe.html')):
        page = homes_page(files[name].decode('utf-8'), catalog, locale)
        need(page.count('</head>') == page.count('</body>') == 1, 'Document boundaries')
        page = page.replace('</head>', '<link rel="stylesheet" href="/phuket-housing-u2.css"></head>', 1)
        page = page.replace('</body>', '<script src="/phuket-housing-u2.js" defer></script></body>', 1)
        files[name] = page.encode('utf-8')
    files['phuket-housing-u2.js'] = (MODULE / 'filters.js').read_bytes()
    files['phuket-housing-u2.css'] = (MODULE / 'catalog.css').read_bytes()
    rows = [{'path': name, 'size': len(data), 'sha256': sha(data)} for name, data in sorted(files.items()) if name != '_release.json']
    payload_hash = sha(''.join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows).encode())
    manifest = {'schema': 'ai-skill-lab.static-release.v1', 'release_id': RELEASE, 'file_count': len(rows), 'payload_sha256': payload_hash, 'files': rows}
    files['_release.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    return files, {'status': 'LOCAL_PREVIEW_NOT_RELEASE_INTEGRATED', 'as_of': as_of, 'catalog_counts': catalog['counts'],
                   'payload_sha256': payload_hash, 'manifest_sha256': sha(files['_release.json']), 'input_sha256': sha(canonical(values)),
                   'policy_sha256': policy_sha, 'parent_manifest_sha256': MANIFEST_SHA,
                   'authority': {'publish': False, 'deploy': False, 'scheduler': False}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--format', choices=('json', 'csv'), default='json')
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--policy-sha', required=True)
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(args.input.stat().st_size <= 1024*1024 and args.policy.stat().st_size <= 1024*1024, 'Input budget')
    values = read_values(args.input.read_bytes(), args.format)
    policy = json.loads(args.policy.read_bytes())
    need(git('branch', '--show-current').decode().strip() == BRANCH and not git('status', '--porcelain=v1').strip(), 'Commit clean local source first')
    parent = ROOT / 'deploy/preview'
    need(not args.out.exists() and args.out.resolve().is_relative_to(parent.resolve()) and args.out.resolve() != parent.resolve(), 'Create-only preview path required')
    need(not any(p.is_symlink() for p in [args.out, *args.out.parents]), 'Symlink output forbidden')
    files, receipt = render(values, policy, policy_sha=args.policy_sha, as_of=args.as_of)
    args.out.mkdir(parents=True, exist_ok=False)
    for name in sorted(files, key=lambda x: (x == '_release.json', x)):
        p = args.out / name; p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as stream: stream.write(files[name])
    actual = {p.relative_to(args.out).as_posix(): p.read_bytes() for p in args.out.rglob('*') if p.is_file()}
    need(actual == files, 'Written preview mismatch; do not retry')
    print(json.dumps(receipt, sort_keys=True), flush=True)


if __name__ == '__main__': main()
