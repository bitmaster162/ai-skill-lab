"""Phuket Universe rental-search plan R1: isolated editorial candidate, RU/EN.
No changes to the working tree, live release, manifest, inventory or runtime.
Run: python build_candidate.py --repo <checkout> [--output <new directory outside repo>]
Without --output, performs structural QA and prints JSON. New release review,
source/static parity, browser QA and owner approval are required before integration.
"""
from __future__ import annotations
import argparse, hashlib, html, json, subprocess
from html.parser import HTMLParser
from pathlib import Path

BASE = "b76fbcf4c42104a057c80d6a6a59df9d936b039a"
RELEASE = "AISL_RESTORED_GUIDES_R1_20261122"
PAYLOAD = "f11a64758e9c5661eea55a24b9a98c6c078e17dcdfca8e335bd04c23776d99e5"
PAGES = {
    "ru": ("phuket-universe.html", "2b7c61e013d25815d27b98bb64db9357a64c36a7ec2e6c53a5dfc0ccf357de3a"),
    "en": ("en/phuket-universe.html", "74f02c92d9595673c289b6dc714a32c8fa099f565fa7272194967fd6befdb9ba"),
}
CSS_PIN = "c362ad0aa48033ad465c976619fb0d5a315610baf99e7b8caa2532e18ea6b287"
ANCHOR = '<section class="pu-s039" id="agencies">'
ID = "rental-search-plan"
TITLE = ID + "-title"
COPY = {
 "ru": ("Перед поиском", "План поиска жилья",
        "Четыре шага перед подбором долгосрочной аренды. Даже если каталог пока пуст, можно определить свои критерии.",
        (
         ("Район и маршруты", "Сравните дорогу до работы, школы и повседневных мест. Выберите район и запасной вариант."),
         ("Полный месячный бюджет", "Сложите аренду и отдельно оплачиваемые услуги. Депозит и разовые платежи считайте отдельно."),
         ("Срок и условия", "Уточните ставку именно на 6 или 12 месяцев, размер депозита и условия возврата."),
         ("Проверка источника", "Перед решением уточните текущую доступность, цену и условия на сайте агентства. Старая карточка не подтверждает наличие."),
        ), "Перейти к фильтрам жилья", "Подборка не является бронью. Наличие, цена и условия требуют подтверждения у источника."),
 "en": ("Before you search", "Plan your rental search",
        "Four steps before comparing long-term rentals. You can define your criteria even while the catalogue is empty.",
        (
         ("Area and daily routes", "Compare journeys to work, school and everyday places. Choose a preferred area and a backup."),
         ("Total monthly budget", "Add rent and separately billed services. Count the deposit and one-off charges separately."),
         ("Term and conditions", "Check the rate for the exact 6- or 12-month term, the deposit and its return conditions."),
         ("Check the source", "Before deciding, confirm current availability, price and terms on the agency's site. An old card is not confirmation."),
        ), "Go to housing filters", "A shortlist is not a reservation. Availability, price and terms need confirmation at the source."),
}

def need(ok, msg):
    if not ok:
        raise ValueError(msg)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

class Tags(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(source)
        self.close()
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

def section(locale):
    label, title, intro, steps, cta, note = COPY[locale]
    e = html.escape
    items = "\n".join(
        '<li class="pu-s103"><span class="pu-s104" aria-hidden="true">'
        + str(i) + '</span><div class="pu-s072"><strong class="pu-s105">'
        + e(head) + '</strong><span class="pu-s106">' + e(body) + '</span></div></li>'
        for i, (head, body) in enumerate(steps, 1))
    return (
        f'<section class="pu-s039" id="{ID}" aria-labelledby="{TITLE}">\n'
        '<div class="pu-s096 pu-pad"><div class="pu-s097">\n'
        '<div class="pu-s098"><span class="pu-s014">' + e(label) + '</span>\n'
        f'<h2 class="pu-s099" id="{TITLE}">' + e(title) + '</h2>\n'
        '<p class="pu-s044">' + e(intro) + '</p>\n'
        '<a class="pu-s082" href="#homes">' + e(cta) + '</a>\n'
        '<p class="pu-s095">' + e(note) + '</p></div>\n'
        '<ol class="pu-s102" role="list">\n' + items + '\n</ol>\n'
        '</div></div>\n</section>\n\n')

def validate_and_build(read):
    manifest = json.loads(read("deploy/live/_release.json"))
    need(manifest["release_id"] == RELEASE and manifest["payload_sha256"] == PAYLOAD, "parent release")
    entries = {v["path"]: v for v in manifest["files"]}
    need(len(entries) == len(manifest["files"]) == 116, "parent inventory")
    css = read("deploy/live/phuket-universe.css")
    need(sha(css) == CSS_PIN == entries["phuket-universe.css"]["sha256"], "CSS pin")
    output = {}
    report = {"base": BASE, "parent_release": RELEASE, "scope": "DRAFT_ONLY", "pages": {}}
    for locale, (path, pin) in PAGES.items():
        raw = read("deploy/live/" + path)
        need(sha(raw) == pin == entries[path]["sha256"] and len(raw) == entries[path]["size"], "parent page")
        old = raw.decode("utf-8")
        need(old.count(ANCHOR) == 1 and ID not in old, "unique insertion point")
        frag = section(locale)
        tags = Tags(frag).tags
        need(sum(t == "li" for t, _ in tags) == 4, "four steps")
        need([(t, a["href"]) for t, a in tags if "href" in a] == [("a", "#homes")], "local CTA")
        need(not any(t in {"script","style","form","input","button","iframe","img","link"} for t, _ in tags), "no active content")
        need(not any(any(k.startswith(("on","data-")) or k == "style" for k in a) for _, a in tags), "no hooks")
        need(all(("." + c).encode() in css for _, a in tags for c in a.get("class","").split()), "existing CSS")
        need(sum(t == "h2" and a.get("id") == TITLE for t, a in tags) == 1, "heading")
        new = old.replace(ANCHOR, frag + ANCHOR, 1)
        need(new.replace(frag, "", 1).encode() == raw, "parent byte preservation")
        before, after = Tags(old).tags, Tags(new).tags
        need([a.get("id") for t,a in after if t=="section"] == ["top","orbit","homes",ID,"agencies"], "section order")
        ids = [a["id"] for _,a in after if "id" in a]
        need(ids.count(ID) == ids.count(TITLE) == ids.count("homes") == 1, "unique IDs")
        need(sum("data-u2-catalog" in a for _,a in after) == 1 and not any("data-u2-card" in a for _,a in after), "empty catalogue")
        need([(t,a) for t,a in before if t in {"script","form","link"}] == [(t,a) for t,a in after if t in {"script","form","link"}], "unchanged active assets")
        payload = new.encode("utf-8")
        output[path] = payload
        report["pages"][locale] = {"path": path,"parent_sha256":pin,"candidate_sha256":sha(payload),"added_bytes":len(payload)-len(raw),"checks":"PASS_STRUCTURE"}
    return output, report

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    repo = args.repo.resolve()
    git = lambda *a: subprocess.check_output(["git","-C",str(repo),*a])
    need(git("rev-parse",BASE+"^{commit}").decode().strip()==BASE, "Git baseline")
    output, report = validate_and_build(lambda path: git("show",BASE+":"+path))
    if args.output is not None:
        dest = args.output.resolve()
        need(dest != repo and repo not in dest.parents and not dest.exists(), "new output outside repo required")
        dest.mkdir(parents=True,exist_ok=False)
        for name,raw in output.items():
            file=dest/name
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_bytes(raw)
        (dest/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__ == "__main__":
    main()
