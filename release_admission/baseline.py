"""T1.5 public-route baseline, transcribed from read-only GitHub main.

No filesystem, network, or write operations.
"""
from __future__ import annotations
import hashlib

_ORIGINAL_BASELINE = """
/
/about
/build
/business
/certificate
/challenge
/curriculum
/en
/en/about
/en/build
/en/business
/en/certificate
/en/challenge
/en/curriculum
/en/family
/en/faq
/en/guides
/en/guides/ai-safety-for-kids
/en/kids
/en/matcher
/en/method
/en/parents
/en/personal
/en/phuket
/en/pricing
/en/privacy
/en/projects
/en/proof
/en/safety
/en/start
/en/studio
/en/teens
/en/terms
/family
/faq
/guides
/guides/ai-safety-for-kids
/kids
/matcher
/method
/parents
/personal
/phuket
/pricing
/privacy
/projects
/proof
/safety
/start
/studio
/teens
/terms
"""
BASELINE_ROUTES = frozenset(_ORIGINAL_BASELINE.strip().splitlines())


def route_digest(routes: set[str] | frozenset[str]) -> str:
    return hashlib.sha256("".join(x + "\n" for x in sorted(routes)).encode("utf-8")).hexdigest()


if len(BASELINE_ROUTES) != 52:
    raise RuntimeError("BASELINE_ROUTES_NOT_52")
