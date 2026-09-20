# PAI Website Maintenance Guide

This site is a static bilingual website. Keep changes small, reviewable, and factual.

## Publications
- Recent papers: `data/publications.json`
- Archive papers: `data/publications-archive.json`
- Required fields: `year`, `title`, `authors`, `venue`
- Optional field: `doi`
- Do not add a DOI unless it has been verified.
- Do not add publication PDF files or `pdf` fields to `pai-web`. Use DOI / publisher links for formal publications. Use a verified arXiv link only when it is the appropriate public source.
- `tools/validate.py` rejects duplicate titles, duplicate DOI assignments, malformed publication records and `pdf` fields.

## Team
- Overview: `team.html`
- Faculty detail pages: `people/*.html`
- English faculty detail pages: `en/people/*.html`
- Use lowercase English filenames and stable slugs.
- Only publish verified titles, bios, honors and contact details.

## Bilingual pages
Chinese pages live at repository root. English pages live under `/en/`.
Keep the Chinese/English switch linked to the corresponding page, not always the homepage.
Keep paired Chinese/English URLs symmetric in `sitemap.xml` and in the language map inside `assets/js/site.js`.

## News and featured content
Only completed or verified events should be published. If there are no suitable verified news items, omit the homepage News module rather than using demo content.

## Assets
Prefer local files under `/assets/` for production. Avoid CDN fonts and nonessential third-party scripts.
Faculty photos currently referenced from the temporary Tongji site must be copied into `/assets/images/people/` and all Team / profile image URLs changed to local relative paths before formal cutover.

### Homepage logo motion
- The verified 5-second homepage logo animation is `assets/media/pai-logo-motion.mp4`.
- `assets/js/home-logo.js` mounts it only into the homepage `.hero-art` region on Chinese and English pages.
- Keep it muted, `playsinline`, non-looping, and preserve the existing static hero artwork as the fallback until the video is ready.
- Do not move the animation into the shared navigation/page-swipe code unless there is a concrete integration need.

## Validation
For normal development / Preview deployment, run:

`python tools/validate.py`

The GitHub Pages workflow also runs this check before deployment. Do not weaken the validator merely to make a release pass; fix the underlying link or data issue.

Immediately before production cutover, also run:

`python tools/check_production_readiness.py`

The production readiness check is intentionally expected to fail while the repository is still configured for GitHub Preview. It checks production robots/sitemap state, Preview-domain leakage, temporary-site faculty image dependencies and forbidden publication PDF fields.

## Release flow
1. Edit content/code.
2. Run validation.
3. Review Chinese + English on mobile and desktop.
4. Check publications, links, images and contact information.
5. Merge/deploy only after checks pass.
6. Tag formal releases, e.g. `v1.0.0`.

## Preview environment
`https://tjpai.github.io/pai-web/` is a development and review environment only.
Its `robots.txt` blocks indexing, and `site.js` adds `noindex,nofollow` on the GitHub preview host.
Do not change the Preview site into an indexable production copy.

## Production cutover
Before replacing the temporary site at `https://ai.tongji.edu.cn/`:
- copy the six core-faculty photos into local `/assets/images/people/` paths and update both Chinese and English Team / profile pages;
- replace every Preview-domain URL in `sitemap.xml` with `https://ai.tongji.edu.cn/...` while preserving the symmetric `zh-CN` / `en` / `x-default` alternates;
- replace Preview `robots.txt` with a production version that allows indexing and points to `https://ai.tongji.edu.cn/sitemap.xml`;
- verify canonical / hreflang / Open Graph output on Chinese and English pages after the site is served from the production domain;
- confirm `404.html` is configured as the server's real 404 error document and still returns HTTP 404;
- add ICP / public-security filing information only when the official values are confirmed;
- define redirects only for important legacy URLs that need continuity;
- run `python tools/validate.py` and then `python tools/check_production_readiness.py`; both must pass;
- run a final phone + desktop, Chinese + English, navigation + publication-link check;
- after production verification, tag the release (for example `v1.0.0`).
