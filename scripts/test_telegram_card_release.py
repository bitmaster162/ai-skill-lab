"""Protect direct-contact and prefilled-brief semantics in each language."""
from html.parser import HTMLParser
import subprocess
import sys
from urllib.parse import parse_qs, urlsplit
import xml.etree.ElementTree as ET

import telegram_card_release as release
from diagnostic_intent_release import historical_workspace


class ContactLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.direct = []
        self.briefs = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        values = dict(attrs)
        classes = values.get("class", "").split()
        if "channel" in classes:
            self.direct.append(values["href"])
        if "briefSendLink" in classes:
            self.briefs.append(values["href"])


def rejects(reason, **inputs):
    try:
        release.verify(**inputs)
    except ValueError as exc:
        assert reason in str(exc), str(exc)
    else:
        raise AssertionError("Admitted an invalid release: " + reason)


def sitemap_dates(xml):
    return {row.findtext("{*}loc"): row.findtext("{*}lastmod")
            for row in ET.fromstring(xml).findall("{*}url")}


release.verify()
direct = ["https://t.me/BiTFormer", "mailto:robert@aiskillab.work",
          "https://wa.me/66649701204", "https://line.me/ti/p/~iwf555"]
for page, (old_label, new_label) in release.LABELS.items():
    html = (release.LIVE / page).read_text(encoding="utf-8")
    card = f"<span>Telegram</span><strong>{new_label}</strong>"
    assert html.count(card) == 1 and old_label not in html
    old, new = ContactLinks(), ContactLinks()
    old.feed(release.original("deploy/live/" + page).decode("utf-8"))
    new.feed(html)
    assert new.direct == old.direct == direct
    assert new.briefs == old.briefs and len(set(new.briefs)) == len(new.briefs) == 5
    for url in new.briefs:
        split = urlsplit(url)
        assert (split.scheme, split.netloc, split.path) == ("https", "t.me", "/BiTFormer")
        assert parse_qs(split.query)["text"][0].strip()
    old_card = f"<span>Telegram</span><strong>{old_label}</strong>"
    rejects("static " + page, file_overrides={page: html.replace(card, old_card, 1).encode()})
    rejects("static " + page, file_overrides={page: html.replace("BiTFormer?text=", "BiTFormer?", 1).encode()})

previous_xml = release.original("deploy/live/sitemap.xml")
old, new = sitemap_dates(previous_xml), sitemap_dates((release.LIVE / "sitemap.xml").read_bytes())
assert len(old) == len(new) == 56 and old.keys() == new.keys()
changed = {url for url in old if new[url] != old[url]}
assert changed == {"https://aiskillab.work/start", "https://aiskillab.work/en/start"}
assert all(new[url] == release.DATE for url in changed)
rejects("static sitemap.xml", file_overrides={"sitemap.xml": previous_xml})
rejects("manifest digest", manifest_override=release.original("deploy/live/_release.json"))
for path in release.SOURCE_SHA:
    rejects("source " + path, source_overrides={path: release.original(path)})
rejects("unknown file", file_overrides={"not-in-release.html": b""})
rejects("static safety.html", file_overrides={"safety.html": b"changed"})

# Run #249's original test, including its historical sitemap and diagnostic tests,
# on the exact commit each release admitted.
files = ["deploy/live", "scripts", *release.previous.previous.SOURCE_SHA, *release.previous.SOURCE_CHANGES]
with historical_workspace(release.PARENT_COMMIT, files) as root:
    subprocess.run([sys.executable, "-B", "scripts/test_certificate_donor_release.py"], cwd=root, check=True)
print("Direct Telegram contact verified in RU/EN; five prefilled links per locale; 109 assets preserved.")
