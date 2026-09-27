#!/usr/bin/env python3
"""Validate source cache-key consistency or stamp deploy artifacts with content hashes.

Source HTML may keep readable/manual version tokens during development. In --check
mode we only require each shared asset to use one consistent token across pages.
During deployment, after runtime/CSS preparation, the script hashes the actual
referenced local CSS/JS files and rewrites ?v= to a deterministic SHA-256 prefix.
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECK_ONLY = "--check" in sys.argv[1:]

HTML_EXCLUDE_PARTS = {"geosketch-mvp", "templates"}
REF_RE = re.compile(
    r'(?P<quote>["\'])(?P<path>(?:(?:\.\./)*)assets/(?P<kind>css|js)/[^"\'?]+\.(?:css|js))'
    r'(?:\?v=(?P<version>[^"\']+))?(?P=quote)'
)


def html_files():
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if any(part in HTML_EXCLUDE_PARTS for part in rel.parts):
            continue
        yield path


def resolve_asset(html_path: Path, ref: str) -> Path:
    path_only = ref.split("?", 1)[0]
    asset = (html_path.parent / path_only).resolve()
    try:
        asset.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit(f"{html_path.relative_to(ROOT)}: asset escapes repository: {ref}") from exc
    return asset


if CHECK_ONLY:
    versions: dict[str, set[str]] = {}
    errors = []
    for html in html_files():
        text = html.read_text(encoding="utf-8")
        for match in REF_RE.finditer(text):
            ref = match.group("path")
            version = match.group("version")
            asset = resolve_asset(html, ref)
            if not asset.is_file():
                errors.append(f"{html.relative_to(ROOT)}: missing referenced asset {ref}")
                continue
            key = asset.relative_to(ROOT).as_posix()
            if version is None:
                errors.append(f"{html.relative_to(ROOT)}: {ref} is missing ?v= cache key")
                continue
            versions.setdefault(key, set()).add(version)

    for asset, tokens in sorted(versions.items()):
        if len(tokens) != 1:
            errors.append(f"{asset}: inconsistent cache keys across HTML: {sorted(tokens)}")

    if errors:
        print("Shared asset cache-key validation failed:")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)
    print(f"Shared asset cache-key validation passed for {len(versions)} referenced CSS/JS asset(s).")
    raise SystemExit(0)

hashes: dict[Path, str] = {}
changed = 0
referenced = set()

for html in html_files():
    text = html.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        ref = match.group("path")
        asset = resolve_asset(html, ref)
        if not asset.is_file():
            raise SystemExit(f"{html.relative_to(ROOT)}: missing referenced asset {ref}")
        if asset not in hashes:
            hashes[asset] = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        referenced.add(asset)
        return f'{match.group("quote")}{ref}?v={hashes[asset]}{match.group("quote")}'

    updated = REF_RE.sub(replace, text)
    if updated != text:
        html.write_text(updated, encoding="utf-8")
        changed += 1

print(f"Stamped {len(referenced)} deployed CSS/JS asset(s) with content hashes across {changed} HTML file(s).")
