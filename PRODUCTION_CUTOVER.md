# PAI Website Production Cutover

This repository currently serves a GitHub Pages preview/review site. Keep Preview stable until the official production domain is ready.

## Stable contracts

- English navigation uses **Outputs** while the stable route remains `/en/publications.html`.
- Homepage documentary images remain `loading="eager"` + `decoding="sync"` for iPhone Safari stability.
- Shared navigation, swipe, scroll restoration and lightweight page switching remain owned by `assets/js/site.js`.
- `sw.js` is only a legacy Service Worker retirement stub; do not restore page-caching Service Worker behavior during cutover.
- Build-time CSS bundling and content-hash cache keys are part of the Pages artifact pipeline and require no manual version bump.

## Single environment switch

Environment/domain state is defined in:

`config/site.json`

Current Preview configuration:

- base URL: `https://tjpai.github.io/pai-web/`
- indexing: disabled
- custom domain: none

Production configuration is already defined as:

- base URL: `https://ai.tongji.edu.cn/`
- indexing: enabled
- custom domain: `ai.tongji.edu.cn`

At the actual cutover, change only:

`"active_environment": "preview"`

to:

`"active_environment": "production"`

The deployment pipeline then prepares the production form of:

- canonical URLs;
- `hreflang` URLs;
- Open Graph / Twitter asset URLs;
- owned JSON-LD URLs;
- `sitemap.xml`;
- `robots.txt`;
- `CNAME`.

Do not manually search-and-replace Preview URLs across HTML files, sitemap and robots.

## External cutover steps

Repository automation cannot perform these infrastructure actions by itself:

1. Configure DNS for `ai.tongji.edu.cn` according to the hosting setup.
2. Set the GitHub Pages **Custom domain** to `ai.tongji.edu.cn` and confirm HTTPS provisioning/enforcement.
3. Confirm the production site resolves over HTTPS from public networks.

Do not switch the repository environment until the external domain is ready to serve the Pages deployment.

## Production verification

After switching `active_environment` and deploying, verify:

- `https://ai.tongji.edu.cn/` returns the Chinese homepage;
- `/en/` returns the English homepage;
- canonical / hreflang / Open Graph / JSON-LD contain only the production domain;
- `robots.txt` allows intended crawling and points to the production sitemap;
- `sitemap.xml` contains the production URLs and bilingual alternates;
- generated `CNAME` is `ai.tongji.edu.cn`;
- no Preview-domain URLs remain in the deployed SEO surface;
- all local assets resolve from the production root;
- `404.html` is actually served with HTTP 404 behavior by the production host;
- language switching, lightweight navigation, Back/Forward scroll restoration and mobile swiping still work;
- top mobile menu and orbit menu remain mutually exclusive;
- homepage Logo animation behaves correctly and respects reduced motion;
- homepage documentary images remain stable on iPhone Safari;
- Outputs publication data and DOI links load correctly;
- share previews use the generated square PAI image.

## Required automated checks

The normal Pages deployment already runs the authoritative checks, including:

- shared first-paint template;
- site/content/link contracts;
- accessibility contracts;
- manifest/icon dimensions;
- SEO contracts;
- homepage image stability;
- CTA / Outputs contracts;
- share metadata;
- JavaScript syntax;
- navigation references;
- cache-key consistency;
- prepared runtime syntax;
- CSS bundle generation;
- content-hash stamping.

For production cutover, also verify:

`python tools/check_production_readiness.py`

The readiness check is expected to fail while `active_environment` is still Preview. It must pass against the production configuration before the formal production release is considered complete.

## Content/infrastructure items that still require factual confirmation

- Add ICP/public-security filing information only after official values are confirmed.
- Add redirects only for legacy URLs that genuinely require continuity.
- Do not introduce CDN fonts, analytics, or third-party scripts simply as part of cutover.

## Release

After production DNS/HTTPS and site behavior are verified on desktop and real phones, tag the formal production release (for example `v1.0.0`).
