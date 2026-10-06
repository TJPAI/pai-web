#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

# Retired one-off and homepage-logo assets.
for rel in (
    '.github/workflows/fix-home-research-index-weight-once.yml',
    'assets/js/home-logo.js',
    'assets/css/home-logo.css',
):
    (ROOT / rel).unlink(missing_ok=True)

# Shared navigation now only owns anchor-navigation.js.
sync = ROOT / 'tools/sync_navigation_scripts.py'
sync.write_text('''#!/usr/bin/env python3
"""Keep shared navigation assets identical for direct entry and in-site navigation."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ('assets/js/anchor-navigation.js?v=20260925-03',)
check_only = '--check' in sys.argv
errors = []
changed = 0
for path in ROOT.rglob('*.html'):
    relative = path.relative_to(ROOT)
    if 'geosketch-mvp' in path.parts or relative.as_posix() == '404.html':
        continue
    text = path.read_text(encoding='utf-8')
    if '</body>' not in text:
        continue
    prefix = '../' * len(relative.parent.parts)
    scripts = [f'<script src="{prefix}{script}"></script>' for script in SCRIPTS]
    script_pattern = r'<script\\b[^>]*src=["\\\'][^"\\\']*(?:menu-exclusive|anchor-navigation|home-logo)\\.js[^"\\\']*["\\\'][^>]*></script>'
    style_pattern = r'<link\\b[^>]*href=["\\\'][^"\\\']*home-logo\\.css[^"\\\']*["\\\'][^>]*>'
    if re.findall(script_pattern, text) == scripts and not re.findall(style_pattern, text):
        continue
    if check_only:
        errors.append(str(relative))
        continue
    text = re.sub(script_pattern, '', text)
    text = re.sub(style_pattern, '', text)
    text = text.replace('</body>', ''.join(scripts) + '</body>', 1)
    path.write_text(text, encoding='utf-8')
    changed += 1
if errors:
    sys.exit('Navigation assets out of sync: ' + ', '.join(errors))
print('Navigation assets passed.' if check_only else f'Updated {changed} page(s).')
''', encoding='utf-8')
subprocess.run([sys.executable, str(sync)], cwd=ROOT, check=True)

# Remove the empty former logo slot from both homepages.
for rel in ('index.html', 'en/index.html'):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    old = '<div class="hero-art" aria-hidden="true"></div>'
    if old not in text:
        raise SystemExit(f'Expected hero-art not found in {rel}')
    path.write_text(text.replace(old, '', 1), encoding='utf-8')

# Platform Introduction is terminal: preserve internal rules, remove final rule.
for rel in ('about.html', 'en/about.html'):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    old = '<section class="section soft divider-short-list anchor-target" id="international-impact">'
    new = '<section class="section soft divider-short-list no-final-divider anchor-target" id="international-impact">'
    if old not in text:
        raise SystemExit(f'Platform section marker not found in {rel}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')

# Build pipeline no longer validates or packages home-logo.js.
pages = ROOT / '.github/workflows/pages.yml'
text = pages.read_text(encoding='utf-8')
text = text.replace(
    'node --check assets/js/site.js && node --check assets/js/home-logo.js && node --check sw.js && node --check assets/js/anchor-navigation.js',
    'node --check assets/js/site.js && node --check sw.js && node --check assets/js/anchor-navigation.js',
)
marker = '      - name: Validate environment matrix\n'
hygiene_step = '      - name: Validate repository hygiene\n        run: python tools/validate_repository_hygiene.py\n'
if hygiene_step not in text:
    if marker not in text:
        raise SystemExit('pages.yml insertion marker missing')
    text = text.replace(marker, hygiene_step + marker, 1)
pages.write_text(text, encoding='utf-8')

package = ROOT / 'tools/package_boda.py'
text = package.read_text(encoding='utf-8')
text = text.replace("        'assets/js/home-logo.js',\n", '')
marker = "    run_python(build, 'validate_environment_matrix.py')\n"
hygiene_call = "    run_python(build, 'validate_repository_hygiene.py')\n"
if hygiene_call not in text:
    if marker not in text:
        raise SystemExit('package_boda insertion marker missing')
    text = text.replace(marker, hygiene_call + marker, 1)
