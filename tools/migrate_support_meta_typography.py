#!/usr/bin/env python3
from pathlib import Path

files = {
    Path('assets/css/refine-base.css'): {
        '.home-hero .hero-note{max-width:520px;color:var(--muted);font-size:14px;margin:0 0 28px}':
        '.home-hero .hero-note{max-width:520px;color:var(--muted);font-size:var(--text-support-size);margin:0 0 28px}',
        '.pub-venue{font-size:13px!important;line-height:1.55;margin-top:3px!important}':
        '.pub-venue{font-size:var(--text-meta-size)!important;line-height:1.55;margin-top:3px!important}',
        '.person .research-line{font-size:14px;color:#3d4551;min-height:46px}':
        '.person .research-line{font-size:var(--text-support-size);color:#3d4551;min-height:46px}',
        '.pub-venue{font-size:12px!important}':
        '.pub-venue{font-size:var(--text-meta-size)!important}',
        '.team-grid .person .research-line{font-size:14px;line-height:1.6}':
        '.team-grid .person .research-line{font-size:var(--text-support-size);line-height:var(--text-support-line)}',
        '.news-row time,.news-row .label{font-size:12px;line-height:1.4}':
        '.news-row time,.news-row .label{font-size:var(--text-meta-size);line-height:1.4}',
        '.pub-actions{font-size:12px}':
        '.pub-actions{font-size:var(--text-meta-size)}',
    },
    Path('assets/css/site.css'): {
        '.news-row time,.news-row .label{font-size:13px;color:var(--muted)}':
        '.news-row time,.news-row .label{font-size:var(--text-meta-size);color:var(--muted)}',
        '.pub-actions{margin-top:10px;display:flex;gap:16px;font-size:13px;font-weight:600}':
        '.pub-actions{margin-top:10px;display:flex;gap:16px;font-size:var(--text-meta-size);font-weight:600}',
    },
}

for path, replacements in files.items():
    text = path.read_text(encoding='utf-8')
    for old, new in replacements.items():
        if old not in text:
            raise SystemExit(f'missing expected CSS fragment in {path}: {old}')
        text = text.replace(old, new, 1)
    path.write_text(text, encoding='utf-8')
