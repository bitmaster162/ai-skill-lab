"""Write a source-and-static patch for review. The active release is read-only."""
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
import sys

CANDIDATE = Path(__file__).resolve().parent
ROOT = CANDIDATE.parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_guides import render_markdown

SLUG = "ai-first-tasks-for-adults"
PAGES = {
    "ru": ("Проверка ответа: работа не заканчивается в чате",
           "5c5f8d8da100a8657aeefbe5d9044462095e92db341e240a37bdebae57bba61b",
           "580cc6096fe22e0a27d60543d7d3d93b8b61fd1db582511d31087c29fd57497c"),
    "en": ("Checking the answer: the work does not end in the chat",
           "b0bcd0a6b545d2d8d4b190e55ab9d3c76350a9a30a8e1c745fb23e04b48df671",
           "5831839b802f7755adaf8d17420e0b6cbc8ee5445713924b92dfa29c1325a20b"),
}


def read_pinned(path, digest):
    data = (ROOT / path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"{path} changed. Review the current input before preparing a new candidate.")
    return data.decode("utf-8")


def diff(path, original, updated):
    return "".join(unified_diff(original.splitlines(keepends=True), updated.splitlines(keepends=True),
                                fromfile="a/" + path, tofile="b/" + path))


def proposed_diff(locale, heading, source_sha, page_sha):
    source_path = f"guides/aiskillab/{SLUG}.{locale}.md"
    prefix = "en/" if locale == "en" else ""
    page_path = f"deploy/live/{prefix}guides/{SLUG}.html"
    source = read_pinned(source_path, source_sha)
    page = read_pinned(page_path, page_sha)

    frontmatter, markdown = source.split("\n---\n", 1)
    marker = f"## {heading}\n\n"
    if markdown.count(marker) != 1:
        raise ValueError(f"Missing unique section heading in {source_path}")
    exercise = (CANDIDATE / f"{locale}.md").read_text(encoding="utf-8").strip()
    revised = markdown.replace(marker, marker + exercise + "\n\n", 1)

    old_body = render_markdown(markdown)["body"]
    new_body = render_markdown(revised)["body"]
    if page.count(old_body) != 1:
        raise ValueError(f"The checked source no longer renders the article body in {page_path}")

    return (diff(source_path, source, frontmatter + "\n---\n" + revised)
            + diff(page_path, page, page.replace(old_body, new_body, 1)))


if __name__ == "__main__":
    patch = "".join(proposed_diff(locale, *page) for locale, page in PAGES.items())
    sys.stdout.buffer.write(patch.encode("utf-8"))
