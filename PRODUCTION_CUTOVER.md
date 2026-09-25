# PAI Website Production Cutover

This repository currently serves a GitHub Pages preview/review site. Keep preview behavior stable until the official production domain is ready.

## Current stable contracts

- English navigation uses **Outputs** while the stable route remains `/en/publications.html`.
- The homepage achievement images are committed with `loading="eager"` and `decoding="sync"` in both languages to avoid iPhone Safari image flicker during lightweight navigation.
- The mobile top menu and orbit menu are mutually exclusive through real toggle transitions; the center-plus control remains available.
- Shared navigation, swipe, scroll restoration and lightweight page switching remain in `assets/js/site.js` and should not be reworked during cutover.
- `sw.js` is only a legacy cache-retirement stub; do not restore a page-caching Service Worker during cutover.

## Preview environment

Preview URL:

`https://tjpai.github.io/pai-web/`

Preview-specific behavior:

- `robots.txt` blocks indexing.
- sitemap/canonical/hreflang/Open Graph URLs use the GitHub Pages preview domain.
- `site.js` treats `tjpai.github.io` as the preview host and applies the `/pai-web` prefix where required.

Do not make the preview copy indexable as a substitute for production.

## Production target

Target domain:

`https://ai.tongji.edu.cn/`

Perform these changes only when the production host is actually ready:

1. Replace Preview-domain URLs in `sitemap.xml` with `https://ai.tongji.edu.cn/`, preserving all Chinese/English/x-default alternates.
2. Replace Preview `robots.txt` with a production version that allows indexing and references `https://ai.tongji.edu.cn/sitemap.xml`.
3. Replace Preview-domain canonical, hreflang, Open Graph and structured-data URLs in all Chinese and English HTML with the production domain.
4. Confirm all local asset paths work from the production root, including the independently injected mobile-menu exclusivity helper.
5. Confirm `404.html` is served as the actual error document and returns HTTP 404.
6. Add ICP/public-security filing details only after official values are confirmed.
7. Add redirects only for legacy URLs that genuinely need continuity.
8. Keep homepage achievement images eager/sync; do not reintroduce lazy/async loading during cutover.
9. Do not introduce CDN fonts or unnecessary third-party scripts during the cutover.

## Required checks before cutover

Run:

`python tools/sync_shared_head.py --check`

`python tools/validate.py`

`python tools/prepare_home_assets.py`

`python tools/validate_home_assets.py`

`python tools/validate_outputs_label.py`

`python tools/validate_share_metadata.py`

`python tools/check_production_readiness.py`

and JavaScript syntax checks for:

- `assets/js/site.js`
- `assets/js/menu-exclusive.js`
- `sw.js`

The production readiness check is expected to fail while the repository still intentionally points at the GitHub preview environment. At actual cutover, all checks must pass.

## Manual verification

Before tagging the production release, verify on real devices and desktop:

- Chinese and English homepages;
- all top-level navigation pages;
- People overview and faculty detail pages;
- Outputs / 研究成果 pages and publication links;
- language switching with supported anchors;
- top mobile menu and orbit-menu mutual exclusion;
- swipe navigation and scroll restoration;
- homepage image return/re-entry behavior on iPhone Safari;
- homepage logo animation;
- share preview metadata;
- 404 behavior.

After production verification, tag the release, for example `v1.0.0`.
