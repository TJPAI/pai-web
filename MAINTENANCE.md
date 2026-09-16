# PAI Website Maintenance Guide

This site is a static bilingual website. Keep changes small, reviewable, and factual.

## Publications
- Recent papers: `data/publications.json`
- Archive papers: `data/publications-archive.json`
- Required fields: `year`, `title`, `authors`, `venue`
- Optional: `doi`, `pdf`
- Do not add a DOI or PDF link unless verified.
- PDFs do not need to be stored in this repository; use verified DOI, publisher or arXiv links where appropriate.

## Team
- Overview: `team.html`
- Faculty detail pages: `people/*.html`
- Use lowercase English filenames and stable slugs.
- Only publish verified titles, bios, honors and contact details.

## Bilingual pages
Chinese pages live at repository root. English pages live under `/en/`.
Keep the Chinese/English switch linked to the corresponding page, not always the homepage.

## News and featured content
Only completed or verified events should be published. If there are no suitable verified news items, omit the homepage News module rather than using demo content.

## Assets
Prefer local files under `/assets/` for production. Avoid CDN fonts and nonessential third-party scripts. Faculty photos currently referenced from the temporary Tongji site must be copied locally before final production cutover.

## Validation
Run:

`python tools/validate.py`

The GitHub Pages workflow also runs this check before deployment.

## Release flow
1. Edit content/code.
2. Run validation.
3. Review Chinese + English on mobile and desktop.
4. Check publications, links, images and contact information.
5. Merge/deploy only after checks pass.
6. Tag formal releases, e.g. `v1.0.0`.

## Preview environment
`https://tjpai.github.io/pai-web/` is a development and review environment only. Its `robots.txt` blocks indexing, and `site.js` adds `noindex,nofollow` on the GitHub preview host. The same JavaScript automatically uses `https://ai.tongji.edu.cn` as the canonical origin after deployment there.

## Production cutover
Before replacing the temporary site at `https://ai.tongji.edu.cn/`:
- copy faculty photos into local `/assets/images/people/` paths and update Team + faculty detail pages;
- replace preview `sitemap.xml` URLs with `https://ai.tongji.edu.cn/...`;
- replace preview `robots.txt` with a production version that allows indexing and points to the production sitemap;
- verify canonical / hreflang output on Chinese and English pages;
- add final ICP / public-security filing information only when the official values are confirmed;
- verify redirects from important legacy URLs;
- run a final mobile/desktop and bilingual check.
