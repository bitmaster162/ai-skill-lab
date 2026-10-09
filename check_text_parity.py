#!/usr/bin/env python3
"""Text/link/meta parity guard for the AI Skill Lab design rollout (stdlib only, GET-only).

The design rollout may change layout, markup and styles. It must NOT change what the page says:
visible text, image alt / aria-label texts, internal links, title, description, canonical, hreflang, H1.

  snapshot:  python3 check_text_parity.py snapshot --base https://aiskillab.work --out baseline.json
             python3 check_text_parity.py snapshot --dir deploy/live --out baseline.json
  compare:   python3 check_text_parity.py compare  --dir deploy/live --baseline baseline.json [--allow allow.json]
             python3 check_text_parity.py compare  --base https://aiskillab.work --baseline baseline.json

Moved text (same words, new position — e.g. sections reordered) is not a violation.
Approved additions live in an allow file (see allow_d1.json): phrases per language / per route and added links;
they are removed from both sides before the diff, so only unapproved text is reported.
Case, whitespace, quote and dash styles are normalized. Exit code 1 on any violation.
"""
import argparse, difflib, hashlib, json, os, re, sys, time, urllib.request
from html.parser import HTMLParser

ROUTES = ["/", "/about", "/build", "/business", "/challenge", "/curriculum", "/family", "/faq", "/kids", "/matcher",
          "/method", "/parents", "/personal", "/phuket", "/pricing", "/privacy", "/projects", "/proof", "/safety",
          "/start", "/studio", "/teens", "/terms"]
