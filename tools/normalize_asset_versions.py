#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REFINE_VERSION = "20260925-04"
SITE_JS_VERSION = "20260925-03"

refine_pattern = re.compile(r"refine\.css\?v=[0-9-]+")
site_js_pattern = re.compile(r"site\.js\?v=[0-9-]+")
changed = 0

for path in ROOT.rglob("*.html"):
    if "geosketch-mvp" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    updated = refine_pattern.sub(f"refine.css?v={REFINE_VERSION}", text)
    updated = site_js_pattern.sub(f"site.js?v={SITE_JS_VERSION}", updated)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        changed += 1

print(f"Normalized refine.css and site.js cache keys in {changed} HTML file(s).")
