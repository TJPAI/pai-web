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
- For books and other formal publications, use the publisher's full official title and preserve authorship accurately; do not present a co-authored work as a sole-authored work.
- The six core-faculty photos are already local production assets under `/assets/images/people/`; do not reintroduce temporary-site image URLs.

## Bilingual pages
Chinese pages live at repository root. English pages live under `/en/`.
Keep the Chinese/English switch linked to the corresponding page, not always the homepage.
Keep paired Chinese/English URLs symmetric in `sitemap.xml` and in the language map inside `assets/js/site.js`.

## News and featured content
Only completed or verified events should be published. If there are no suitable verified news items, omit the homepage News module rather than using demo content.

## Assets
Prefer local files under `/assets/` for production. Avoid CDN fonts and nonessential third-party scripts.
The canonical static PAI mark is `assets/images/brand/pai-logo.svg`; Header branding should reference this asset rather than duplicating the SVG path in CSS.

### Homepage logo motion
- The verified 5-second homepage logo animation is `assets/media/pai-logo-motion.mp4`.
- `assets/js/home-logo.js` mounts it into the homepage intro area on Chinese and English homepages.
- On mobile, keep the approved centered placement below the Header.
- On desktop, keep the motion mark in the right-side whitespace so it never overlaps the hero headline.
- Keep it muted, `playsinline`, non-looping; after completion it holds briefly and then fades away without shifting the page layout.
- The Header uses the final static PAI mark while retaining `Tongji University` beneath it.
- Whenever `home-logo.css` or `home-logo.js` changes, bump the corresponding query-string cache key in both `index.html` and `en/index.html` so Safari does not keep the previous motion behavior.
- Do not move the animation into the shared navigation/page-swipe code unless there is a concrete integration need.

### Orbit navigation
- The orbit / center-plus navigation is a mobile interaction aid and is hidden at desktop widths (`min-width: 769px`).
- Desktop uses the full top navigation instead; do not show both navigation systems at the same time.
- Keep the existing mobile orbit behavior and page-swipe blocking rules unchanged unless a concrete mobile bug is reproduced.

### Mobile WebView compatibility
- iOS WeChat can retain old CSS more aggressively than Safari. When changing shared mobile typography in `refine.css`, bump the `refine.css` query-string cache key on both homepages before evaluating WeChat screenshots.
- Keep the mobile text autosizing guard in `refine.css`; do not compensate for a stale WebView cache by permanently shrinking Safari typography.
- `refine.css` remains the canonical presentation entry point and imports `refine-base.css`, `app-core.css`, and `typography.css` in that order. Do not link or bundle those internal layers directly from HTML; preserve the validated cascade.

## Validation
For normal development / Preview deployment, run:

`python tools/validate.py`

The GitHub Pages workflow also runs this check before deployment. Do not weaken the validator merely to make a release pass; fix the underlying link or data issue.

Immediately before production cutover, also run:

`python tools/check_production_readiness.py`

The production readiness check is intentionally expected to fail while the repository is still configured for GitHub Preview. It checks production robots/sitemap state, Preview-domain leakage, temporary-site image dependencies and forbidden publication PDF fields.

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
Already completed before cutover:
- six core-faculty photos are local under `/assets/images/people/` and Team pages use local relative paths;
- canonical Header mark is local under `/assets/images/brand/pai-logo.svg`.

Do only at the actual production cutover to `https://ai.tongji.edu.cn/`:
- replace every Preview-domain URL in `sitemap.xml` with `https://ai.tongji.edu.cn/...` while preserving the symmetric `zh-CN` / `en` / `x-default` alternates;
- replace Preview `robots.txt` with a production version that allows indexing and points to `https://ai.tongji.edu.cn/sitemap.xml`;
- replace hard-coded Preview-domain canonical / hreflang / Open Graph URLs in Chinese and English HTML with the production domain, then verify the rendered output;
- confirm `404.html` is configured as the server's real 404 error document and still returns HTTP 404;
- add ICP / public-security filing information only when the official values are confirmed;
- define redirects only for important legacy URLs that need continuity;
- run `python tools/validate.py` and then `python tools/check_production_readiness.py`; both must pass;
- run a final phone + desktop, Chinese + English, navigation + publication-link check;
- after production verification, tag the release (for example `v1.0.0`).
