"""Strict JSON I/O, exact UTF-8 canonical serialization (NOT RFC 8785/JCS).

This local protocol deliberately fixes a smaller domain-specific canonicalization:
- no floats, NaN, duplicate keys, surrogate codepoints or unrecognized types;
- Unicode is not normalized; the attestation schema accepts only ASCII strings;
- sorted object keys, minified separators, JSON UTF-8 with ensure_ascii=False.
The signature input is DOMAIN || canonical_payload_bytes.
Do NOT label this encoding JCS. Its use requires separate policy approval.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

DOMAIN = b"AI_SKILL_LAB_OWNER_ADMISSION_V1\x00"
MAX_ENVELOPE_BYTES = 16_384
UTC_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


class InvalidDocument(ValueError):
    pass


def strict_json_bytes(data: bytes) -> dict:
    if type(data) is not bytes or not 1 <= len(data) <= MAX_ENVELOPE_BYTES:
        raise InvalidDocument("JSON_INPUT_TYPE_OR_SIZE")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict:
        obj: dict = {}
        for key, value in pairs:
            if key in obj:
                raise InvalidDocument("JSON_DUPLICATE_KEY")
            obj[key] = value
        return obj

    def no_float(_s: str):
        raise InvalidDocument("JSON_FLOAT_FORBIDDEN")

    def no_constant(_s: str):
        raise InvalidDocument("JSON_CONSTANT_FORBIDDEN")

    try:
        decoded = data.decode("utf-8", errors="strict")
        obj = json.loads(decoded, object_pairs_hook=pairs_hook,
                         parse_float=no_float, parse_constant=no_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise InvalidDocument("JSON_INVALID_UTF8_OR_SYNTAX") from exc
    if type(obj) is not dict:
        raise InvalidDocument("JSON_ROOT_NOT_OBJECT")
    return obj


def _validate_serializable(obj: Any, *, depth: int = 0) -> None:
    if depth > 12:
        raise InvalidDocument("CANONICAL_NESTING_LIMIT")
    if obj is None or type(obj) in (bool, str, int):
        if type(obj) is str:
            try:
                obj.encode("utf-8", errors="strict")
            except UnicodeError as exc:
                raise InvalidDocument("CANONICAL_INVALID_UNICODE") from exc
        return
    if type(obj) is list:
        for value in obj:
            _validate_serializable(value, depth=depth + 1)
        return
    if type(obj) is dict:
        for key, value in obj.items():
            if type(key) is not str:
                raise InvalidDocument("CANONICAL_KEY_NOT_STRING")
            _validate_serializable(key, depth=depth + 1)
            _validate_serializable(value, depth=depth + 1)
        return
    raise InvalidDocument("CANONICAL_UNSUPPORTED_TYPE")


def canonical_bytes(value: Any) -> bytes:
    _validate_serializable(value)
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (UnicodeError, ValueError, TypeError) as exc:
        raise InvalidDocument("CANONICAL_SERIALIZATION_ERROR") from exc


def sha256_bytes(data: bytes) -> str:
    if type(data) is not bytes:
        raise InvalidDocument("HASH_INPUT_NOT_BYTES")
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def utc_timestamp(text: str) -> datetime:
    if type(text) is not str or not UTC_PATTERN.fullmatch(text):
        raise InvalidDocument("UTC_FORMAT_INVALID")
    try:
        out = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise InvalidDocument("UTC_DATETIME_INVALID") from exc
    if out.strftime("%Y-%m-%dT%H:%M:%SZ") != text:
        raise InvalidDocument("UTC_CANONICAL_MISMATCH")
    return out
