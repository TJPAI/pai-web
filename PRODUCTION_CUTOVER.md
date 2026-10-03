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

Do **not** change `active_environment` on `main` merely to build the official server package. `tools/package_boda.py` copies the repository to a temporary build tree and selects production only there, so the GitHub Pages Preview remains unchanged.

Do not manually search-and-replace Preview URLs across HTML files, sitemap or robots.

## Single production build implementation

`tools/package_boda.py` is the source of truth for the official server build. It performs the full production validation and build sequence, including:

- strict production readiness;
- canonical / hreflang / Open Graph / JSON-LD URLs;
- production `robots.txt` and `sitemap.xml`;
- publication rendering;
- share metadata;
- JavaScript syntax checks;
- runtime preparation;
- CSS bundling and content-hash stamping;
- `_site/` public-artifact validation;
- removal of the GitHub Pages-only `CNAME`;
- exclusion of `geosketch-mvp`;
- removal of Preview-domain references;
- ZIP integrity validation.

Both the continuous production dry run and the manual release workflow call this same packager. There is no second production build recipe in the workflow YAML.

## Continuous production dry run

Every normal Pages deployment runs a separate `Validate production server build` job. It calls `tools/package_boda.py` and discards the resulting temporary ZIP after validation.

A red production dry-run job should be treated as a release blocker even if Preview still deploys successfully.

## Build the official server package

Run the GitHub Actions workflow:

**Build production server artifact**

This manual workflow is intentionally thin:

1. checks out the exact repository commit;
2. runs `python tools/package_boda.py --output pai-web-production.zip`;
3. uploads `pai-web-production.zip` as a GitHub Actions artifact for 30 days.

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

The normal Pages workflow continuously checks Preview and invokes the same production packager used for formal release. The manual production-artifact workflow invokes that packager again before uploading the ZIP.

For direct local verification, use:

`python tools/package_boda.py --output pai-web-production.zip`

## Content/infrastructure items requiring factual confirmation

- Add ICP/public-security filing information only after official values are confirmed.
- Add redirects only for legacy URLs that genuinely require continuity.
- Do not introduce CDN fonts, analytics, or third-party scripts simply as part of cutover.
- Server compression, HTTP protocol support and security headers are hosting/platform concerns and should be configured at the institutional server layer when available; they are not implemented by static HTML/CSS/JS files.

## Release

After the production server package, DNS/HTTPS and real-device behavior are verified, tag the formal production release (for example `v1.0.0`).
