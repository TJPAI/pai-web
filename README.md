# PAI Web

Official website repository for the PAI Research Center at Tongji University.

## Maintenance status

The current site is stable. Prefer small, atomic changes and avoid broad refactors unless a concrete issue requires them.

Key constraints:
- Treat `main` as the source of truth.
- Preserve the iPhone/Safari navigation and swipe behavior in `assets/js/site.js`.
- Keep the mobile top menu and orbit menu mutually exclusive through their actual state transitions.
- Keep the English UI label `Outputs` while the URL remains `/en/publications.html`.
- Do not re-enable the legacy Service Worker; `sw.js` is a retirement stub that clears old `pai-site-*` caches.
- Keep preview indexing blocked until the production-domain cutover is explicitly performed.

## Main files

- `index.html`, `en/index.html` — Chinese and English homepages
- `assets/js/site.js` — shared navigation, page switching, swipe, publication loading and orbit behavior
- `assets/js/home-logo.js` — inline SVG homepage logo animation
- `assets/js/menu-exclusive.js` — mobile menu/orbit exclusivity helper
- `assets/css/refine.css` — shared presentation entry point
- `assets/css/typography.css` — canonical title typography
- `tools/validate.py` — structural and content validation
- `tools/validate_share_metadata.py` — share metadata consistency checks
- `tools/validate_home_assets.py` — homepage achievement-image and lazy-loading checks
- `MAINTENANCE.md` — detailed implementation notes
- `PRODUCTION_CUTOVER.md` — production-domain migration checklist

## Deployment

GitHub Pages deploys from `main` through `.github/workflows/pages.yml`. A change is considered deployed only after the workflow completes successfully.
