# PAI Website Maintenance Guide

This site is a static bilingual website. Keep changes small, reviewable, and factual.

## Publications
- Recent papers: `data/publications.json`
- Archive papers: `data/publications-archive.json`
- Required fields: `year`, `title`, `authors`, `venue`
- Optional: `doi`, `pdf`
- Do not add a DOI or PDF link unless verified.

## Team
- Overview: `team.html`
- Faculty detail pages: `people/*.html`
- Use lowercase English filenames and stable slugs.
- Only publish verified titles, bios, honors and contact details.

## Bilingual pages
Chinese pages live at repository root. English pages live under `/en/`.
Keep the Chinese/English switch linked to the corresponding page, not always the homepage.

## News and featured content
When structured news data is introduced, use stable slugs and reverse chronological dates. Only completed or verified events should be presented as achievements.

## Assets
Prefer local files under `/assets/` for production. Avoid CDN fonts and nonessential third-party scripts. Faculty photos currently referenced from the legacy Tongji site should be copied locally before final production cutover.

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

## Production cutover
Before moving from the GitHub preview to `ai.tongji.edu.cn`:
- replace preview-domain canonical/sitemap URLs with the production domain;
- localize faculty images and important PDFs;
- add final ICP / public-security filing information;
- verify redirects from important legacy URLs;
- run a final mobile/desktop and bilingual check.