package.write_text(text, encoding='utf-8')

# Repository hygiene guard catches the exact class of accidental probe/one-off leftovers.
(ROOT / 'tools/validate_repository_hygiene.py').write_text('''#!/usr/bin/env python3
"""Reject temporary or retired repository artifacts before deployment."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
problems = []
for path in ROOT.iterdir():
    if path.name.startswith('__'):
        problems.append(f'temporary root artifact: {path.name}')
workflow_dir = ROOT / '.github' / 'workflows'
if workflow_dir.exists():
    for path in workflow_dir.glob('*-once.yml'):
        problems.append(f'one-off workflow left in repository: {path.relative_to(ROOT)}')
for rel in ('assets/js/home-logo.js', 'assets/css/home-logo.css'):
    if (ROOT / rel).exists():
        problems.append(f'retired homepage-logo asset still present: {rel}')
for html in ROOT.rglob('*.html'):
    if '_site' in html.parts:
        continue
    text = html.read_text(encoding='utf-8', errors='ignore')
    if 'home-logo.js' in text or 'home-logo.css' in text:
        problems.append(f'retired homepage-logo reference: {html.relative_to(ROOT)}')
if problems:
    raise SystemExit('Repository hygiene failed:\n- ' + '\n- '.join(problems))
print('Repository hygiene passed.')
''', encoding='utf-8')

# CSS cleanup: remove declarations now guaranteed by the final canonical identity lock.
refine = ROOT / 'assets/css/refine.css'
text = refine.read_text(encoding='utf-8')
replacements = (
    ('.research-identity>.research-index{display:block;font-size:16px;line-height:1;letter-spacing:.03em;color:#8B94A2}',
     '.research-identity>.research-index{display:block;letter-spacing:.03em;color:#8B94A2}'),
    ('.research-identity>.research-code-main>span{font-size:28px;line-height:1;letter-spacing:0;font-weight:650;color:var(--ink);white-space:nowrap}',
     '.research-identity>.research-code-main>span{letter-spacing:0;color:var(--ink);white-space:nowrap}'),
    ('    font-size:12px;line-height:1.3;letter-spacing:0;text-transform:none;\n    font-weight:500;max-width:none;color:#596577;',
     '    letter-spacing:0;text-transform:none;\n    font-weight:500;max-width:none;color:#596577;'),
    ('  .research-direction .research-identity>.research-code-main>span{font-size:36px}\n', ''),
    ('  .research-direction .research-identity>.research-code-main>.research-expansion{font-size:15px;line-height:1.3}\n', ''),
    ('  .research-grid .research-identity>.research-code-main>span{font-size:24px}\n', ''),
    ('  .research-grid .research-identity>.research-code-main>.research-expansion{font-size:11px}\n', ''),
    ('    font-size:11px;line-height:1.35;letter-spacing:0;text-transform:none;', '    letter-spacing:0;text-transform:none;'),
    ('    font-size:12px;\n    line-height:1;\n', ''),
    ('    font-size:25px;\n    line-height:1;\n    font-weight:680;\n', ''),
    ('    font-size:10.5px;\n    line-height:1.3;\n', ''),
)
for old, new in replacements:
    if old not in text:
        raise SystemExit('Expected refine.css cleanup target missing')
    text = text.replace(old, new, 1)

redundant = '''@media(min-width:1025px) and (max-width:1099px){
  .challenge-grid.divider-short-list>:nth-last-child(-n+2),
  .partner-grid.divider-short-list>:nth-last-child(-n+2){
    border-bottom:0!important;
  }
  :is(.research-grid,.updates-grid,.media-list).divider-short-list>:last-child{
    border-bottom:0!important;
  }
}
'''
if redundant not in text:
    raise SystemExit('Redundant divider block missing')
text = text.replace(redundant, '', 1)

