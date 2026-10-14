#!/usr/bin/env python3
"""Reproducible empty-inventory U2 integration; offline and read-only by default.

The header-only snapshot and empty consent template are deliberate publication
boundaries. Nonempty inventory requires its own review, not editing this seal.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy/live'
MODULE = ROOT / 'tools/phuket_housing_u2'
sys.path.insert(0, str(MODULE))
import catalog
_spec = importlib.util.spec_from_file_location('phuket_u2_preview', MODULE / 'preview.py')
assert _spec is not None and _spec.loader is not None
preview = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(preview)
RELEASE = 'PHUKET_UNIVERSE_U2_EMPTY_CATALOG_R6_20261014'
BRANCH = 'agent/phuket-universe-u2-integration-local-r1'
SNAPSHOT = ROOT / 'data/phuket_housing_r6_snapshot.json'
PROFILE = ROOT / 'data/phuket_housing_r6_profile.json'
SOURCE_SECTIONS = ROOT / 'data/phuket_housing_r6_sections.json'
AS_OF = '2026-10-14'
INPUT_SHA = 'a9e2b3b604b03e2dba232506e65b0175c094428181af7e050fa10d812b1f428d'
POLICY_SHA = '5001ac8008c0596236b4b8b887d3f7d039aa8f0984563a7064c3dcefa0091b3a'


def inputs() -> tuple[list, dict]:
    snapshot = json.loads(SNAPSHOT.read_bytes())
    catalog.need(snapshot.get('schema') == 'phuket-housing-empty-snapshot.v1'
                 and snapshot.get('as_of') == AS_OF, 'R6 snapshot identity')
    values = snapshot.get('values')
    catalog.need(values == [list(catalog.HEADERS)] and catalog.sha(catalog.canonical(values)) == INPUT_SHA,
                 'R6 only the verified empty inventory is admitted')
    policy = json.loads((MODULE / 'policy-template.json').read_bytes())
    catalog.need(catalog.sha(catalog.canonical(policy)) == POLICY_SHA
                 and policy.get('agencies') == [] and policy.get('max_listing_age_days') is None,
                 'R6 no consents or freshness authority')
    return values, policy


def client_script() -> bytes:
    """Keep tested filter logic; allow Next client navigation to initialize again."""
    source = (MODULE / 'filters.js').read_text(encoding='utf-8')
    catalog.need(source.count('(() => {') == 1 and source.count('})();') == 1, 'Filter wrapper drift')
    source = source.replace('(() => {', '(() => {\n  function initializeHousingFilters() {', 1)
    source = source.replace('})();', "  }\n  document.addEventListener('phuket-housing:ready', initializeHousingFilters);\n  initializeHousingFilters();\n})();", 1)
    return source.encode('utf-8')


def section_sources() -> dict:
    values, policy = inputs()
    compiled = catalog.compile_catalog(values, policy, policy_sha=POLICY_SHA, as_of=AS_OF)
    catalog.need(compiled['listings'] == [] and compiled['counts']['accepted'] == 0, 'Real inventory blocked')
    parent = preview.parent_payload()
    sections = {}
    for locale, filename in [('ru', 'phuket-universe.html'), ('en', 'en/phuket-universe.html')]:
        page = preview.homes_page(parent[filename].decode('utf-8'), compiled, locale)
        start, end = preview.section_bounds(page)
        sections[locale] = page[start:end]
    return {'schema': 'phuket-housing-sections.v1', 'input_sha256': INPUT_SHA, 'listings_count': 0, **sections}


def generated_sources() -> dict[Path, bytes]:
    return {
        SOURCE_SECTIONS: (json.dumps(section_sources(), ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8'),
        ROOT / 'public/phuket-housing-u2.js': client_script(),
        ROOT / 'public/phuket-housing-u2.css': (MODULE / 'catalog.css').read_bytes(),
    }


def render() -> dict[str, bytes]:
    values, policy = inputs()
    files, stats = preview.render(values, policy, policy_sha=POLICY_SHA, as_of=AS_OF)
    catalog.need(stats['catalog_counts']['accepted'] == 0, 'R6 real listings forbidden')
    files['phuket-housing-u2.js'] = client_script()
    rows = [{'path': n, 'size': len(b), 'sha256': catalog.sha(b)} for n, b in sorted(files.items()) if n != '_release.json']
    payload = catalog.sha(''.join(f"{r['path']}\t{r['size']}\t{r['sha256']}\n" for r in rows).encode('utf-8'))
    manifest = {'schema': 'ai-skill-lab.static-release.v1', 'release_id': RELEASE,
                'file_count': len(rows), 'payload_sha256': payload, 'files': rows}
    files['_release.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode('utf-8')
    return files


def require_local_draft() -> None:
    catalog.need(preview.git('branch', '--show-current').decode().strip() == BRANCH, 'Isolated R6 branch only')
    p = json.loads(PROFILE.read_bytes())
    catalog.need(p.get('status') == 'Draft' and p.get('authority') == {
        'push': False, 'pr': False, 'merge': False, 'deploy': False, 'production': False,
        'scheduler': False, 'real_listings': False}, 'R6 draft preparation only')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-sources', action='store_true')
    parser.add_argument('--prepare-local', action='store_true')
    args = parser.parse_args()
    source = generated_sources()
    if args.prepare_sources:
        require_local_draft()
        catalog.need(all(not path.exists() for path in source), 'Generated source create-only')
        for path, data in source.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    catalog.need(all(path.is_file() and path.read_bytes() == data for path, data in source.items()), 'R6 generated source drift')
    files = render()
    if args.prepare_local:
        require_local_draft()
        current = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob('*') if p.is_file()}
        catalog.need(current == preview.parent_payload(), 'R6 preparation requires intact R5; no reseal')
        for name, data in sorted(files.items(), key=lambda row: row[0] == '_release.json'):
            target = LIVE / name
            catalog.need(not target.is_symlink() and target.resolve().is_relative_to(LIVE.resolve()), 'Unsafe local target')
            if not target.exists() or target.read_bytes() != data:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    current = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob('*') if p.is_file()}
    catalog.need(current == files, 'R6 source/static reproduction mismatch')
    print('PHUKET_R6_REPRODUCTION_PASS files=' + str(len(files)))


if __name__ == '__main__':
    main()
