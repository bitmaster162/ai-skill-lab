"""Write the proposed RU and EN page diff to stdout without modifying the release."""
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
import sys

CANDIDATE = Path(__file__).resolve().parent
ROOT = CANDIDATE.parents[2]
SLUG = "ai-first-tasks-for-adults"
PAGES = {
    "ru": (f"guides/{SLUG}.html", "580cc6096fe22e0a27d60543d7d3d93b8b61fd1db582511d31087c29fd57497c"),
    "en": (f"en/guides/{SLUG}.html", "5831839b802f7755adaf8d17420e0b6cbc8ee5445713924b92dfa29c1325a20b"),
}


def proposed_diff(locale, route, digest):
    path = f"deploy/live/{route}"
    original = (ROOT / path).read_bytes()
    if sha256(original).hexdigest() != digest:
        raise ValueError(f"{path} changed. Review the current page before preparing a new candidate.")

    text = original.decode("utf-8")
    heading = '<h2 id="section-4">'
    if text.count(heading) != 1:
        raise ValueError(f"{path} must contain a single section-4 heading.")
    start = text.index("</h2>\n", text.index(heading)) + len("</h2>\n")
    fragment = (CANDIDATE / f"{locale}.html").read_text(encoding="utf-8")
    updated = text[:start] + fragment + text[start:]
    return "".join(unified_diff(text.splitlines(keepends=True), updated.splitlines(keepends=True),
                                fromfile="a/" + path, tofile="b/" + path))


if __name__ == "__main__":
    patch = "".join(proposed_diff(locale, *page) for locale, page in PAGES.items())
    sys.stdout.buffer.write(patch.encode("utf-8"))
