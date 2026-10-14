"""U2 offline catalogue compiler. No network, credentials, publishing or scheduler.
Only a trusted operator supplies the private consent policy. A digest and a
confirmed flag bind that input; they are not a substitute for legal review.
"""
from __future__ import annotations
import csv
import hashlib
import html
import io
import ipaddress
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from urllib.parse import parse_qsl, urlsplit, urlunsplit

HEADERS = ('deal', 'area', 'type', 'bedrooms', 'price_thb', 'title', 'source_name', 'source_url', 'updated_at', 'partner_ok')
MAX_BYTES = 1024 * 1024  # Technical bound, not an approved commercial listing cap.
MAX_ROWS = 1000  # Current sheet grid bound, including its header.
TERMS_SHA = '1bc0947ae7062069dd116dde0d3356e483181c53c66440f453e2fa4d43483d9c'
AREAS = {
    'bang-tao': ('Банг Тао', 'Bang Tao', 159, 212.7),
    'patong': ('Патонг', 'Patong', 162.6, 302.7),
    'karon': ('Карон', 'Karon', 159, 348.6),
    'kata': ('Ката', 'Kata', 162.6, 371.1),
    'rawai': ('Раваи', 'Rawai', 183.3, 406.2),
    'chalong': ('Чалонг', 'Chalong', 195, 348.6),
    'phuket-town': ('Пхукет-таун', 'Phuket Town', 238.2, 314.4),
}
TYPES = {'condo': ('Квартира или кондо', 'Apartment or condo'), 'villa': ('Вилла', 'Villa'), 'house': ('Дом', 'House')}
DEALS = {'rent': ('Аренда', 'Rent'), 'sale': ('Продажа', 'Sale')}


def need(ok: bool, code: str) -> None:
    if not ok:
        raise ValueError(code)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def text(value: object, limit: int) -> str:
    need(isinstance(value, str), 'text_type')
    value = unicodedata.normalize('NFC', value).strip()
    need(0 < len(value) <= limit and not any(unicodedata.category(ch).startswith('C') for ch in value), 'text_format')
    return value


def enum_value(value: object, choices: dict, extra: dict | None = None) -> str:
    value = text(value, 60).casefold()
    lookup = {k.casefold(): k for k in choices}
    for k, labels in choices.items():
        for label in labels[:2]:
            lookup[str(label).casefold()] = k
    lookup.update(extra or {})
    need(value in lookup, 'unknown_enum')
    return lookup[value]


