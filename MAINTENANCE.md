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
- The English user-facing navigation label is `Outputs`; the stable URL remains `/en/publications.html`.

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
- The approved homepage logo animation is generated as inline SVG by `assets/js/home-logo.js` from the canonical one-stroke path used by the final PAI mark.
- The draw animation runs for about 5 seconds, holds briefly, then fades without shifting page layout.
- `assets/css/home-logo.css` controls placement and the fade/hidden states.
- On mobile, keep the approved centered placement below the Header.
- On desktop, keep the motion mark in the right-side whitespace so it never overlaps the hero headline.
- The animation is non-looping. Its `requestAnimationFrame` loop must stop when drawing completes; do not introduce a permanent animation timer.
- Respect `prefers-reduced-motion`: the final mark should appear without running the draw animation.
- Both homepages contain the final editorial structure in HTML. Lightweight navigation and swipe previews use that same markup; `home-logo.js` only manages the logo animation. Keep the canonical homepage image loading settings in previews and committed pages to avoid a visible handoff.
- The Header uses the final static PAI mark while retaining `Tongji University` beneath it.
- Whenever `home-logo.css` or `home-logo.js` changes, bump the corresponding query-string cache key in both `index.html` and `en/index.html` so Safari and WeChat do not keep the previous motion behavior.
- Do not move the animation into the shared navigation/page-swipe code unless there is a concrete integration need.

### Desktop homepage presentation
- At desktop widths, keep the top navigation slightly stronger than the mobile/tablet treatment, but do not increase Header height or reintroduce the orbit menu.
- Keep homepage imagery sparse and editorial rather than turning the page into a gallery.
- The current `Research Excellence / 代表性成果` block uses three documentary stories: Microsoft Indoor Localization Competition, CIIE high-precision localization / smart navigation, and through-the-earth magnetic communication.
- The three achievement images are self-hosted under `assets/images/home/` and are committed directly with `loading="eager"` and `decoding="sync"` in both homepages. Keep this Safari-safe setting; it prevents visible image re-entry/flicker when iPhone Safari returns to Home through lightweight navigation.
- `tools/prepare_home_assets.py` remains an idempotent deployment safeguard, and `tools/validate_home_assets.py` rejects regressions away from `eager` + `sync`.
- The homepage separately presents Collaboration Platforms and Media Coverage; do not fold those sections back into the achievement-image block.
- Documentary homepage images must preserve their native aspect ratio: use container-width scaling with `height:auto`; do not crop them with fixed heights, forced aspect ratios, or `object-fit:cover`.
- Keep the verified external source-page links on the achievement figures for provenance; do not hotlink display images from external sites.
- The desktop Footer intentionally has a little more vertical breathing room and stronger brand/navigation hierarchy than the compact mobile Footer.

### Orbit navigation
- The orbit / center-plus navigation is a mobile interaction aid and is hidden at desktop widths (`min-width: 769px`).
- Desktop uses the full top navigation instead; do not show both navigation systems at the same time.
- The top mobile menu and orbit menu share explicit state transitions in `site.js` (`setMobileMenu` and the orbit `setOpen`). Opening either directly closes the other; do not simulate button clicks to coordinate them. Classes, ARIA state and auto-rotation must stay synchronized.
- Navigation helper references are committed in HTML and validated with `python tools/sync_navigation_scripts.py --check`; deployment must not inject an additional behavior layer. Use the same tool without `--check` after adding a page.
- Keep the existing mobile orbit behavior and page-swipe blocking rules unchanged unless a concrete mobile bug is reproduced.

### Mobile WebView compatibility
- iOS WeChat can retain old CSS more aggressively than Safari. When changing shared mobile typography in `refine.css`, bump the `refine.css` query-string cache key on both homepages before evaluating WeChat screenshots.
- Keep the mobile text autosizing guard in `refine.css`; do not compensate for a stale WebView cache by permanently shrinking Safari typography.
- Every directly accessible HTML page, not only the homepages, must use `viewport-fit=cover` and identify iOS WeChat in `<head>` before the main stylesheet/body paint so the intended 100% text scale is present from the first frame. This includes Chinese/English inner pages, faculty detail pages and `404.html`, because users may refresh or open any of them as the initial WebView entry point.
- The single source of truth for that first-paint block is `templates/shared/wechat-first-paint.inc`.
- Run `python tools/sync_shared_head.py --write` after changing the shared block or after adding a new HTML page. The script updates every deployable HTML page from the shared template.
- Run `python tools/sync_shared_head.py --check` to verify that no page has drifted. GitHub Pages runs this check automatically before deployment, so a new page cannot silently ship without the guard.
- Do not replace the first-paint guard with `maximum-scale=1` or `user-scalable=no`; user zoom must remain available.
- `refine.css` remains the canonical presentation entry point and imports `refine-base.css`, `app-core.css`, and `typography.css` in that order. Do not link or bundle those internal layers directly from HTML; preserve the validated cascade.

## Validation
For normal development / Preview deployment, run:

`python tools/sync_shared_head.py --check`

`python tools/validate.py`

The GitHub Pages workflow runs both checks before deployment, followed by share-metadata and runtime-syntax validation. Do not weaken the validators merely to make a release pass; fix the underlying template, link or data issue.

Immediately before production cutover, also run:

`python tools/check_production_readiness.py`

The production readiness check is intentionally expected to fail while the repository is still configured for GitHub Preview. It checks production robots/sitemap state, Preview-domain leakage, temporary-site image dependencies and forbidden publication PDF fields.

## Release flow
1. Edit content/code.
2. If a shared first-paint or new-page change is involved, run `python tools/sync_shared_head.py --write`.
3. Run shared-head and site validation.
4. Review Chinese + English on mobile and desktop.
5. Check publications, links, images and contact information.
6. Merge/deploy only after checks pass.
7. Tag formal releases, e.g. `v1.0.0`.

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
- run `python tools/sync_shared_head.py --check`, `python tools/validate.py` and then `python tools/check_production_readiness.py`; all must pass;
- run a final phone + desktop, Chinese + English, navigation + publication-link check;
- after production verification, tag the release (for example `v1.0.0`).

## Platform content ownership
- Platform descriptions, headings and display order live in `about.html` and `en/about.html`. Never replace readable text with CSS pseudo-elements or identify platforms by their sibling position.
- Use stable `platform-journal`, `platform-conference`, `platform-community`, `platform-china` and `platform-center` classes for scoped presentation.
