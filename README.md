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

## Deployment pipeline

GitHub Pages builds a deployment artifact rather than publishing the repository byte-for-byte. The workflow:

1. validates shared head/content/accessibility/manifest/SEO/link/output contracts;
2. prepares URLs and crawl policy from `config/site.json`;
3. prepares share metadata;
4. validates JavaScript and navigation asset references;
5. applies narrowly scoped deployment runtime optimizations;
6. bundles the layered `refine.css` stack into one deployed stylesheet;
7. stamps deployed local CSS/JS references with content-derived cache hashes;
8. stages an explicit `_site/` public tree;
9. uploads and deploys only that public tree.

Source CSS remains layered for maintainability; deployed CSS is bundled to avoid an `@import` request waterfall.

The published site includes website HTML/assets/data plus the retained `geosketch-mvp` experience, but excludes repository/build internals such as `tools/`, `config/`, `.github/`, README and maintenance documents.

## Environment switch

`config/site.json` is the single source of truth for Preview vs Production URLs.

Current mode:

`active_environment: "preview"`

Preview uses `https://tjpai.github.io/pai-web/` and blocks indexing. Production is preconfigured for `https://ai.tongji.edu.cn/` and enables indexing. At production cutover, switch the active environment instead of manually replacing URLs across HTML/sitemap/robots.

DNS and the GitHub Pages **Custom domain** setting remain external configuration and must still be completed outside the repository.

## Cache keys

Do not manually bump deployed CSS/JS query strings for ordinary changes. The deployment workflow computes cache keys from the final asset contents after runtime preparation and CSS bundling.

The source-level cache-key checker still prevents inconsistent references between HTML files.

Generated deployment outputs are ignored by Git (`_site/`, the CSS bundle, generated square share PNG and generated `CNAME`).

## Validation

The Pages workflow currently validates:

- Python tooling syntax;
- shared first-paint template consistency;
- site/link/content structure;
- accessibility contracts;
- web manifest and icon dimensions;
- environment-aware SEO contracts;
- homepage Safari image contracts;
- CTA links and Outputs terminology;
- share metadata;
- JavaScript syntax;
- shared navigation asset references;
- source cache-key consistency;
- prepared runtime syntax.

See `MAINTENANCE.md` for maintenance rules and `PRODUCTION_CUTOVER.md` for the production-domain checklist.