def iso_day(value: object) -> date:
    need(isinstance(value, str) and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', value)), 'date_format')
    return date.fromisoformat(value)


def https_source(value: object) -> tuple[str, str]:
    raw = text(value, 1500)
    need(not any(ch.isspace() for ch in raw) and '\\' not in raw, 'url_format')
    parts = urlsplit(raw)
    need(parts.scheme == 'https' and parts.username is None and parts.password is None and parts.port in (None, 443), 'https_required')
    host = (parts.hostname or '').lower()
    need(bool(re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,63}', host)), 'domain_format')
    need(not host.endswith(('.local', '.localhost', '.internal', '.home', '.lan')), 'private_host')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError('ip_host')
    need(not parts.fragment and not any(x in raw.lower() for x in ('%00', '%0a', '%0d', '%5c')), 'url_control_or_fragment')
    # Keep only understood listing-address parameters. Do not carry tracking,
    # authentication or arbitrary contact data into public links.
    need(all(k in {'id', 'listing_id', 'property_id', 'lang'} and len(v) <= 100 and '@' not in v
             for k, v in parse_qsl(parts.query, keep_blank_values=True, strict_parsing=True)), 'url_query_not_admitted')
    return urlunsplit(('https', host, parts.path or '/', parts.query, '')), host


def read_values(raw: bytes, kind: str = 'json') -> list:
    need(len(raw) <= MAX_BYTES, 'input_byte_budget')
    if kind == 'csv':
        values = list(csv.reader(io.StringIO(raw.decode('utf-8-sig')), strict=True))
    else:
        obj = json.loads(raw.decode('utf-8-sig'), parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite_json')))
        values = obj.get('values') if isinstance(obj, dict) else obj
    need(isinstance(values, list) and 1 <= len(values) <= MAX_ROWS, 'input_row_budget')
    need(isinstance(values[0], list) and tuple(values[0]) == HEADERS, 'exact_headers_required')
    return values


def compile_catalog(values: list, policy: dict, *, policy_sha: str, as_of: str) -> dict:
    today = iso_day(as_of)
    need(sha(canonical(policy)) == policy_sha, 'policy_digest_mismatch')
    need(policy.get('schema') == 'phuket-housing-consents.v1' and policy.get('terms_sha256') == TERMS_SHA, 'policy_identity')
    need(policy.get('authority') == {'publish': False, 'deploy': False, 'legal_review_completed': False}, 'local_authority_only')
    need(isinstance(values, list) and 1 <= len(values) <= MAX_ROWS and tuple(values[0]) == HEADERS, 'exact_headers_required')
    age_limit = policy.get('max_listing_age_days')
    need(age_limit is None or type(age_limit) is int and age_limit >= 0, 'freshness_policy_invalid')
    approvals = policy.get('agencies')
    need(isinstance(approvals, list), 'consent_registry_missing')
    indexed = {}
    for item in approvals:
        need(isinstance(item, dict), 'consent_record_invalid')
        key = (item.get('domain'), item.get('source_name'))
        need(all(isinstance(x, str) and x for x in key) and key not in indexed, 'duplicate_or_invalid_consent')
        indexed[key] = item
    rejected: Counter = Counter()
    accepted = []
    for row in values[1:]:
        if isinstance(row, list) and all(v is None or v == '' for v in row):
            continue
        try:
            need(isinstance(row, list) and len(row) == len(HEADERS), 'row_width')
            item = dict(zip(HEADERS, row))
            need(item['partner_ok'] == 'yes', 'partner_not_approved')
            url, host = https_source(item['source_url'])
            name = text(item['source_name'], 100)
            consent = indexed.get((host, name))
            need(consent is not None and consent.get('status') == 'confirmed', 'consent_missing_or_revoked')
            need(consent.get('terms_sha256') == TERMS_SHA and bool(re.fullmatch('[a-f0-9]{64}', str(consent.get('evidence_sha256', '')))), 'consent_evidence_missing')
            need(set(HEADERS) - {'partner_ok'} <= set(consent.get('fields', [])), 'consent_scope')
            need(iso_day(consent.get('granted_on')) <= today <= iso_day(consent.get('valid_through')), 'consent_date')
            need(age_limit is not None, 'freshness_policy_unset')
            updated = iso_day(item['updated_at'])
            need(0 <= (today - updated).days <= age_limit, 'future_or_stale_listing')
            deal = enum_value(item['deal'], DEALS)
            area = enum_value(item['area'], AREAS)
            prop = enum_value(item['type'], TYPES, {'apartment': 'condo', 'квартира': 'condo', 'кондо': 'condo'})
            beds = str(item['bedrooms'])
            need(type(item['bedrooms']) is not bool and bool(re.fullmatch(r'\d{1,2}', beds)), 'bedrooms_invalid')
            price = str(item['price_thb'])
            need(type(item['price_thb']) is not bool and bool(re.fullmatch(r'\d{1,12}(?:\.\d{1,2})?', price)), 'price_invalid')
            amount = int(Decimal(price) * 100)
            need(amount > 0, 'price_nonpositive')
            entry = {'deal': deal, 'area': area, 'type': prop, 'bedrooms': int(beds), 'price_minor': amount,
                     'title': text(item['title'], 160), 'source_name': name, 'source_url': url, 'updated_at': updated.isoformat()}
            # No monthly/nightly inference: the ten-column source has no period.
            entry['price_period'] = 'unspecified' if deal == 'rent' else 'total'
            entry['id'] = sha(canonical([name, url, deal]))[:20]
            accepted.append(entry)
        except (ValueError, TypeError, KeyError, OverflowError):
            import sys
            exc = sys.exc_info()[1]
            code = str(exc) if type(exc) is ValueError and str(exc) in {
                'row_width', 'partner_not_approved', 'https_required', 'url_format', 'domain_format', 'private_host', 'ip_host',
                'url_control_or_fragment', 'url_query_not_admitted', 'consent_missing_or_revoked', 'consent_evidence_missing',
                'consent_scope', 'consent_date', 'freshness_policy_unset', 'future_or_stale_listing', 'date_format',
                'unknown_enum', 'bedrooms_invalid', 'price_invalid', 'price_nonpositive', 'text_type', 'text_format'
            } else 'invalid_row'
            rejected[code] += 1
    grouped = defaultdict(list)
    for entry in accepted:
        grouped[entry['id']].append(entry)
    listings = []
    for entries in grouped.values():
        if len({canonical(x) for x in entries}) != 1:
            rejected['conflicting_duplicate'] += len(entries)
        else:
            listings.append(entries[0])
            rejected['exact_duplicate'] += len(entries) - 1
    rejected.pop('exact_duplicate', None) if rejected.get('exact_duplicate') == 0 else None
    listings.sort(key=lambda x: (-date.fromisoformat(x['updated_at']).toordinal(), x['id']))
    return {'schema': 'phuket-housing-public.v1', 'as_of': as_of, 'listings': listings,
            'counts': {'accepted': len(listings), 'excluded': dict(sorted(rejected.items()))},
            'authority': {'publish': False, 'deploy': False}}


def card(entry: dict, locale: str, island_path: str) -> str:
    need(locale in ('ru', 'en'), 'locale')
    en = locale == 'en'; lang = int(en); esc = lambda x: html.escape(str(x), quote=True)
    area = AREAS[entry['area']]
    price = f"{Decimal(entry['price_minor']) / 100:,.2f}".rstrip('0').rstrip('.') + ' THB'
    period = ('Payment period: see agency source.' if en else 'Период оплаты — у агентства-источника.') if entry['deal'] == 'rent' else ''
    label = 'Open agency listing' if en else 'На сайт агентства'
    beds_label = 'Bedrooms' if en else 'Спальни'
    return (f'<article class="u2-card" data-u2-card data-id="{entry["id"]}" data-deal="{entry["deal"]}" '
            f'data-area="{entry["area"]}" data-type="{entry["type"]}" data-beds="{entry["bedrooms"]}" data-price="{entry["price_minor"]}">'
            f'<svg class="u2-card-map" viewBox="0 0 360 440" aria-hidden="true"><path d="{esc(island_path)}"></path>'
            f'<circle cx="{area[2]}" cy="{area[3]}" r="10"></circle></svg><div>'
            f'<p class="u2-card-meta">{DEALS[entry["deal"]][lang]} · {area[lang]} · {TYPES[entry["type"]][lang]}</p>'
            f'<h3>{esc(entry["title"])}</h3><p>{beds_label}: {entry["bedrooms"]}</p><p class="u2-price">{price}</p>'
            f'<p>{period}</p><p>{esc(entry["source_name"])} · <time datetime="{entry["updated_at"]}">{entry["updated_at"]}</time></p>'
            f'<a href="{esc(entry["source_url"])}" rel="noopener">{label} ↗</a></div></article>')
