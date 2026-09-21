#!/usr/bin/env python3
"""Keep the iOS WeChat first-paint guard identical across all deployable HTML pages.

Usage:
  python tools/sync_shared_head.py --check   # CI: fail if any page drifts or omits the guard
  python tools/sync_shared_head.py --write   # normalize all pages from the shared template
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "shared" / "wechat-first-paint.inc"
EXCLUDED_DIRS = {".git", "node_modules", "templates", "tmp"}

# Matches either the old simple viewport tag or the current WeChat first-paint block.
BLOCK_RE = re.compile(
    r'<meta name="viewport" content="width=device-width,initial-scale=1(?:,viewport-fit=cover)?">'
    r'(?:<style>html\{-webkit-text-size-adjust:100%;text-size-adjust:100%\}'
    r'html\.wechat-ios,html\.wechat-ios body\{-webkit-text-size-adjust:100%!important;'
    r'text-size-adjust:100%!important\}</style>'
    r'<script>\(function\(\)\{var u=navigator\.userAgent;'
    r'if\(/MicroMessenger/i\.test\(u\)&&/\(iPhone\|iPad\|iPod\)/i\.test\(u\)\)'
    r'document\.documentElement\.classList\.add\("wechat-ios"\)\}\)\(\);</script>)?'
)


def html_pages() -> list[Path]:
    pages: list[Path] = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        pages.append(path)
    return sorted(pages)


def template_text() -> str:
    return TEMPLATE.read_text(encoding="utf-8").strip()


def check() -> int:
    expected = template_text()
    bad: list[str] = []
    for path in html_pages():
        text = path.read_text(encoding="utf-8")
        if expected not in text:
            bad.append(str(path.relative_to(ROOT)))
    if bad:
        print("Shared WeChat first-paint block is missing or out of sync:")
        for name in bad:
            print(f"  - {name}")
        print("Run: python tools/sync_shared_head.py --write")
        return 1
    print(f"Shared head template OK on {len(html_pages())} HTML pages.")
    return 0


def write() -> int:
    expected = template_text()
    changed = 0
    failures: list[str] = []
    for path in html_pages():
        text = path.read_text(encoding="utf-8")
        if expected in text:
            continue
        new_text, count = BLOCK_RE.subn(expected, text, count=1)
        if count != 1:
            failures.append(str(path.relative_to(ROOT)))
            continue
        path.write_text(new_text, encoding="utf-8")
        changed += 1
    if failures:
        print("Could not locate a supported viewport block in:")
        for name in failures:
            print(f"  - {name}")
        return 1
    print(f"Updated {changed} HTML page(s) from {TEMPLATE.relative_to(ROOT)}.")
    return check()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    return check() if args.check else write()


if __name__ == "__main__":
    raise SystemExit(main())
