#!/usr/bin/env python3
from __future__ import annotations

from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "live"
PUBLIC = ROOT / "public"
HELPER = ROOT / "lib" / "og-assets.ts"

PAGES = {
    "home": {
        "ru_alt": "Освойте AI так, чтобы результат остался у вас.",
        "en_alt": "Learn AI so the capability stays with you.",
        "ru_file": "index.html", "en_file": "en.html",
        "ru_src": "app/(ru)/page.tsx", "en_src": "app/(en)/en/page.tsx",
    },
    "pricing": {
        "ru_alt": "Знайте цену. Фиксируйте scope.",
        "en_alt": "Know the price. Define the scope.",
        "ru_file": "pricing.html", "en_file": "en/pricing.html",
        "ru_src": "app/(ru)/pricing/page.tsx", "en_src": "app/(en)/en/pricing/page.tsx",
    },
    "start": {
        "ru_alt": "Сначала fit. Потом программа.",
        "en_alt": "Fit first. Program second.",
        "ru_file": "start.html", "en_file": "en/start.html",
        "ru_src": "app/(ru)/start/page.tsx", "en_src": "app/(en)/en/start/page.tsx",
    },
    "kids": {
        "ru_alt": "AI — не кнопка «сделай за меня».",
        "en_alt": "AI is not a button that does it for you.",
        "ru_file": "kids.html", "en_file": "en/kids.html",
        "ru_src": "app/(ru)/kids/page.tsx", "en_src": "app/(en)/en/kids/page.tsx",
    },
    "teens": {
        "ru_alt": "Не просто пользоваться AI. Собирать и объяснять.",
        "en_alt": "Do more than use AI. Build it. Explain it.",
        "ru_file": "teens.html", "en_file": "en/teens.html",
        "ru_src": "app/(ru)/teens/page.tsx", "en_src": "app/(en)/en/teens/page.tsx",
    },
    "parents": {
        "ru_alt": "Платить не за «ребёнок поиграл с AI».",
        "en_alt": "Do not pay for “my child played with AI.”",
        "ru_file": "parents.html", "en_file": "en/parents.html",
        "ru_src": "app/(ru)/parents/page.tsx", "en_src": "app/(en)/en/parents/page.tsx",
    },
    "personal": {
        "ru_alt": "Не курс про AI, а ваш рабочий процесс.",
        "en_alt": "Not a course about AI. Your own working system.",
        "ru_file": "personal.html", "en_file": "en/personal.html",
        "ru_src": "app/(ru)/personal/page.tsx", "en_src": "app/(en)/en/personal/page.tsx",
    },
    "business": {
        "ru_alt": "Не «добавить AI». Изменить один процесс.",
        "en_alt": "Do not add AI. Change one process.",
        "ru_file": "business.html", "en_file": "en/business.html",
        "ru_src": "app/(ru)/business/page.tsx", "en_src": "app/(en)/en/business/page.tsx",
    },
    "phuket": {
        "ru_alt": "Локально на Phuket. И без географии online.",
        "en_alt": "Local in Phuket. Borderless online.",
        "ru_file": "phuket.html", "en_file": "en/phuket.html",
        "ru_src": "app/(ru)/phuket/page.tsx", "en_src": "app/(en)/en/phuket/page.tsx",
    },
    "faq": {
        "ru_alt": "Одиннадцать ответов до разговора.",
        "en_alt": "Eleven answers before the call.",
        "ru_file": "faq.html", "en_file": "en/faq.html",
        "ru_src": "app/(ru)/faq/page.tsx", "en_src": "app/(en)/en/faq/page.tsx",
    },
}

EXPECTED_SHA = {
    "og-en-business.png": "ea2e5fe1a2707b1875685bc231c95898988498701d819f0c54d247fe22b8a551",
    "og-en-faq.png": "7c34e4daa11b6bfc4699deb0c3a2a3fa14c54d9fd914be50ca4303d88125a55c",
    "og-en-home.png": "302cdb4cecbc76d5dba39338bb2c386d0db12fa25e6f69041b72c31596199eb8",
    "og-en-kids.png": "f4248b79cbfd65d15c30a903accee50da3bb21e9c2cbb1c6da74d0aadb195918",
    "og-en-parents.png": "de603bccb599389f9fde47434985521bcd4a406fdb2969246d184e1e26e6ab1f",
    "og-en-personal.png": "3d0047a49199ec4d5732c21f9eae07231c565e0514acf85724da65974c65f56f",
    "og-en-phuket.png": "476dad46df2d7b13bf797c382256f7f9c1b109ede651cb8e5248eed8f21399db",
    "og-en-pricing.png": "d4a4cfeaa09be3e424a2a1c2dfb90a62962bc0a116723ee7e7b66eaf8df506e2",
    "og-en-start.png": "8526784e01f7f718a184d7e80a4d680a894ff9c64f4bc5196b6a078ee43993d2",
    "og-en-teens.png": "d214837b837fbc909e8159643125a92aca4ed9ba3ea4a4daa9172b86a9a1304e",
    "og-ru-business.png": "cc4d2737c32b80abae1bb5a318e83198dc3054df1b210a519337e27f547804e6",
    "og-ru-faq.png": "60362a7fa06131799ffbfdcda11030e775e8daef8bcc22799bd9adc3bc0bd6e0",
    "og-ru-home.png": "636fdf86ef13749514f8b03c2df8913e66c97bc91f3d2f8fb4006dadcf79fefa",
    "og-ru-kids.png": "280686326263971116903712f8330763c4cb1fe9fca1a1c23745ac414bcf4972",
    "og-ru-parents.png": "8ccd91bde923c719992d06df6df77615cf8746682f6c4c21555a45dbc0ff1a5c",
    "og-ru-personal.png": "ceaa3de7f42ee1c574877be557d5655e724a1c5408979a7d5856c9b2467b3771",
    "og-ru-phuket.png": "6011b07763303074990e6fdbcb5809ef8c8d8094b5440404fa9540e649c0644b",
    "og-ru-pricing.png": "c1a1fee223e67774bb66f62ee7b523b6b79f3081eba1f8b7addb074ab09d705d",
    "og-ru-start.png": "7a695ab6b7eaf1916c7ad049f93ab327da7b0786a5fdd34f436cad682dbf39b6",
    "og-ru-teens.png": "33b9eb38381e28d501aec3e7c027bafcc18c6e89de782f400ae145f17f3b5808",
}

