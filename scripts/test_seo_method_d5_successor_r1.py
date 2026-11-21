"""Negative fixtures for exact, draft-only method D5 successor."""
from pathlib import Path
import json
from seo_method_d5_successor_r1 import CandidateDeny, verified_source_main, SOURCES, FOLDER, ARCHIVE_SHA

ROOT = Path(__file__).resolve().parents[1]
approved = verified_source_main(ROOT)
assert set(approved) == set(SOURCES)
for rel, expected in approved.items():
    assert expected == SOURCES[rel][2]

denied = 0
for name in SOURCES:
    source_path = ROOT / SOURCES[name][0]
    wrong = source_path.read_bytes().replace(b"method-example", b"method-changed", 1)
    assert wrong != source_path.read_bytes()
    try:
        verified_source_main(ROOT, sources_override={name: wrong})
    except CandidateDeny as e:
        assert "SOURCE_SHA" in str(e)
        denied += 1
    else:
        raise AssertionError("Modified source passed " + name)

archive = (ROOT / FOLDER / "review.zip").read_bytes()
assert len(archive) > 1000 and ARCHIVE_SHA
for wrong in (archive[:-1] + bytes([archive[-1] ^ 1]), archive[:-1]):
    try:
        verified_source_main(ROOT, zip_override=wrong)
    except CandidateDeny as e:
        assert "ARCHIVE_SHA" in str(e)
        denied += 1
    else:
        raise AssertionError("Modified archive passed")
assert denied == 4
print("SEO_METHOD_D5_EXACT_SUCCESSOR=PASS sources=2 full_static=108 fail_closed_fixtures=4 old_release=IMMUTABLE approval=NONE")
