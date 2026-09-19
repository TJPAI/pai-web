#!/usr/bin/env python3
from pathlib import Path

p=Path('assets/css/refine-base.css')
text=p.read_text(encoding='utf-8')
replacements={
    '.page-hero p{max-width:760px;font-size:18px;line-height:1.75;margin:0;color:var(--muted)}':
    '.page-hero p{max-width:760px;font-size:var(--text-lead-size);line-height:var(--text-lead-line);margin:0;color:var(--muted)}',
    '.content-section p{font-size:16px;line-height:1.85}':
    '.content-section p{font-size:var(--text-body-size);line-height:1.85}',
    '.join-item p{margin:0;color:var(--muted);font-size:14px;line-height:1.7}':
    '.join-item p{margin:0;color:var(--muted);font-size:var(--text-support-size);line-height:1.7}',
    '.page-hero p{font-size:17px;line-height:1.62}':
    '.page-hero p{font-size:var(--text-lead-size);line-height:1.62}',
    '.content-section p,.prose p{font-size:16px;line-height:1.7}':
    '.content-section p,.prose p{font-size:var(--text-body-size);line-height:var(--text-body-line)}',
    '.join-item p{font-size:14px;line-height:1.6}':
    '.join-item p{font-size:var(--text-support-size);line-height:var(--text-support-line)}',
}
for old,new in replacements.items():
    if old not in text:
        raise SystemExit(f'missing expected CSS fragment: {old}')
    text=text.replace(old,new,1)
p.write_text(text,encoding='utf-8')
