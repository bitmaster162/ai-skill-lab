#!/usr/bin/env python3
"""Exact inline-script CSP digests via an HTML parser, not a tag-filtering regex.

Script text is hashed as UTF-8 without whitespace or entity normalization.
External scripts are identified by the parsed 'src' attribute (case-insensitive).
A malformed or unclosed script causes a fail-closed error.
"""
from __future__ import annotations

import base64
import hashlib
from html.parser import HTMLParser


class _Scripts(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.hashes: set[str] = set()
        self.parts: list[str] | None = None
        self.external = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        if self.parts is not None:
            raise ValueError("nested script element")
        self.parts = []
        self.external = any(name == "src" for name, _ in attrs)

    def handle_data(self, data: str) -> None:
        if self.parts is not None:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "script":
            return
        if self.parts is None:
            raise ValueError("unmatched script end tag")
        body = "".join(self.parts)
        if not self.external and body.strip():
            digest = hashlib.sha256(body.encode("utf-8")).digest()
            self.hashes.add("'sha256-" + base64.b64encode(digest).decode("ascii") + "'")
        self.parts = None
        self.external = False

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            raise ValueError("self-closing script element is not admitted")
        super().handle_startendtag(tag, attrs)


def inline_script_hashes(document: str) -> set[str]:
    if not isinstance(document, str):
        raise TypeError("HTML source must be text")
    parser = _Scripts()
    parser.feed(document)
    parser.close()
    if parser.parts is not None:
        raise ValueError("unclosed script element")
    return parser.hashes
