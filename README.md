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

The English navigation label is **Outputs** while the stable route remains `en/publications.html`. English HTML source files must contain `Outputs` directly; deployment does not rewrite the label.

## Homepage image stability

The three documentary images in the homepage achievement section are committed directly with `loading="eager"` and `decoding="sync"` in both Chinese and English homepages. This is an intentional iPhone Safari stability requirement. Do not change them back to lazy/async loading.

`tools/validate_home_assets.py` verifies the source remains Safari-safe; deployment does not rewrite these image attributes.

## Validation

GitHub Pages runs the following checks before deployment:

- Python tooling syntax;
- shared first-paint template consistency;
- site/link/content validation;
- homepage image stability;
- Outputs terminology;
- share metadata;
- JavaScript syntax;
- mobile-menu helper injection/path validation;
- shared asset cache-key normalization and verification.

See `MAINTENANCE.md` for detailed maintenance rules and `PRODUCTION_CUTOVER.md` for production-domain cutover steps.

## Preview

The GitHub Pages site is a preview/review environment. `robots.txt` intentionally blocks indexing until the production cutover.
