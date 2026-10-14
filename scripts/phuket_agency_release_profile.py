"""Exact R5 agency-copy integration. Reads only; grants no external authority."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy/live'
RELEASE = 'PHUKET_UNIVERSE_U1_AGENCY_TERMS_R5_20261014'
PROFILE_PATH = ROOT / 'data/phuket_universe_agency_terms_r5_profile.json'
MANIFEST_SHA = '07a73c34164905d37167ed594b51547a2add12cc2e00f42c631853d8266949de'
PAYLOAD_SHA = 'e8b41c9e6fed3e6b1f2b9edf66e1ddd227c4253fd1cb70c7030265dba1c63726'
R3_PROFILE_SHA = '636aa7ce973594e31b8704b1c23d577ebb556e70d08c18ea727c0744c2a1d7a5'
R3_PAYLOAD_SHA = '40606d00063d1ec99f495bf3623f8a8ddba23bc04298c530cf6cd97f92965c10'
R3_MANIFEST_SHA = '8200834001cbecdfae4cad7976886730561c138ae1d61e9340f984d5ddac4cf1'
REPORT_SHA = '926336a8df1baa55d89de11bcbf96b87ebcf70acbf03db6a228a34aece056770'
CHANGED_FILES = frozenset({'phuket-universe.html', 'en/phuket-universe.html', 'phuket-universe.css'})
UNIVERSE_FILES = frozenset({'phuket-universe.html', 'en/phuket-universe.html'})
AUTHORITY = {'push': False, 'pr': False, 'merge': False, 'deploy': False, 'production': False}
BUDGETS = {'payload_max_bytes': 1327774, 'nonfont_max_bytes': 1206386,
           'font_max_bytes': 121388, 'font_max_file_bytes': 55296,
           'html_max_file_bytes': 36864, 'css_max_file_bytes': 41984}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest(rows: dict) -> str:
    return sha(''.join(f"{n}\t{r['size']}\t{r['sha256']}\n" for n, r in sorted(rows.items())).encode('utf-8'))


def active() -> bool:
    return json.loads((LIVE / '_release.json').read_text(encoding='utf-8')).get('release_id') == RELEASE


def profile() -> dict:
    p = json.loads(PROFILE_PATH.read_text(encoding='utf-8'))
    if (p.get('schema') != 'ai-skill-lab.release-profile.v1' or p.get('release_id') != RELEASE
            or p.get('payload_sha256') != PAYLOAD_SHA or p.get('file_count') != 104
            or p.get('public_routes') != 56 or p.get('workshop_routes') != 54
            or p.get('authority') != AUTHORITY or p.get('budgets') != BUDGETS
            or p.get('source_report_sha256') != REPORT_SHA
            or p.get('previous_manifest_sha256') != R3_MANIFEST_SHA):
        raise ValueError('R5 profile identity/authority/budget drift')
    old_raw = (ROOT / 'data/phuket_universe_u1_static_r3_profile.json').read_bytes()
    if sha(old_raw) != R3_PROFILE_SHA:
        raise ValueError('R3 immutable profile changed')
    old = json.loads(old_raw)
    for key in ('fonts', 'parent_commit', 'parent_file_pins', 'parent_payload_sha256',
                'parent_manifest_sha256', 'parent_release_id', 'new_files',
                'modified_parent_files', 'universe_routes'):
        if p.get(key) != old.get(key):
            raise ValueError('Historical scope changed: ' + key)
    pins = p.get('r3_file_pins', {})
    if len(pins) != 104 or digest(pins) != R3_PAYLOAD_SHA:
        raise ValueError('R3 independent byte pins changed')
    transfers = p.get('transfer_profiles', {})
    if set(transfers) != UNIVERSE_FILES:
        raise ValueError('R5 transfer route set changed')
    for name, value in transfers.items():
        ru = name == 'phuket-universe.html'
        expected_fonts = ['Unbounded-ru-en.woff2', 'Manrope-latin.woff2'] + (['Manrope-cyrillic.woff2'] if ru else [])
        caps = {'css_br_max': 9984, 'first_br_max': 18432, 'first_gzip_max': 21760,
                'first_with_fonts_max': 109056 if ru else 102400,
                'font_bytes': 91352 if ru else 76852}
        if value.get('fonts') != expected_fonts or any(value.get(k) != v for k, v in caps.items()):
            raise ValueError('R5 route-specific transfer limits changed')
    return p


def verify_integrity() -> dict:
    p = profile()
    mraw = (LIVE / '_release.json').read_text(encoding='utf-8')
    m = json.loads(mraw)
    records = m.get('files', [])
    if (m.get('schema') != 'ai-skill-lab.static-release.v1' or m.get('release_id') != RELEASE
            or len(records) != 104 or len({e['path'] for e in records}) != 104):
        raise ValueError('R5 duplicate/missing records or wrong identity')
    if sha(mraw.encode('utf-8')) != MANIFEST_SHA:
        raise ValueError('R5 independent manifest pin changed')
    actual = {}
    for path in LIVE.rglob('*'):
        if path.is_symlink():
            raise ValueError('R5 symlink forbidden')
        if path.is_file() and path.name != '_release.json':
            data = path.read_bytes()
            actual[path.relative_to(LIVE).as_posix()] = {'size': len(data), 'sha256': sha(data)}
    recorded = {e['path']: {'size': e['size'], 'sha256': e['sha256']} for e in records}
    if actual != recorded or m.get('file_count') != 104:
        raise ValueError('R5 actual payload differs from manifest')
    if digest(actual) != PAYLOAD_SHA or m.get('payload_sha256') != PAYLOAD_SHA:
        raise ValueError('R5 independent payload pin changed')
    r3 = p['r3_file_pins']
    if set(actual) != set(r3) or {n for n in r3 if r3[n] != actual[n]} != CHANGED_FILES:
        raise ValueError('R5 must change exactly two Universe pages and CSS')
    parent = p['parent_file_pins']
    if {n for n in parent if parent[n] != actual[n]} != {'llms.txt', 'sitemap.xml'}:
        raise ValueError('Inherited Workshop bytes changed')
    total = sum(e['size'] for e in actual.values())
    fonts = {n: e for n, e in actual.items() if n.endswith('.woff2')}
    font_bytes = sum(e['size'] for e in fonts.values())
    if total != 1327774 or fonts != p['fonts'] or font_bytes != 121388:
        raise ValueError('R5 measured byte composition changed')
    return {'release': RELEASE, 'files': 104, 'routes': 56, 'workshop_routes': 54,
            'parent_files_unchanged': 96, 'r3_files_unchanged': 101,
            'font_bytes': font_bytes, 'payload_bytes': total}


def check_release() -> dict:
    result = verify_integrity()
    from build_phuket_agency_release_r5 import render
    from prepare_phuket_agency_terms_r4 import add_terms, copy_data
    from phuket_release_profile import universe_page
    actual = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob('*') if p.is_file()}
    if render() != actual:
        raise ValueError('R5 immutable parent / report copy reproduction mismatch')
    raw = (ROOT / 'components/phuketUniverseMarkup.ts').read_text(encoding='utf-8')
    markup = json.loads(raw.split('export const phuketUniverseMarkup = ', 1)[1].rsplit(' as const;', 1)[0])
    copy = copy_data()
    for name in sorted(UNIVERSE_FILES):
        locale = 'en' if name.startswith('en/') else 'ru'
        text = actual[name].decode('utf-8')
        if not universe_page(LIVE / name) or add_terms(markup[locale], locale, copy) not in text:
            raise ValueError('R5 source/static terms or shell mismatch')
        if text.count('id="agency-pilot-terms"') != 1:
            raise ValueError('R5 duplicate/missing terms block')
    for name, expected in profile()['source_override_sha256'].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError('R5 reviewed source pin changed: ' + name)
    return result
