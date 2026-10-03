# Stable Baseline

Confirmed stable baseline: **2026-10-03**

- Commit: `d50bf290c075bac2aa6b69c27ded17294129feec`
- Snapshot branch: `stable-2026-10-03`
- GitHub Pages run: `#1257` (`37067328158`), completed successfully

This baseline was verified after the site-wide divider, section-background, page-structure and cross-page anchor cleanup.

## Regression-protected behavior

Future changes should preserve these behaviors unless a reproduced bug requires changing them:

- iPhone Safari homepage stability and documentary-image loading behavior;
- homepage logo animation behavior;
- fixed/mobile header behavior and mobile menu/orbit interaction;
- horizontal swipe navigation and Back/Forward scroll restoration;
- lightweight page navigation;
- cross-page anchor landing for the three Research Explore links, platform information, media coverage and Join → Contact Us;
- anchor targets align to the live header edge after lightweight navigation;
- explicit `divider-wide` / `divider-short-list` hierarchy and responsive final-row behavior;
- explicit `page-*` page identities rather than DOM-inference selectors;
- Chinese/English structural parity;
- Publications default visibility of two papers per year;
- Results 01–06 continuity;
- Service Worker retirement behavior;
- CSS deployment bundling and content-hash asset versioning.

## Change discipline

Use this baseline as the comparison point for future visual or interaction work. Prefer small isolated branches and shared structural rules over page-specific patches. Do not rewrite already verified navigation, Safari, divider or anchor behavior during unrelated cleanup.