migrated = '''
/* Consolidated rules migrated from the retired homepage-logo stylesheet. */
.home-hero .hero-grid{grid-template-columns:minmax(0,1fr);gap:0}
.home-hero .hero-grid>div:first-child{max-width:760px}

@media(min-width:1025px){
  .home-hero{padding-top:64px;padding-bottom:70px}
  .home-hero>.container{max-width:1060px}
  .home-hero~.section>.container{max-width:1000px}
  .home-hero~.section:has(.challenge-grid)>.container{max-width:1020px}
  .home-hero~.section:has(.research-grid)>.container{max-width:1100px}
  .home-hero~.section:has(.numbers)>.container{max-width:860px}
  .home-hero~.section:has(.partner-grid)>.container{max-width:980px}
  .home-hero~.section:has(.home-achievement-stories)>.container{max-width:1100px}
  .selected-updates>.container,.home-media-section>.container{max-width:960px}
  .home-hero~.section .title-section{font-size:38px!important;line-height:1.15!important}
  .home-hero~.section .eyebrow,.home-hero~.join .eyebrow{font-size:11px!important;letter-spacing:.145em!important}
  .home-hero~.section .title-item{font-size:19px!important;line-height:1.38!important}
  .home-hero~.section .research-title.title-feature{font-size:23px!important;line-height:1.28!important}
  .home-hero~.section :is(.challenge p,.research p,.partner p,.update-item p){font-size:16.5px;line-height:1.72}
  .home-hero~.section .text-link{font-size:14.5px}
  .home-hero~.section .media-title{font-size:15px;line-height:1.55}
  .home-hero~.section .media-meta{font-size:12px}
  .home-hero~.section:has(.partner-grid) .partner{padding-top:25px;padding-bottom:27px}
  .home-hero~.section:has(.partner-grid) .partner h3{font-size:20px!important;margin-bottom:12px}
  .home-hero~.section:has(.partner-grid) .partner p{font-size:16.5px;line-height:1.66}
  .home-hero~.section:has(.challenge-grid){padding-top:110px;padding-bottom:110px}
  .home-hero~.section:has(.research-grid){padding-top:110px;padding-bottom:112px}
  .home-hero~.section:has(.numbers){padding-top:90px;padding-bottom:92px}
  .home-hero~.section:has(.partner-grid){padding-top:96px;padding-bottom:98px}
  .home-hero~.section:has(.home-achievement-stories){padding-top:118px;padding-bottom:116px}
  .selected-updates{padding-top:106px;padding-bottom:106px}
  .home-media-section{padding-top:82px;padding-bottom:78px}
  .selected-updates .update-item h3{font-size:18.5px!important}
  .selected-updates .update-item p{font-size:15.5px;line-height:1.62}
  .home-media-section .media-list{line-height:1.5}
}
@media(min-width:769px){
  .home-achievement-stories{grid-template-columns:minmax(0,1.80961357fr) minmax(0,2.40903388fr) minmax(0,2.09150327fr);max-width:1077.18px;margin-inline:auto;gap:18px;justify-content:center;align-items:start}
  .home-achievement-story,.home-achievement-story>a{height:auto;width:100%}
  .home-achievement-story>a{display:block}
  .home-achievement-story img,.home-achievement-story:nth-child(3) img{display:block;width:100%!important;height:auto!important;max-width:none;margin:0;aspect-ratio:auto!important;object-fit:contain!important;object-position:center!important}
  .home-achievement-story figcaption{min-height:0}
}
:is(.team-grid img.person-photo,.page-person-detail .person-detail>.person-photo){display:block;width:100%;height:auto!important;max-height:none!important;aspect-ratio:auto!important;object-fit:contain!important;object-position:center!important;background:#f2f3f5;border:1px solid var(--line)}
@media(min-width:1025px){
  .join-context .section-head p:first-of-type{grid-row:1 / span 2}
  .join-context .section-head p+p{grid-row:auto;margin-top:8px}
}
'''
if 'Consolidated rules migrated from the retired homepage-logo stylesheet' in text:
    raise SystemExit('Migrated CSS already present')
refine.write_text(text.rstrip() + '\n' + migrated, encoding='utf-8')

# Self-delete after execution; the workflow deletes itself separately.
Path(__file__).unlink(missing_ok=True)
