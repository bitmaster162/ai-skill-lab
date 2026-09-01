#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy/live"
problems = []
checks = 0


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.current = None
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        values = dict(attrs)
        self.current = {
            "href": (values.get("href") or "").strip(),
            "text": [],
        }

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"].append(data)

    def handle_endtag(self, tag):
        if tag.lower() != "a" or self.current is None:
            return
        text = " ".join("".join(self.current["text"]).split())
        self.anchors.append((self.current["href"], text))
        self.current = None


def anchors_for(path):
    parser = AnchorParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.anchors


for path in sorted(LIVE.rglob("*.html")):
    rel = path.relative_to(ROOT).as_posix()
    for href, text in anchors_for(path):
        label = text.casefold()
        if "telegram" in label:
            checks += 1
            if not href.startswith("https://t.me/"):
                problems.append(
                    f"{rel} labels Telegram but href={href!r}: {text!r}"
                )
        if href in {"/start", "/en/start"}:
            checks += 1
            if "telegram" in label:
                problems.append(
                    f"{rel} internal Start CTA masquerades as direct Telegram: {text!r}"
                )

for rel in ("deploy/live/start.html", "deploy/live/en/start.html"):
    direct = [
        href
        for href, _text in anchors_for(ROOT / rel)
        if href.startswith("https://t.me/")
    ]
    checks += 1
    if not direct:
        problems.append(f"{rel} missing direct Telegram action")

print(f"cta_semantics_checks={checks}")
if problems:
    for problem in problems:
        print("FAIL:", problem)
    sys.exit(1)
print("CTA_SEMANTICS_PASS")
