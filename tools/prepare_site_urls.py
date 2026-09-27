#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

from site_config import ROOT, BASE_URL, CUSTOM_DOMAIN, ALLOW_INDEXING, ENVIRONMENT

KNOWN_BASES = {
    "https://tjpai.github.io/pai-web/",
    "https://ai.tongji.edu.cn/",
}


def rewrite_text(text: str) -> str:
    for base in KNOWN_BASES:
        if base != BASE_URL:
            text = text.replace(base, BASE_URL)
    return text


changed = 0
for path in ROOT.rglob("*.html"):
    rel = path.relative_to(ROOT)
    if any(part in {".git", "node_modules", "templates", "tmp"} for part in rel.parts):
        continue
    text = path.read_text(encoding="utf-8")
    updated = rewrite_text(text)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1

sitemap = ROOT / "sitemap.xml"
if sitemap.exists():
    text = sitemap.read_text(encoding="utf-8")
    updated = rewrite_text(text)
    if updated != text:
        sitemap.write_text(updated, encoding="utf-8")
        changed += 1

robots = ROOT / "robots.txt"
if ALLOW_INDEXING:
    robots_text = f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n"
else:
    robots_text = (
        "User-agent: *\n"
        "Disallow: /\n\n"
        f"# {ENVIRONMENT.capitalize()} environment only. Indexing is disabled by config/site.json.\n"
    )
if not robots.exists() or robots.read_text(encoding="utf-8") != robots_text:
    robots.write_text(robots_text, encoding="utf-8")
    changed += 1

cname = ROOT / "CNAME"
if CUSTOM_DOMAIN:
    cname_text = CUSTOM_DOMAIN + "\n"
    if not cname.exists() or cname.read_text(encoding="utf-8") != cname_text:
        cname.write_text(cname_text, encoding="utf-8")
        changed += 1
elif cname.exists():
    cname.unlink()
    changed += 1

print(
    f"Prepared site URLs for {ENVIRONMENT}: base={BASE_URL} "
    f"indexing={'on' if ALLOW_INDEXING else 'off'} custom_domain={CUSTOM_DOMAIN or '-'}; "
    f"changed={changed}"
)
