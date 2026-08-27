from __future__ import annotations

import os
from urllib.parse import urlsplit

DEFAULT_PUBLIC_ORIGIN = "https://ai-skill-lab.vercel.app"


def normalize_public_origin(value: str) -> str:
    value = value.strip().rstrip("/")
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise RuntimeError(f"invalid public origin: {value!r}")
    return f"https://{parsed.netloc.lower()}"


PUBLIC_ORIGIN = normalize_public_origin(
    os.environ.get("NEXT_PUBLIC_SITE_URL", DEFAULT_PUBLIC_ORIGIN)
)
