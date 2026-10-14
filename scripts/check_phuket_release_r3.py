#!/usr/bin/env python3
"""Read-only R3 integrity, alternative layout, and source/static parity gate."""
from pathlib import Path
import json
from phuket_release_profile import active, verify_integrity, universe_page, ROOT, LIVE, UNIVERSE_FILES, profile, sha

def main():
    import phuket_universe_r7_release_profile as universe_r7
    if universe_r7.active():
        result = universe_r7.check_release()
        from test_phuket_universe_r7 import run_units
        run_units()
        print("PHUKET_R7_PROFILE_PASS " + json.dumps(result, sort_keys=True))
        return 0
    import phuket_housing_release_profile as housing_r6
    if housing_r6.active():
        result = housing_r6.check_release()
        from test_phuket_housing_release_r6 import run_units
        run_units()
        print("PHUKET_R6_PROFILE_PASS " + json.dumps(result, sort_keys=True))
        return 0
    import phuket_agency_release_profile as agency_r5
    if agency_r5.active():
        result = agency_r5.check_release()
        from test_phuket_agency_release_r5 import run_units
        run_units()
        print("PHUKET_R5_PROFILE_PASS " + json.dumps(result, sort_keys=True))
        return 0
    if not active():
        print("PHUKET_R3_NOT_APPLICABLE")
        return 0
    result = verify_integrity()
    from build_phuket_release_r3 import render
    actual = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob("*") if p.is_file()}
    if render() != actual:
        raise ValueError("R3 immutable-parent/source reproduction mismatch")
    text = (ROOT / "components/phuketUniverseMarkup.ts").read_text(encoding="utf-8")
    markup = json.loads(text.split("export const phuketUniverseMarkup = ", 1)[1].rsplit(" as const;", 1)[0])
    for name in sorted(UNIVERSE_FILES):
        path = LIVE / name
        if not universe_page(path):
            raise ValueError("Unvalidated alternate shell")
        locale = "en" if name.startswith("en/") else "ru"
        if markup[locale] not in path.read_text(encoding="utf-8"):
            raise ValueError("Source/static markup mismatch")
    for name, digest in profile()["source_override_sha256"].items():
        if sha((ROOT / name).read_bytes()) != digest:
            raise ValueError("R3 reviewed source pin changed: " + name)
    from test_phuket_release_r3 import run_units
    run_units()
    print("PHUKET_R3_PROFILE_PASS " + json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
