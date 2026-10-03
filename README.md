# PAI Research Center Website

Static bilingual website for the PAI Research Center at Tongji University.

## Structure

- Chinese pages: repository root.
- English pages: `en/`.
- Shared runtime: `assets/js/site.js`.
- Shared presentation entry point: `assets/css/refine.css`.
- Publication data: `data/publications.json` and `data/publications-archive.json`.
- Faculty detail pages: `people/` and `en/people/`.
- Environment/domain configuration: `config/site.json`.

## Stable content contracts

- English navigation uses **Outputs** while the stable route remains `en/publications.html`.
- The three homepage documentary images intentionally use `loading="eager"` and `decoding="sync"` for iPhone Safari stability. Do not change them to lazy/async without a reproduced device-level reason.
- `sw.js` is a legacy Service Worker retirement stub; page caching is not provided by a Service Worker.

## Deployment paths

The repository intentionally has two delivery paths with different purposes.

### Preview: GitHub Pages

`.github/workflows/pages.yml` builds and deploys the public Preview site. It:

1. validates shared head/content/accessibility/manifest/SEO/link/output contracts;
2. verifies production prerequisites with a non-mutating preflight;
3. prepares Preview URLs and crawl policy from `config/site.json`;
4. prepares share metadata and validates JavaScript/navigation assets;
5. applies narrowly scoped deployment runtime optimizations;
6. bundles the layered `refine.css` stack into one deployed stylesheet;
7. stamps deployed local CSS/JS references with content-derived cache hashes;
8. stages an explicit `_site/` public tree;
9. uploads and deploys only that public tree to GitHub Pages.

The same workflow also performs a separate, non-deploying production-server dry run on every `main` push. That job temporarily selects the production profile in an isolated checkout and proves that the official-server artifact can be built successfully.

### Production: validated server package

`.github/workflows/production-artifact.yml` is a manual `workflow_dispatch` workflow for the official server. It temporarily selects the production profile, runs the strict production checks, builds the same optimized `_site/` tree, removes the GitHub Pages-only `CNAME`, and uploads:

`pai-web-production.zip`

The ZIP is the validated production package to deploy to the institutional server / site-management platform. It is not automatically deployed by GitHub Actions.

Source CSS remains layered for maintainability. `refine.css` imports the base, app, typography, and desktop layout layers in order; deployment bundles them into one stylesheet without an `@import` request waterfall.

Both public artifacts exclude repository/build internals and `geosketch-mvp`; the geometry MVP remains in the repository but is not published under the PAI website domain.

## Environment profiles

`config/site.json` is the single source of truth for Preview vs Production URLs.

The committed/default mode remains:

`active_environment: "preview"`

Preview uses `https://tjpai.github.io/pai-web/` and blocks indexing. Production is preconfigured for `https://ai.tongji.edu.cn/` and enables indexing.

For the official server package, do **not** change `active_environment` on `main`. The production artifact workflow switches only its isolated CI workspace to production, leaving the Preview source state unchanged.

Do not manually search-and-replace Preview URLs across HTML, sitemap or robots files.

## Cache keys

Do not manually bump deployed CSS/JS query strings for ordinary changes. The build workflow computes cache keys from the final asset contents after runtime preparation and CSS bundling.

The source-level cache-key checker still prevents inconsistent references between HTML files.

Generated deployment outputs are ignored by Git (`_site/`, the CSS bundle, generated `CNAME`, and production ZIP).

## Validation

The Preview Pages workflow continuously validates both the live Preview build and a full production-server dry run. Checks include:

- Python tooling syntax;
- shared first-paint template consistency;
- site/link/content structure;
- accessibility contracts;
- web manifest and icon dimensions;
- environment-aware SEO contracts;
- strict production readiness in the production dry run;
- homepage Safari image contracts;
- CTA links and Outputs terminology;
- share metadata;
- JavaScript syntax;
- shared navigation asset references;
- source cache-key consistency;
- prepared runtime syntax;
- public-artifact boundaries and production-domain markers.

See `MAINTENANCE.md` for maintenance rules and `PRODUCTION_CUTOVER.md` for the production-server checklist.
