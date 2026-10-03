# PAI Website Production Cutover

The repository keeps GitHub Pages as the stable Preview/review site. The official `https://ai.tongji.edu.cn/` deployment is produced as a validated server package and is not deployed automatically by the Pages workflow.

## Stable contracts

- English navigation uses **Outputs** while the stable route remains `/en/publications.html`.
- Homepage documentary images remain `loading="eager"` + `decoding="sync"` for iPhone Safari stability.
- Shared navigation, swipe, scroll restoration and lightweight page switching remain owned by `assets/js/site.js`.
- `sw.js` is only a legacy Service Worker retirement stub; do not restore page-caching Service Worker behavior during cutover.
- Build-time CSS bundling and content-hash cache keys are part of both Preview and production artifacts and require no manual version bump.

## Environment profiles

Environment/domain state is defined in:

`config/site.json`

Committed/default Preview profile:

- base URL: `https://tjpai.github.io/pai-web/`
- indexing: disabled
- custom domain: none

Production profile:

- base URL: `https://ai.tongji.edu.cn/`
- indexing: enabled
- configured host: `ai.tongji.edu.cn`

Do **not** change `active_environment` on `main` merely to build the official server package. The production artifact workflow switches only its isolated CI workspace to production, so the GitHub Pages Preview can remain stable.

Do not manually search-and-replace Preview URLs across HTML files, sitemap or robots.

## Continuous production dry run

Every normal Pages deployment also runs a separate `Validate production server build` job. It temporarily selects the production profile and validates the complete production build without publishing it.

The dry run covers:

- strict production readiness;
- canonical / hreflang / Open Graph / JSON-LD URLs;
- production `robots.txt` and `sitemap.xml`;
- share metadata;
- runtime preparation;
- CSS bundling and content-hash stamping;
- `_site/` public-artifact boundaries;
- removal of Preview-domain URLs;
- exclusion of `geosketch-mvp`;
- server-artifact behavior without a `CNAME` file.

A red production dry-run job should be treated as a release blocker even if Preview still deploys successfully.

## Build the official server package

Run the GitHub Actions workflow:

**Build production server artifact**

This manual workflow:

1. checks out the current repository state;
2. renders crawlable publication HTML;
3. switches only the CI workspace to the production profile;
4. runs the strict production readiness and validation pipeline;
5. creates the optimized `_site/` tree;
6. removes the GitHub Pages-only `CNAME` file;
7. asserts the production-domain and artifact-boundary contracts;
8. packages the result as `pai-web-production.zip`;
9. uploads the ZIP as a GitHub Actions artifact for 30 days.

The ZIP contents, not the repository root, are the production web files to deploy.

## External cutover steps

Repository automation cannot perform the institutional hosting actions by itself:

1. Confirm the target server/site-management platform for `ai.tongji.edu.cn` is ready.
2. Run **Build production server artifact** from the exact commit intended for release.
3. Download `pai-web-production.zip` and deploy its contents to the production web root using the institutional hosting process.
4. If the site-management platform generates or requires its own `index.jsp`, keep that server-side wrapper as required; do not overwrite a working platform-generated entry file unless intentionally replacing it.
5. Confirm DNS, HTTPS certificate and public-network resolution for `ai.tongji.edu.cn`.
6. Verify that the server serves the uploaded static assets with the intended paths and MIME types.

GitHub Pages Custom domain configuration is **not** part of this server-package deployment path.

## Production verification

After the production package is deployed, verify:

- `https://ai.tongji.edu.cn/` returns the Chinese homepage;
- `/en/` returns the English homepage;
- canonical / hreflang / Open Graph / JSON-LD contain only the production domain;
- `robots.txt` allows intended crawling and points to the production sitemap;
- `sitemap.xml` contains production URLs and bilingual alternates;
- no Preview-domain URLs remain in the deployed SEO surface;
- all local assets resolve from the production root;
- `geosketch-mvp` is not exposed under the PAI production site;
- the production package does not contain a GitHub Pages `CNAME` file;
- `404.html` is served with correct 404 behavior by the production host;
- language switching, lightweight navigation, Back/Forward scroll restoration and mobile swiping still work;
- top mobile menu and orbit menu remain mutually exclusive;
- homepage Logo animation behaves correctly and respects reduced motion;
- homepage documentary images remain stable on iPhone Safari;
- cross-page anchor links land directly below the fixed Header;
- Outputs publication data and DOI links load correctly;
- share previews use the generated square PAI image.

## Automated checks

The normal Pages workflow continuously checks Preview and a complete production-server dry run. The manual production-artifact workflow repeats the strict production build before packaging.

The strict production readiness command remains:

`python tools/check_production_readiness.py`

It is run after the CI workspace has selected the production profile.

## Content/infrastructure items requiring factual confirmation

- Add ICP/public-security filing information only after official values are confirmed.
- Add redirects only for legacy URLs that genuinely require continuity.
- Do not introduce CDN fonts, analytics, or third-party scripts simply as part of cutover.
- Server compression, HTTP protocol support and security headers are hosting/platform concerns and should be configured at the institutional server layer when available; they are not implemented by static HTML/CSS/JS files.

## Release

After the production server package, DNS/HTTPS and real-device behavior are verified, tag the formal production release (for example `v1.0.0`).
