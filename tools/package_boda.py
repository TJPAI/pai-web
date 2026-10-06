#!/usr/bin/env python3
"""Build and validate the production Boda ZIP without changing source Preview state."""
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


def run_python(build: Path, script: str, *args: str) -> None:
    subprocess.run(
        [sys.executable, str(build / 'tools' / script), *args],
        cwd=build,
        check=True,
    )


def run_node_check(build: Path, *paths: str) -> None:
    for rel in paths:
        subprocess.run(['node', '--check', rel], cwd=build, check=True)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
output.parent.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory(prefix='pai-boda-') as temporary:
    build = Path(temporary) / 'source'
    shutil.copytree(
        ROOT,
        build,
        ignore=shutil.ignore_patterns('.git', '_site', '__pycache__', '*.zip'),
    )

    # Production selection is local to this temporary build tree. The repository and
    # GitHub Pages Preview remain on the committed preview profile.
    config_path = build / 'config/site.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    config['active_environment'] = 'production'
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    # Keep the production package on the same validated source/build contracts as the
    # normal Pages pipeline. This script is the production-server build source of truth.
    subprocess.run(
        [sys.executable, '-m', 'compileall', '-q', str(build / 'tools')],
        cwd=build,
        check=True,
    )
    run_python(build, 'validate_repository_hygiene.py')
    run_python(build, 'validate_environment_matrix.py')
    run_python(build, 'check_production_readiness.py')
    run_python(build, 'sync_shared_head.py', '--check')
    run_python(build, 'render_publications.py')
    run_python(build, 'validate.py')
    run_python(build, 'validate_accessibility.py')
    run_python(build, 'validate_secure_links.py')
    run_python(build, 'validate_manifest.py')
    run_python(build, 'prepare_site_urls.py')
    run_python(build, 'validate_seo_contracts.py')
    run_python(build, 'validate_home_assets.py')
    run_python(build, 'validate_cta_links.py')
    run_python(build, 'validate_outputs_label.py')
    run_python(build, 'prepare_share_logo.py')
    run_python(build, 'validate_share_metadata.py')
    run_node_check(
        build,
        'assets/js/site.js',
        'assets/js/anchor-navigation.js',
        'sw.js',
    )
    run_python(build, 'sync_navigation_scripts.py', '--check')
    run_python(build, 'normalize_asset_versions.py', '--check')
    run_python(build, 'prepare_runtime.py')
    run_node_check(build, 'assets/js/site.js')
    run_python(build, 'prepare_css_bundle.py')

    # Boda is updated incrementally during normal maintenance. Keep the source-level
    # asset query tokens stable instead of rewriting every HTML page when one CSS/JS
    # file changes. The server's normal Last-Modified/ETag revalidation handles the
    # replaced asset; a full release remains available when a cache reset is needed.
    run_python(build, 'prepare_public_artifact.py')

    site = build / '_site'

    # CNAME is only meaningful for a GitHub Pages custom-domain deployment. The
    # institutional/Boda server package must not contain it.
    (site / 'CNAME').unlink(missing_ok=True)
    run_python(build, 'validate_public_artifact.py')

    # Production server artifact boundary.
    required = (
        'index.html',
        'en/index.html',
        'robots.txt',
        'sitemap.xml',
        'site.json',
    )
    for rel in required:
        if not (site / rel).is_file():
            raise SystemExit(f'Production artifact missing required file: {rel}')
    if (site / 'CNAME').exists():
        raise SystemExit('Production server artifact must not contain CNAME')
    if (site / 'geosketch-mvp').exists():
        raise SystemExit('Production server artifact must not publish geosketch-mvp')
    if list(site.rglob('*.webmanifest')):
        raise SystemExit('Production artifact contains legacy webmanifest')

    robots = (site / 'robots.txt').read_text(encoding='utf-8')
    if 'Disallow: /' in robots:
        raise SystemExit('Production robots.txt still blocks indexing')
    if 'Sitemap: https://ai.tongji.edu.cn/sitemap.xml' not in robots:
        raise SystemExit('Production robots.txt does not reference the production sitemap')

    sitemap = (site / 'sitemap.xml').read_text(encoding='utf-8')
    if 'https://ai.tongji.edu.cn/' not in sitemap:
        raise SystemExit('Production sitemap does not contain the production domain')

    files = sorted(path for path in site.rglob('*') if path.is_file())
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
        bad = archive.testzip()
        if bad is not None:
            raise SystemExit(f'ZIP integrity failed at {bad}')

    print(f'Boda ZIP ready: {output} ({len(files)} files)')
