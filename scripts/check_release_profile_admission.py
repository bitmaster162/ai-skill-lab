#!/usr/bin/env python3
"""Bounded, read-only historical-byte loading for a trusted sandbox.

All paths must be relative literal POSIX paths. No network, subprocess, writes,
symlink following, or special-file reads. This is a prototype; POSIX-only.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path


class Hold(RuntimeError):
    """Cannot establish a positive result due to missing/incomplete evidence."""


class Deny(ValueError):
    """Bad path, unsafe object or identity/content mismatch."""


def components(relative: str) -> tuple[str, ...]:
    if type(relative) is not str or len(relative) > 512 or not relative:
        raise Deny("UNSAFE_PATH")
    if relative.startswith("/") or "\\" in relative or ":" in relative or "\x00" in relative:
        raise Deny("UNSAFE_PATH")
    parts = tuple(relative.split("/"))
    if any(p in ("", ".", "..") or any(ord(c) < 32 or ord(c) == 127 for c in p) for p in parts):
        raise Deny("UNSAFE_PATH")
    return parts


def _directory_flags() -> int:
    """Require POSIX no-follow and directory-handle primitives; never degrade."""
    required = ("O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC")
    if not all(type(getattr(os, field, None)) is int for field in required):
        raise Hold("POSIX_DIRFD_NOFOLLOW_UNAVAILABLE")
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC


def _open_root_fd(root: Path) -> int:
    """Open every ancestor from / by dirfd, without a pathname TOCTOU gap."""
    if not isinstance(root, Path):
        raise Deny("ROOT_PATH_TYPE")
    absolute = root.absolute()
    if not absolute.is_absolute():
        raise Deny("ROOT_NOT_ABSOLUTE")
    parts = absolute.parts
    if not parts or parts[0] != "/" or any(p in ("", ".", "..") for p in parts[1:]):
        raise Deny("ROOT_PATH_TRAVERSAL")
    flags = _directory_flags()
    fd = None
    completed = False
    try:
        fd = os.open("/", flags)
        for segment in parts[1:]:
            next_fd = os.open(segment, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        completed = True
        return fd
    except FileNotFoundError as exc:
        raise Hold("HISTORICAL_CORPUS_NOT_MATERIALIZED") from exc
    except OSError as exc:
        raise Deny("UNSAFE_ROOT_OR_SYMLINK_ANCESTOR") from exc
    finally:
        # Ownership of the open FD passes to caller only on successful return.
        if not completed and fd is not None:
            os.close(fd)


def _descend(fd: int, segment: str) -> int:
    flags = _directory_flags()
    return os.open(segment, flags, dir_fd=fd)


def _check_root(root: Path) -> None:
    fd = _open_root_fd(root)
    os.close(fd)


def read_file(root: Path, relative: str, max_bytes: int) -> bytes:
    parts = components(relative)
    if type(max_bytes) is not int or max_bytes < 0 or max_bytes > 4_000_000:
        raise Deny("FILE_BUDGET_INVALID")
    fd = None
    try:
        fd = _open_root_fd(root)
        for segment in parts[:-1]:
            new_fd = _descend(fd, segment)
            os.close(fd)
            fd = new_fd
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
        leaf = os.open(parts[-1], flags, dir_fd=fd)
        try:
            before = os.fstat(leaf)
            if not stat.S_ISREG(before.st_mode):
                raise Deny("SPECIAL_FILE_DENIED")
            if before.st_nlink != 1:
                raise Deny("HARDLINK_DENIED")
            if before.st_size > max_bytes:
                raise Deny("FILE_OVER_BUDGET")
            chunks = []
            read_total = 0
            while True:
                data = os.read(leaf, min(65536, max_bytes + 1 - read_total))
                if not data:
                    break
                chunks.append(data)
                read_total += len(data)
                if read_total > max_bytes:
                    raise Deny("FILE_OVER_BUDGET")
            after = os.fstat(leaf)
            stamp = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size,
                               s.st_mtime_ns, s.st_ctime_ns)
            if stamp(before) != stamp(after) or read_total != before.st_size:
                raise Deny("CONCURRENT_FILE_MUTATION")
            return b"".join(chunks)
        finally:
            os.close(leaf)
    except FileNotFoundError as exc:
        raise Hold("HISTORICAL_CORPUS_FILE_MISSING") from exc
    except (NotADirectoryError, IsADirectoryError, PermissionError, OSError) as exc:
        raise Deny("UNSAFE_OR_UNREADABLE_FILE") from exc
    finally:
        if fd is not None:
            os.close(fd)


def inventory(root: Path, subdirectory: str, *, max_entries: int = 300) -> set[str]:
    """Bounded recursive walk using pinned dirfds; never rescan by pathname."""
    parts = components(subdirectory)
    if type(max_entries) is not int or max_entries <= 0 or max_entries > 10_000:
        raise Deny("INVENTORY_BUDGET_INVALID")
    counter = [0]
    result: set[str] = set()
    fd = None

    def visit(dirfd: int, prefix: str, depth: int) -> None:
        if depth > 16:
            raise Deny("INVENTORY_MAX_DEPTH")
        before = os.fstat(dirfd)
        with os.scandir(dirfd) as scan:
            names = [item.name for item in scan]
        if len(names) != len(set(names)):
            raise Deny("DUPLICATE_DIRECTORY_ENTRY")
        for name in sorted(names):
            components(name)
            counter[0] += 1
            if counter[0] > max_entries:
                raise Deny("INVENTORY_MAX_ENTRIES")
            info = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise Deny("SYMLINK_IN_ASSET_INVENTORY")
            rel = prefix + name
            if stat.S_ISDIR(info.st_mode):
                child = _descend(dirfd, name)
                try:
                    pinned = os.fstat(child)
                    if (info.st_dev, info.st_ino, info.st_mode) != (
                            pinned.st_dev, pinned.st_ino, pinned.st_mode):
                        raise Deny("RACING_DIRECTORY_ENTRY")
                    visit(child, rel + "/", depth + 1)
                finally:
                    os.close(child)
            elif stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1:
                    raise Deny("HARDLINK_IN_ASSET_INVENTORY")
                second = os.stat(name, dir_fd=dirfd, follow_symlinks=False)
                if (info.st_dev, info.st_ino, info.st_mode, info.st_size,
                    info.st_mtime_ns, info.st_ctime_ns) != (
                    second.st_dev, second.st_ino, second.st_mode, second.st_size,
                    second.st_mtime_ns, second.st_ctime_ns):
                    raise Deny("RACING_FILE_ENTRY")
                result.add(rel)
            else:
                raise Deny("SPECIAL_FILE_IN_ASSET_INVENTORY")
        with os.scandir(dirfd) as scan:
            final_names = [item.name for item in scan]
        after = os.fstat(dirfd)
        fields = lambda s: (s.st_dev, s.st_ino, s.st_mode,
                            s.st_mtime_ns, s.st_ctime_ns)
        if sorted(names) != sorted(final_names) or fields(before) != fields(after):
            raise Deny("CONCURRENT_DIRECTORY_MUTATION")

    try:
        fd = _open_root_fd(root)
        for segment in parts:
            new_fd = _descend(fd, segment)
            os.close(fd)
            fd = new_fd
        visit(fd, "", 0)
        return result
    except FileNotFoundError as exc:
        raise Hold("HISTORICAL_CORPUS_NOT_MATERIALIZED") from exc
    except Deny:
        raise
    except (NotADirectoryError, IsADirectoryError, PermissionError, OSError) as exc:
        raise Deny("UNSAFE_OR_UNREADABLE_INVENTORY") from exc
    finally:
        if fd is not None:
            os.close(fd)

# The previously defined safe_io functions are embedded to fit the exact six-file scope.
import hashlib
import json
import re
import sys
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from release_admission import AdmissionDenied, validate_full, verify_profile_identity, load_archived_profile
from release_admission.authority import APPROVED_HISTORICAL_PINS


def run(root: Path) -> dict:
    raw_manifest = read_file(root, "deploy/live/_release.json", 80_000)
    try:
        document = json.loads(raw_manifest.decode("utf-8"))
        release_id = document.get("release_id")
    except (UnicodeError, ValueError, TypeError, AttributeError) as error:
        raise Deny("INVALID_RELEASE_MANIFEST") from error
    if type(release_id) is not str or release_id not in APPROVED_HISTORICAL_PINS:
        raise Deny("UNKNOWN_RELEASE_DENIED")
    profile_bytes = load_archived_profile(release_id)
    identity = verify_profile_identity(release_id, profile_bytes)
    manifest_records = document.get("files")
    if type(manifest_records) is not list or len(manifest_records) != identity.file_count:
        raise Deny("MANIFEST_RECORD_COUNT_MISMATCH")
    names = []
    for row in manifest_records:
        if type(row) is not dict or type(row.get("path")) is not str:
            raise Deny("INVALID_MANIFEST_RECORD")
        components(row["path"])
        names.append(row["path"])
    if len(set(names)) != len(names) or "_release.json" in names:
        raise Deny("DUPLICATE_OR_SELF_REFERENTIAL_ASSET")
    exact_inventory = inventory(root, "deploy/live", max_entries=150)
    if exact_inventory != set(names) | {"_release.json"}:
        raise Deny("PHYSICAL_ASSET_INVENTORY_DRIFT")
    assets = {name: read_file(root, "deploy/live/" + name, 4_000_000) for name in names}
    # Source pins are part of canonical historical profile; never inspect arbitrary source paths.
    source_pins = json.loads(profile_bytes)["source_pins"]
    sources = {path: read_file(root, path, 4_000_000) for path in source_pins}
    paths = ["/" if n == "index.html" else "/en" if n == "en.html" else "/" + n[:-5]
             for n in names if n.endswith(".html") and n != "404.html"]
    # Read sitemap and llms from the exact pinned physical files. No user-supplied URLs.
    sitemap = assets.get("sitemap.xml", b"")
    if b"<!DOCTYPE" in sitemap.upper() or b"<!ENTITY" in sitemap.upper():
        raise Deny("UNSAFE_SITEMAP_XML")
    try:
        sitemap_urls = [x.text.strip() if x.text else "" for x in
                        ET.fromstring(sitemap).findall(".//{*}url/{*}loc")]
        llms_urls = re.findall(r"\]\((https?://[^)\s]+)\)", assets["llms.txt"].decode("utf-8"))
    except (ValueError, KeyError, UnicodeError, ET.ParseError) as error:
        raise Deny("INVALID_URL_INDICES") from error
    validated = validate_full(release_id, profile_bytes, raw_manifest,
                              assets, sources, paths, sitemap_urls, llms_urls)
    return {"schema":"ai-skill-lab.r4e.source-only.check.v1",
            "status":"HISTORICAL_BYTE_VALIDATION_PASS_NO_OWNER_AUTHORITY",
            "release_id":release_id, "assets_verified":validated.asset_count,
            "routes_verified":validated.route_count,
            "profile_sha256":validated.profile_sha256,
            "manifest_sha256":validated.manifest_sha256,
            "payload_sha256":validated.payload_sha256,
            "publication_authorized":False, "merge_authorized":False,
            "owner_trust_root_deployed":False}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        print("R4E_ADMISSION_DENY_UNEXPECTED_ARGUMENTS")
        return 2
    try:
        result = run(ROOT)
    except Hold as exc:
        print("R4E_ADMISSION_HOLD:", str(exc))
        return 3
    except (AdmissionDenied, Deny, ValueError, TypeError) as exc:
        print("R4E_ADMISSION_DENY:", str(exc))
        return 2
    except Exception as exc:
        print("R4E_ADMISSION_ERROR_FAIL_CLOSED:", type(exc).__name__, str(exc))
        return 2
    print(json.dumps(result, sort_keys=True))
    print("R4E_HISTORICAL_PROFILE_SOURCE_CHECK_PASS_NOT_AUTHORIZATION")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
