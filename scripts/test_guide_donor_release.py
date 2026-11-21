"""Semantic and tamper regression fixtures for the two new crawler-visible donor links."""
from html.parser import HTMLParser
import json

import guide_donor_release as donor


class Links(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.rows = []
        self.current = None
        self.feed(body.decode())
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            assert self.current is None, "nested anchor"
            self.current = [tuple(attrs), ""]

    def handle_data(self, text):
        if self.current is not None:
            self.current[1] += text

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.rows.append(self.current)
            self.current = None


def reject(reason, **fixture):
    try:
        donor.verify(**fixture)
    except ValueError as error:
        assert reason in str(error), str(error)
    else:
        raise AssertionError("Accepted a tampered release: " + reason)


manifest = donor.verify()
tested = {
    "index.html": ("/guides/ai-first-tasks-for-adults", "первые практические задачи для взрослых"),
    "en/method.html": ("/en/guides/ai-first-tasks-for-adults", "practical AI tasks for adults"),
}
for rel, (href, label) in tested.items():
    body = (donor.LIVE / rel).read_bytes()
    before = Links(donor.parent_blob("deploy/live/" + rel)).rows
    after = Links(body).rows
    matches = [a for a in after if dict(a[0]).get("href") == href]
    assert len(matches) == 1 and matches[0][1] == label
    assert [a for a in after if a not in matches] == before, "existing anchor or CTA changed"
    assert (donor.LIVE / (href.lstrip("/") + ".html")).is_file()
    reject("static byte " + rel, file_overrides={rel: body.replace(href.encode(), b"/wrong-locale", 1)})
reject("manifest digest", manifest_override=json.dumps({**manifest, "parent_manifest_sha256": "0" * 64}).encode())
reject("unknown file", file_overrides={"other.html": b""})
for rel in ("sitemap.xml", "analytics/preferences.js", "en/start.html"):
    reject("static byte " + rel, file_overrides={rel: (donor.LIVE / rel).read_bytes() + b" "})
for rel in ("lib/guides.ts", "app/(en)/en/method/page.tsx"):
    reject("source " + rel, source_overrides={rel: (donor.ROOT / rel).read_bytes() + b" "})
print("Guide donor release verified: 2 additions, prior anchors preserved, 9 tamper fixtures")
