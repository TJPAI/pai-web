#!/usr/bin/env python3
"""Build a production Boda ZIP without changing source or preview configuration."""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
output.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='pai-boda-') as temporary:
    build = Path(temporary) / 'source'
    shutil.copytree(ROOT, build, ignore=shutil.ignore_patterns('.git', '_site', '__pycache__', '*.zip'))
    config_path = build / 'config/site.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    config['active_environment'] = 'production'
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    for script in ('render_publications.py', 'prepare_site_urls.py', 'prepare_css_bundle.py',
                   'normalize_asset_versions.py', 'prepare_public_artifact.py'):
        subprocess.run([sys.executable, str(build / 'tools' / script)], cwd=build, check=True)
    site = build / '_site'
    (site / 'CNAME').unlink(missing_ok=True)
    assert (site / 'site.json').is_file(), 'site.json missing'
    assert not list(site.rglob('*.webmanifest')), 'legacy manifest present'
    assert 'Disallow: /' not in (site / 'robots.txt').read_text(encoding='utf-8')
    files = sorted(p for p in site.rglob('*') if p.is_file())
    for path in files:
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        if re.search(r'tjpai\.github\.io|site\.webmanifest', text, re.I):
            raise SystemExit(f'Legacy public reference in {path.relative_to(site)}')
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(site))
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None, 'ZIP integrity failed'
    print(f'Boda ZIP ready: {output} ({len(files)} files)')