class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "meta":
            return
        a = {k: (v or "") for k, v in attrs}
        key = a.get("property") or a.get("name")
        if key:
            self.meta[key] = a.get("content", "")

def png_dimensions(data: bytes) -> tuple[int, int]:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG with IHDR")
    return struct.unpack(">II", data[16:24])

def main() -> int:
    errors: list[str] = []
    checks = 0
    helper = HELPER.read_text(encoding="utf-8")
    checks += 1
    if helper.count("export function ogPageMetadata") != 1:
        errors.append("source helper missing or duplicated")

    asset_bytes = 0
    hashes: set[str] = set()
    for name, expected_sha in sorted(EXPECTED_SHA.items()):
        public = PUBLIC / name
        live = LIVE / name
        for path in (public, live):
            checks += 1
            if not path.is_file():
                errors.append(f"missing asset {path.relative_to(ROOT)}")
                continue
            data = path.read_bytes()
            asset_bytes += len(data) if path == live else 0
            checks += 1
            try:
                dims = png_dimensions(data)
            except ValueError as exc:
                errors.append(f"{path.relative_to(ROOT)}: {exc}")
                continue
            if dims != (1200, 630):
                errors.append(f"{path.relative_to(ROOT)} dimensions={dims}")
            digest = sha256(data).hexdigest()
            checks += 1
            if digest != expected_sha:
                errors.append(f"{path.relative_to(ROOT)} sha256={digest} expected={expected_sha}")
            if path == live:
                hashes.add(digest)
        if public.is_file() and live.is_file():
            checks += 1
            if public.read_bytes() != live.read_bytes():
                errors.append(f"source/static asset mismatch {name}")

    checks += 2
    if len(EXPECTED_SHA) != 20:
        errors.append(f"asset inventory={len(EXPECTED_SHA)} expected=20")
    if len(hashes) != 20:
        errors.append(f"unique live hashes={len(hashes)} expected=20")

    target_files: set[str] = set()
    for slug, spec in PAGES.items():
        for locale in ("ru", "en"):
            alt = spec[f"{locale}_alt"]
            filename = f"og-{locale}-{slug}.png"
            image = f"https://aiskillab.work/{filename}"
            static_rel = spec[f"{locale}_file"]
            source_rel = spec[f"{locale}_src"]
            target_files.add(static_rel)

            parser = MetaParser()
            parser.feed((LIVE / static_rel).read_text(encoding="utf-8"))
            expected_meta = {
                "og:image": image,
                "og:image:alt": alt,
                "og:image:width": "1200",
                "og:image:height": "630",
                "twitter:image": image,
                "twitter:card": "summary_large_image",
            }
            for key, value in expected_meta.items():
                checks += 1
                if parser.meta.get(key) != value:
                    errors.append(f"{static_rel}: {key}={parser.meta.get(key)!r} expected={value!r}")

            source = (ROOT / source_rel).read_text(encoding="utf-8")
            checks += 3
            if 'import { ogPageMetadata } from "@/lib/og-assets";' not in source:
                errors.append(f"{source_rel}: helper import missing")
            marker = f'ogPageMetadata({{ locale: "{locale}", slug: "{slug}"'
            if source.count(marker) != 1:
                errors.append(f"{source_rel}: helper call count={source.count(marker)}")
            if f'{slug}: "{alt}"' not in helper:
                errors.append(f"helper alt mapping missing {locale}/{slug}")

    # Scope guard: representative routes outside OG20 stay on generic OG.
    generic = ["about.html", "guides.html", "en/about.html", "en/guides.html"]
    for rel in generic:
        parser = MetaParser()
        parser.feed((LIVE / rel).read_text(encoding="utf-8"))
        checks += 2
        if parser.meta.get("og:image") != "https://aiskillab.work/og.png":
            errors.append(f"{rel}: generic og:image changed")
        if parser.meta.get("twitter:image") != "https://aiskillab.work/og.png":
            errors.append(f"{rel}: generic twitter:image changed")

    checks += 2
    if asset_bytes != 182808:
        errors.append(f"live OG20 bytes={asset_bytes} expected=182808")
    if not (LIVE / "og.png").is_file() or not (PUBLIC / "og.png").is_file():
        errors.append("generic og.png must remain")

    print(f"OG20_R1_CHECK checks={checks} assets=20 target_routes=20 generic_scope=4 asset_bytes={asset_bytes}")
    if errors:
        print("OG20_R1_FAIL")
        for error in errors:
            print("-", error)
        return 1
    print("OG20_R1_PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
