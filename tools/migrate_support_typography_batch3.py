#!/usr/bin/env python3
from pathlib import Path

files={
    Path('assets/css/refine-base.css'):{
        '.impact-capabilities{margin-top:14px;color:var(--ink);font-size:14px;font-weight:600;letter-spacing:.005em}':
        '.impact-capabilities{margin-top:14px;color:var(--ink);font-size:var(--text-support-size);font-weight:600;letter-spacing:.005em}',
        '.research-detail .muted{font-size:14px;line-height:1.8;margin-top:26px}':
        '.research-detail .muted{font-size:var(--text-support-size);line-height:1.8;margin-top:26px}',
        '.publication-note strong{color:var(--ink);font-size:14px}':
        '.publication-note strong{color:var(--ink);font-size:var(--text-support-size)}',
        '.pub-authors{color:#3f4652!important;font-size:14px!important;line-height:1.6}':
        '.pub-authors{color:#3f4652!important;font-size:var(--text-support-size)!important;line-height:1.6}',
    },
    Path('assets/css/site.css'):{
        '.metric span{display:block;color:var(--muted);margin-top:12px;font-size:14px}':
        '.metric span{display:block;color:var(--muted);margin-top:12px;font-size:var(--text-support-size)}',
        '.fact{margin-top:18px;padding-top:16px;border-top:1px solid var(--line);font-size:14px;color:#394150}':
        '.fact{margin-top:18px;padding-top:16px;border-top:1px solid var(--line);font-size:var(--text-support-size);color:#394150}',
        '.person .role{font-size:14px;color:var(--muted)}':
        '.person .role{font-size:var(--text-support-size);color:var(--muted)}',
        '.pub p{margin:0;color:var(--muted);font-size:14px}':
        '.pub p{margin:0;color:var(--muted);font-size:var(--text-support-size)}',
    },
}

for path,replacements in files.items():
    text=path.read_text(encoding='utf-8')
    for old,new in replacements.items():
        if old not in text:
            raise SystemExit(f'missing expected CSS fragment in {path}: {old}')
        text=text.replace(old,new,1)
    path.write_text(text,encoding='utf-8')
