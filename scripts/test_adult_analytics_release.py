"""Release-identity, excluded-page, inherited-payload and disclosure tamper fixtures."""
import json

import adult_analytics_release as release


def rejects(contains, **fixture):
    try:
        release.verify(**fixture)
    except ValueError as error:
        assert contains in str(error), error
    else:
        raise AssertionError("tamper accepted: " + contains)


assert release.active()
manifest = release.verify()
raw = (release.LIVE / "_release.json").read_bytes()
rejects("manifest digest", manifest_override=raw + b" ")
wrong_parent = {**manifest, "parent_manifest_sha256": "0" * 64}
rejects("manifest digest", manifest_override=json.dumps(wrong_parent).encode())
for name in ("en/business.html", "teens.html", "en/privacy.html", "analytics/preferences.js"):
    original = (release.LIVE / name).read_bytes()
    rejects("static byte " + name, file_overrides={name: original + b" "})
rejects("unknown file", file_overrides={"unexpected.htm": b""})
print(f"Adult analytics release verified: {manifest['file_count']} assets, four eligible routes, seven negative fixtures")
