# PAI Website Production Cutover Runbook

Target production domain: `https://ai.tongji.edu.cn/`

This runbook is intentionally split into three phases. Do not apply production-only SEO changes while the GitHub Pages site is still being used as Preview.

## Current production-site observations — verified 2026-09-21

The public `https://ai.tongji.edu.cn/` site is still serving the legacy PAI website.

Observed from the public site:

- the site is effectively organized as a long single-page presentation of About / Research Team / research content rather than the new bilingual multi-page structure;
- legacy content still exposes image resources under the older `/new_web/image/` path family;
- the page still shows the José Luis Cordeiro lecture announcement for 2026-09-14, so the production copy has not yet been replaced by the new frozen candidate;
- the public page still reports `1 部学术专著（剑桥大学出版社，2024）`, while the new site uses the newer verified core-team aggregate of two academic monographs;
- the current public site can therefore be treated as the rollback source until the new release is fully verified.

These observations do **not** reveal the server-side deployment mechanism. Do not assume Nginx, Apache, FTP/SFTP, a CMS, or a reverse proxy solely from the public page.

### Five deployment facts to obtain from the Tongji-side administrator

Only these five answers are needed before the cutover can be executed safely:

1. **Deployment target** — what exact server path, site root, CMS slot, or publishing mechanism currently serves `ai.tongji.edu.cn`?
2. **Write method** — should the release be uploaded by SFTP/SSH, a school publishing console/CMS, a Git pull, or handed to an administrator for deployment?
3. **Web-server routing** — who can configure the real 404 document and any required legacy redirects?
4. **TLS / domain ownership** — who controls the HTTPS certificate and DNS / reverse-proxy binding for `ai.tongji.edu.cn`?
5. **Rollback method** — what exact operation restores the current legacy site, and where is its last known-good copy kept?

Do not change DNS or production routing until these five items are answered and the rollback operation is known.

## Phase A — Safe to complete before the cutover window

- [x] Core faculty images are local under `assets/images/people/`.
- [x] Canonical Header logo is local under `assets/images/brand/pai-logo.svg`.
- [x] Chinese and English top-level pages are paired.
- [x] Publication data is local and validated.
- [x] Preview blocks indexing through `robots.txt` and runtime `noindex,nofollow` behavior.
- [x] Normal Pages validation passes before deployment.
- [x] Public production-site structure and migration unknowns were rechecked on 2026-09-21.
- [ ] Recheck the final content freeze: homepage, About, People, Research, Publications, Join, Contact, and all faculty profiles in both languages.
- [ ] Recheck all external links that are meant to remain on the production site.
- [ ] Confirm official ICP / public-security filing values, if they are required and available. Do not add placeholders.
- [ ] Obtain the five Tongji-side deployment facts listed above.
- [ ] Confirm the rollback path to the existing site before changing the production server.

## Phase B — Execute only in the actual production cutover window

### 1. Freeze the release candidate

- [ ] Record the exact `main` SHA selected for production.
- [ ] Confirm the GitHub Pages workflow for that SHA is `completed / success`.
- [ ] Avoid unrelated content or visual changes after the release SHA is frozen.

### 2. Convert repository SEO metadata from Preview to production

Replace every hard-coded Preview origin `https://tjpai.github.io/pai-web` with `https://ai.tongji.edu.cn` in production-facing metadata, including:

- [ ] `<link rel="canonical">`
- [ ] `hreflang="zh-CN"`
- [ ] `hreflang="en"`
- [ ] `hreflang="x-default"`
- [ ] Open Graph `og:url`
- [ ] Open Graph / Twitter absolute share-image URLs
- [ ] JSON-LD `@id`, `url`, image URLs, and organization membership references where applicable
- [ ] `sitemap.xml`

Keep Chinese / English URL pairs symmetric.

### 3. Switch robots.txt to production mode

Replace the Preview-only blocking configuration with a production version that:

