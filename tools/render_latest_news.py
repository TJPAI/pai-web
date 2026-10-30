#!/usr/bin/env python3
"""Render bilingual Latest News from data/latest-news.json without a second HTML owner."""
from pathlib import Path
from html import escape
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data/latest-news.json").read_text(encoding="utf-8"))
items = data["items"]
visible = data["default_visible"]
assert visible == 5 and len(items) == 45
assert len({(x["date"], x["zh"]["text"]) for x in items}) == len(items)
assert all(re.fullmatch(r"\\d{4}-\\d{2}", x["date"]) for x in items)
assert [x["date"] for x in items] == sorted((x["date"] for x in items), reverse=True)

def item_html(entry, lang):
    record = entry[lang]
    date = escape(entry["date"], quote=True)
    label = entry["date"].replace("-", ".")
    title = record["text"]  # Existing editorial HTML entities are retained as-is.
    assert "<" not in title and ">" not in title
    url = record.get("url")
    if url:
        assert url.startswith(("https://", "http://"))
        return (f'<a class="results-news-row" href="{escape(url, quote=True)}" '
                f'target="_blank" rel="noopener noreferrer"><time datetime="{date}">{label}</time>'
                f'<span>{title}</span></a>')
    return (f'<div class="results-news-row results-news-row-static"><time datetime="{date}">'
            f'{label}</time><span>{title}</span></div>')

for lang, page in (("zh", "publications.html"), ("en", "en/publications.html")):
    path = ROOT / page
    source = path.read_text(encoding="utf-8")
    replacement = ('<div class="results-news-list">'
                   + "".join(item_html(x, lang) for x in items[:visible])
                   + '</div><div class="results-news-list results-news-extra" id="results-news-extra" hidden>'
                   + "".join(item_html(x, lang) for x in items[visible:])
                   + '</div>')
    pattern = r'<div class="results-news-list">.*?</div><div class="results-news-list results-news-extra" id="results-news-extra" hidden>.*?</div>(?=</aside>)'
    rendered, count = re.subn(pattern, lambda _: replacement, source, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"{page}: cannot find Latest News lists")
    if "--check" in sys.argv:
        if rendered != source:
            raise SystemExit(f"{page}: news out of sync; run tools/render_latest_news.py")
    else:
        path.write_text(rendered, encoding="utf-8")
    print(f"{page}: {len(items)} bilingual news entries verified")
