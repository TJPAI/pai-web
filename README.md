# PAI Web

Static bilingual website for the PAI Research Center at Tongji University.

## Current status

The site is in a stable, small-change maintenance phase. Treat the current `main` branch and successful GitHub Pages deployment as the source of truth.

## Key entry points

- Chinese home: `index.html`
- English home: `en/index.html`
- Shared runtime/navigation: `assets/js/site.js`
- Homepage logo motion: `assets/js/home-logo.js`
- Mobile menu/orbit exclusivity: `assets/js/menu-exclusive.js`
- Shared presentation: `assets/css/refine.css`
- Content validation: `tools/validate.py`
- Share metadata validation: `tools/validate_share_metadata.py`
- GitHub Pages workflow: `.github/workflows/pages.yml`

## Maintenance rules

- Prefer small, atomic changes; avoid broad refactors.
- Protect iPhone Safari navigation, swipe, scroll restoration, page cache, orbit navigation and homepage logo motion unless a concrete bug is reproduced.
- English user-facing navigation uses **Outputs** while the stable URL remains `/en/publications.html`.
- Keep Chinese and English pages aligned.
- Do not re-enable a Service Worker without a specific requirement.
- Preview remains blocked from search indexing until the production-domain cutover is completed.

See `MAINTENANCE.md` for detailed implementation notes and `PRODUCTION_CUTOVER.md` for the production-domain checklist.

## Deployment

Pushes to `main` are validated and deployed through GitHub Pages. A change is considered live only after the Pages workflow completes successfully.
