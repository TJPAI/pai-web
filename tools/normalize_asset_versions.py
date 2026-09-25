#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
REFINE_VERSION = "20260925-05"
SITE_JS_VERSION = "20260925-03"

refine_pattern = re.compile(r"refine\.css\?v=[0-9-]+")
site_js_pattern = re.compile(r"site\.js\?v=[0-9-]+")
expected_refine = f"refine.css?v={REFINE_VERSION}"
expected_site_js = f"site.js?v={SITE_JS_VERSION}"
check_only = "--check" in sys.argv[1:]
changed = 0
errors = []

for path in ROOT.rglob("*.html"):
    if "geosketch-mvp" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    if check_only:
        for match in refine_pattern.findall(text):
            if match != expected_refine:
                errors.append(f"{path.relative_to(ROOT)}: stale cache key {match}; expected {expected_refine}")
        for match in site_js_pattern.findall(text):
            if match != expected_site_js:
                errors.append(f"{path.relative_to(ROOT)}: stale cache key {match}; expected {expected_site_js}")
        continue

    updated = refine_pattern.sub(expected_refine, text)
    updated = site_js_pattern.sub(expected_site_js, updated)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1

if check_only:
    if errors:
        print("Shared asset cache-key validation failed:")
        for error in errors:
            print(f" - {error}")
        sys.exit(1)
    print("Shared asset cache-key validation passed.")
else:
    print(f"Normalized refine.css and site.js cache keys in {changed} HTML file(s).")