ROUTES = ROUTES + ["/en" if r == "/" else "/en" + r for r in ROUTES]
HOST = "aiskillab.work"
SKIP = {"script", "style", "noscript", "template"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.words_raw, self.attr_texts = [], [], []
        self.title, self.meta, self.canonical, self.hreflang, self.h1 = "", {}, "", {}, []
        self.links, self.lang, self._h1 = set(), "", None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html": self.lang = a.get("lang", "")
        if tag == "meta" and (a.get("name") or a.get("property")):
            self.meta[(a.get("name") or a.get("property")).lower()] = a.get("content", "")
        if tag == "link":
            rel = a.get("rel", "").lower()
            if rel == "canonical": self.canonical = a.get("href", "")
            if rel == "alternate" and a.get("hreflang"): self.hreflang[a["hreflang"]] = a.get("href", "")
        if tag == "a" and a.get("href"):
            h = a["href"].split("#")[0]
            if h.startswith("/") or HOST in h or h.startswith(("mailto:", "tel:", "http")): self.links.add(h)
        for k in ("alt", "aria-label", "placeholder", "title"):
            if a.get(k) and tag not in ("link", "meta"): self.attr_texts.append(f"{tag}[{k}]={norm(a[k])}")
        if tag == "h1": self._h1 = []
        if tag not in VOID: self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "h1" and self._h1 is not None:
            self.h1.append(norm(" ".join(self._h1))); self._h1 = None
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag: pass

    def handle_data(self, data):
        if any(t in SKIP for t in self.stack): return
        if "title" in self.stack and "svg" not in self.stack:
            self.title += data; return
        if self._h1 is not None: self._h1.append(data)
        self.words_raw.append(data)


def norm(s):
    s = s.replace(" ", " ").replace(" ", " ").replace(" ", " ").lower()
    s = re.sub(r"[«»“”„\"'’‘`]", "", s)
    s = re.sub(r"[—–‑−]", "-", s)
    return re.sub(r"\s+", " ", s).strip()


def parse(html):
    p = Page(); p.feed(html)
    words = norm(" ".join(p.words_raw)).split()
    return {"lang": p.lang, "title": norm(p.title), "description": norm(p.meta.get("description", "")),
            "canonical": p.canonical, "hreflang": p.hreflang, "h1": p.h1, "words": words,
            "attr_texts": sorted(set(p.attr_texts)), "links": sorted(p.links)}


def fetch(base, route):
    url = base.rstrip("/") + (route if route != "/" else "/")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 parity-guard"})
    for i in range(4):
        try:
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        except Exception:
            if i == 3: raise
            time.sleep(2)


def read_dir(d, route):
    f = "index.html" if route == "/" else ("en.html" if route == "/en" else route.lstrip("/") + ".html")
    return open(os.path.join(d, f), encoding="utf-8").read()


def load(args):
    out = {}
    for r in ROUTES:
        html = read_dir(args.dir, r) if args.dir else fetch(args.base, r)
        out[r] = parse(html)
    return out


def runs(opcodes, a, b, side):
    for tag, i1, i2, j1, j2 in opcodes:
        if side == "new" and tag in ("insert", "replace"): yield b[j1:j2]
        if side == "removed" and tag in ("delete", "replace"): yield a[i1:i2]


def significant(run):
    return len(run) >= 3 or any(re.search(r"\d|[$€₽฿%]", w) for w in run)


def lang_of(route):
    return "en" if route == "/en" or route.startswith("/en/") else "ru"


def strip_phrases(words, phrases):
    s = " " + " ".join(words) + " "
    for p in phrases:
        s = re.sub(r"(?<= )" + re.escape(p) + r"(?= )", " ", s)
    return s.split()


def compare(base, cur, allow):
    report, bad = {}, 0
    for r in ROUTES:
        A, B = base[r], cur[r]
        lg = lang_of(r)
        phrases = sorted({norm(x) for x in allow.get("phrases", {}).get(lg, []) + allow.get("route_phrases", {}).get(r, [])},
                         key=len, reverse=True)
        ok_links = set(allow.get("links", {}).get(lg, []) + allow.get("route_links", {}).get(r, []))
        a, b = strip_phrases(A["words"], phrases), strip_phrases(B["words"], phrases)
        sa, sb = " " + " ".join(a) + " ", " " + " ".join(b) + " "
        ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
        new = [" ".join(x) for x in runs(ops, a, b, "new") if significant(x) and (" " + " ".join(x) + " ") not in sa]
        rem = [" ".join(x) for x in runs(ops, a, b, "removed") if significant(x) and (" " + " ".join(x) + " ") not in sb]
        # E3.2: 26 RU pages are localized. Exact SHA of every word in rendered
        # body is stronger than ignoring arbitrary translated phrases; links,
        # metadata, H1 and accessible labels are still checked independently.
        pin = allow.get("approved_text_sha256", {}).get(r)
        observed = hashlib.sha256(" ".join(B["words"]).encode("utf-8")).hexdigest()
        text_sha_drift = pin is not None and observed != pin
        if pin is not None and not text_sha_drift:
            new, rem = [], []
        allowed_meta = set(allow.get("meta_changes", {}).get(r, []))
        meta = [k for k in ("lang", "title", "description", "canonical", "hreflang", "h1") if A[k] != B[k] and k not in allowed_meta]
        ok_removed_links = set(allow.get("removed_links", {}).get(r, []))
        links_rem = sorted(set(A["links"]) - set(B["links"]) - ok_removed_links)
        links_new = sorted(set(B["links"]) - set(A["links"]) - ok_links)
        ok_removed_attrs = set(allow.get("removed_attr_texts", {}).get(r, []))
        attr_rem = sorted(set(A["attr_texts"]) - set(B["attr_texts"]) - ok_removed_attrs)
        ok_attrs = set(allow.get("attr_texts", {}).get(r, []))
        attr_new = sorted(x for x in set(B["attr_texts"]) - set(A["attr_texts"]) if x not in ok_attrs and x.split("=", 1)[-1] not in phrases)
        item = {k: v for k, v in (("new_text", new), ("removed_text", rem), ("text_sha256_drift", [r] if text_sha_drift else []),
                                   ("meta_changed", meta), ("links_removed", links_rem),
                                   ("links_added", links_new), ("attr_removed", attr_rem), ("attr_added", attr_new)) if v}
        if item:
            report[r] = item; bad += 1
    return report, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["snapshot", "compare"])
    ap.add_argument("--base"); ap.add_argument("--dir"); ap.add_argument("--out"); ap.add_argument("--baseline"); ap.add_argument("--allow")
    args = ap.parse_args()
    if bool(args.base) == bool(args.dir): sys.exit("give exactly one of --base or --dir")
    cur = load(args)
    if args.mode == "snapshot":
        json.dump({"routes": cur}, open(args.out, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"snapshot: {len(cur)} routes -> {args.out}"); return
    base = json.load(open(args.baseline, encoding="utf-8"))["routes"]
    allow = json.load(open(args.allow, encoding="utf-8")) if args.allow else {}
    if args.dir:
        release_meta = json.load(open(os.path.join(args.dir, "_release.json"), encoding="utf-8"))
        if release_meta.get("release_id") in {"E3_4_AI_SAFETY_AUDIENCE_R1", "E3_5_HEADING_STRUCTURE_R1"}:
            route_pins = json.load(open(os.path.join(os.path.dirname(__file__), "data/e3_4_ru_route_sha_pins.json"), encoding="utf-8"))
            assert route_pins.get("release") == "E3_4_AI_SAFETY_AUDIENCE_R1"
            assert set(route_pins.get("routes", {})) == {"/personal", "/teens"}
            for route, item in route_pins["routes"].items():
                observed = hashlib.sha256(" ".join(cur[route]["words"]).encode("utf-8")).hexdigest()
                assert observed == item["d1_words_sha256"], f"E3.4 D1 exact text drift {route}"
                assert route in allow.get("approved_text_sha256", {}), f"E3.2 D1 inheritance missing {route}"
                allow["approved_text_sha256"][route] = item["d1_words_sha256"]
        if release_meta.get("release_id") == "E3_5_HEADING_STRUCTURE_R1":
            pins = json.load(open(os.path.join(os.path.dirname(__file__), "data/e3_5_heading_pins.json"), encoding="utf-8"))
            assert pins["release_id"] == "E3_5_HEADING_STRUCTURE_R1"
            route = "/pricing"
            expected = pins["routes"][route]["d1_words_sha256"]
            actual = hashlib.sha256(" ".join(cur[route]["words"]).encode("utf-8")).hexdigest()
            assert actual == expected, "E3.5 pricing visible word order/text SHA drift"
            assert route in allow.get("approved_text_sha256", {}), "E3.2 D1 /pricing pin missing"
            allow["approved_text_sha256"][route] = expected
    report, bad = compare(base, cur, allow)
    for r, item in report.items():
        print(f"\n## {r}")
        for k, v in item.items():
            for x in (v if isinstance(v, list) else [v]):
                print(f"  {k}: {x[:220] if isinstance(x, str) else x}")
    print(f"\nPARITY {'OK' if not bad else 'FAIL'}: {len(ROUTES) - bad}/{len(ROUTES)} routes unchanged in text, links and meta")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
