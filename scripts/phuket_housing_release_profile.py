"""Exact R6 U2 empty-inventory profile; fail closed, reads only, no authority."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy/live'
RELEASE = 'PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014'
PROFILE_PATH = ROOT / 'data/phuket_housing_r6_profile.json'
MANIFEST_SHA = '5d07745a1220b1da82e224409210635ae83511f6184101671ea24987468b5966'
PAYLOAD_SHA = '0b5f3b9d20d3dbcb9dcb03c6e65c0f9b513792c7cbaf71d958ee15d13914ec94'
R5_PROFILE_SHA = 'be62c1022a71c9cfd39a4590489ba4bb154bad88c73bc75a562b9312554d1c04'
R5_PAYLOAD_SHA = 'e8b41c9e6fed3e6b1f2b9edf66e1ddd227c4253fd1cb70c7030265dba1c63726'
R5_MANIFEST_SHA = '07a73c34164905d37167ed594b51547a2add12cc2e00f42c631853d8266949de'
INPUT_SHA = 'a9e2b3b604b03e2dba232506e65b0175c094428181af7e050fa10d812b1f428d'
POLICY_SHA = '5001ac8008c0596236b4b8b887d3f7d039aa8f0984563a7064c3dcefa0091b3a'
PAGES = frozenset({'phuket-universe.html', 'en/phuket-universe.html'})
NEW_FILES = frozenset({'phuket-housing-u2.js', 'phuket-housing-u2.css'})
AUTHORITY = {'push': False, 'pr': False, 'merge': False, 'deploy': False,
             'production': False, 'scheduler': False, 'real_listings': False}
BUDGETS = {'payload_max_bytes': 1330820, 'nonfont_max_bytes': 1209432,
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
            or p.get('payload_sha256') != PAYLOAD_SHA or p.get('manifest_sha256') != MANIFEST_SHA
            or p.get('file_count') != 106 or p.get('public_routes') != 56 or p.get('workshop_routes') != 54
            or p.get('authority') != AUTHORITY or p.get('budgets') != BUDGETS
            or p.get('input_sha256') != INPUT_SHA or p.get('policy_sha256') != POLICY_SHA
            or p.get('accepted_listings') != 0 or p.get('previous_manifest_sha256') != R5_MANIFEST_SHA
            or set(p.get('new_u2_files', [])) != NEW_FILES or set(p.get('changed_r5_files', [])) != PAGES):
        raise ValueError('R6 profile identity/authority/budget drift')
    old_raw = (ROOT / 'data/phuket_universe_agency_terms_r5_profile.json').read_bytes()
    if sha(old_raw) != R5_PROFILE_SHA:
        raise ValueError('Historical R5 profile changed')
    old = json.loads(old_raw)
    for key in ('fonts', 'parent_commit', 'parent_file_pins', 'parent_payload_sha256',
                'parent_manifest_sha256', 'parent_release_id', 'new_files', 'modified_parent_files',
                'universe_routes', 'source_report_sha256'):
        if p.get(key) != old.get(key):
            raise ValueError('R6 inherited scope drift: ' + key)
    pins = p.get('r5_file_pins', {})
    if len(pins) != 104 or digest(pins) != R5_PAYLOAD_SHA:
        raise ValueError('R6 immutable R5 inventory drift')
    transfers = p.get('transfer_profiles', {})
    if set(transfers) != PAGES:
        raise ValueError('R6 transfer page scope')
    for name, value in transfers.items():
        ru = name == 'phuket-universe.html'
        fonts = ['Unbounded-ru-en.woff2', 'Manrope-latin.woff2'] + (['Manrope-cyrillic.woff2'] if ru else [])
        caps = {'css_br_max': 10496, 'first_br_max': 19456 if ru else 18432,
                'first_gzip_max': 23040 if ru else 22016,
                'first_with_fonts_max': 110592 if ru else 102400, 'font_bytes': 91352 if ru else 76852}
        if value.get('fonts') != fonts or any(value.get(k) != v for k, v in caps.items()):
            raise ValueError('R6 page transfer budget drift')
    return p


def verify_integrity() -> dict:
    p = profile()
    raw = (LIVE / '_release.json').read_text(encoding='utf-8')
    m = json.loads(raw)
    rows = m.get('files', [])
    if (m.get('release_id') != RELEASE or m.get('schema') != 'ai-skill-lab.static-release.v1'
            or len(rows) != 106 or len({e['path'] for e in rows}) != 106):
        raise ValueError('R6 duplicate/missing records or identity')
    if sha(raw.encode('utf-8')) != MANIFEST_SHA:
        raise ValueError('R6 manifest pin drift')
    actual = {}
    for file in LIVE.rglob('*'):
        if file.is_symlink():
            raise ValueError('R6 symlink forbidden')
        if file.is_file() and file.name != '_release.json':
            value = file.read_bytes()
            actual[file.relative_to(LIVE).as_posix()] = {'size': len(value), 'sha256': sha(value)}
    recorded = {e['path']: {'size': e['size'], 'sha256': e['sha256']} for e in rows}
    if recorded != actual or m.get('file_count') != 106:
        raise ValueError('R6 payload differs from manifest')
    if digest(actual) != PAYLOAD_SHA or m.get('payload_sha256') != PAYLOAD_SHA:
        raise ValueError('R6 payload pin drift')
    previous = p['r5_file_pins']
    if (set(actual) - set(previous) != NEW_FILES or set(previous) - set(actual)
            or {n for n in previous if previous[n] != actual[n]} != PAGES):
        raise ValueError('R6 only two pages and two assets allowed')
    fonts = {n: row for n, row in actual.items() if n.endswith('.woff2')}
    if fonts != p['fonts'] or sum(r['size'] for r in actual.values()) != 1330820:
        raise ValueError('R6 byte budget/font inventory drift')
    from build_phuket_housing_release_r6 import inputs
    inputs()
    return {'release': RELEASE, 'files': 106, 'routes': 56, 'workshop_routes': 54,
            'r5_files_unchanged': 102, 'parent_files_unchanged': 96,
            'font_bytes': 121388, 'payload_bytes': 1330820, 'real_listings': 0}


def check_release() -> dict:
    result = verify_integrity()
    from build_phuket_housing_release_r6 import render, generated_sources
    from phuket_release_profile import universe_page
    files = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob('*') if p.is_file()}
    if render() != files:
        raise ValueError('R6 reproduction drift')
    if any(not p.is_file() or p.read_bytes() != expected for p, expected in generated_sources().items()):
        raise ValueError('R6 Next sources differ from reviewed compiler output')
    for name in PAGES:
        if not universe_page(LIVE / name):
            raise ValueError('R6 alternative shell drift')
        text = files[name].decode('utf-8')
        if text.count('data-u2-catalog=""') != 1 or 'data-u2-card' in text or 'class="pu-s083"' in text:
            raise ValueError('R6 empty catalogue boundary changed')
        if text.count('id="agency-pilot-terms"') != 1:
            raise ValueError('R6 agency terms missing')
    for name, expected in profile()['source_override_sha256'].items():
        if sha((ROOT / name).read_bytes()) != expected:
            raise ValueError('R6 source pin drift: ' + name)
    return result