- [ ] allows normal indexing;
- [ ] does not contain `Disallow: /`;
- [ ] contains `Sitemap: https://ai.tongji.edu.cn/sitemap.xml`.

### 4. Run repository validation before publishing production files

Run:

```bash
python tools/validate.py
python tools/check_production_readiness.py
```

Both must pass. Do not weaken the validators to force a pass.

`tools/check_production_readiness.py` already fails when Preview URLs remain, when `robots.txt` still blocks the whole site, or when the production sitemap is missing.

### 5. Deploy the frozen production files to ai.tongji.edu.cn

- [ ] Publish the exact frozen release content using the confirmed Tongji-side deployment mechanism.
- [ ] Preserve relative asset paths and directory structure.
- [ ] Do not introduce a second copy of site CSS / JS outside the repository.
- [ ] Configure `404.html` as the actual HTTP 404 error document.
- [ ] Keep HTTPS enabled and confirm the certificate is valid for `ai.tongji.edu.cn`.
- [ ] If important legacy URLs exist, configure only verified redirects that are actually needed.
- [ ] Do not delete the legacy site backup until Phase C is complete.

## Phase C — Immediate post-cutover verification

### HTTP and metadata

- [ ] `https://ai.tongji.edu.cn/` returns HTTP 200.
- [ ] Representative Chinese and English pages return HTTP 200.
- [ ] A nonexistent path returns HTTP 404 while rendering the intended 404 page.
- [ ] `https://ai.tongji.edu.cn/robots.txt` is production-safe and references the production sitemap.
- [ ] `https://ai.tongji.edu.cn/sitemap.xml` contains only production URLs.
- [ ] No rendered canonical / hreflang / OG / JSON-LD output contains `tjpai.github.io/pai-web`.
- [ ] No production HTML references the old temporary image path `https://ai.tongji.edu.cn/new_web/image/`.

### iPhone Safari

Verify on a real iPhone, not only desktop responsive mode:

- [ ] Header logo renders sharply.
- [ ] Hamburger toggles to X and back without a gray tap box.
- [ ] Mobile menu navigation works.
- [ ] Horizontal page swipe works away from Safari edge gestures.
- [ ] Browser Back restores the expected page and scroll position.
- [ ] Long-press text selection does not trigger horizontal page navigation.
- [ ] Floating orbit menu opens, rotates, drags smoothly, remains open across page navigation, and closes only through its center toggle.
- [ ] Chinese / English switching lands on the corresponding page.
- [ ] Homepage logo animation behaves exactly as in the approved Preview version.
- [ ] Share preview uses the approved `assets/images/social/pai-share-v4.jpg` image.

### Desktop

- [ ] Main navigation, footer links, faculty profiles, publication links and contact links work.
- [ ] Chinese / English page pairs correspond correctly.
- [ ] No unexpected horizontal overflow or missing assets.

### Content spot checks

- [ ] Contact phone and email are correct.
- [ ] Three research directions use the approved wording.
- [ ] Faculty titles and bios match the content freeze.
- [ ] Publication / monograph titles use verified official wording and authorship.
- [ ] The old 2026-09-14 lecture notice is no longer the production homepage content unless intentionally republished elsewhere.

## Release completion

Only after all Phase C checks pass:

- [ ] Create the formal production release tag, e.g. `v1.0.0`.
- [ ] Record the production SHA and cutover date in this file or the release notes.
- [ ] Keep the GitHub Pages copy as Preview; do not make the Preview copy indexable unless there is a separate deliberate decision.

## Rollback trigger

Rollback to the previous production site if any of the following cannot be corrected promptly during the cutover window:

- homepage or core navigation is unavailable;
- HTTPS / certificate failure;
- major Chinese or English routes return incorrect HTTP status;
- static assets fail broadly;
- production metadata still points to Preview after deployment;
- mobile navigation / Safari page navigation is materially broken.

After rollback, keep the new build available only in Preview, fix the root cause, rerun both validators, and schedule a new cutover attempt.