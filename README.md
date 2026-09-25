# PAI Research Center Website

Static bilingual website for the PAI Research Center at Tongji University.

## Structure

- Chinese pages live at repository root.
- English pages live under `en/`.
- Shared runtime: `assets/js/site.js`.
- Shared presentation entry point: `assets/css/refine.css`.
- Publication data: `data/publications.json` and `data/publications-archive.json`.
- Faculty detail pages: `people/` and `en/people/`.

## Current English terminology

The English navigation label is **Outputs** while the stable route remains `en/publications.html`.

## Homepage image stability

The three documentary images in the homepage achievement section are committed directly with `loading="eager"` and `decoding="sync"` in both Chinese and English homepages. This is an intentional iPhone Safari stability requirement. Do not change them back to lazy/async loading.

`tools/prepare_home_assets.py` is an idempotent deployment safeguard, and `tools/validate_home_assets.py` verifies the source remains Safari-safe.

## Validation

GitHub Pages runs the following checks before deployment:

- shared first-paint template consistency;
- site/link/content validation;
- homepage image stability;
- Outputs terminology;
- share metadata;
- JavaScript syntax.

See `MAINTENANCE.md` for detailed maintenance rules and `PRODUCTION_CUTOVER.md` for production-domain cutover steps.

## Preview

The GitHub Pages site is a preview/review environment. `robots.txt` intentionally blocks indexing until the production cutover.
