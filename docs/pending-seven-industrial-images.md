# Seven new industrial achievements — pending image assets

This draft adds achievements 15–21 immediately following DWELT on both bilingual Outputs pages.

Seven user-supplied graphics must be placed under `assets/images/technology/` **before merge**:

| No. | Asset |
| --- | --- |
| 15 | uwb-nearlink-direction-finding-radar-sensing.jpg |
| 16 | short-range-wireless-ranging-localization.jpg |
| 17 | nearlink-wireless-protocol-stack.jpg |
| 18 | nearlink-communication-positioning.jpg |
| 19 | vision-language-drone-target-discovery.jpg |
| 20 | autonomous-drone-navigation-obstacle-avoidance.jpg |
| 21 | autonomous-drone-industrial-inspection.jpg |

All seven images were provided as the original JPEG uploads in the conversation. This GitHub PR intentionally stays draft until the original user-provided images are committed; the current branch only contains page content and references.

Before merging: verify bilingual image paths, all 7 contact links, card order, mobile layout, packaging manifest, and no publication/award regression. The Boda production baseline confirmed by user is `5729db3c`.

## Two existing technology image replacements (2026-11-27)

Use user-uploaded JPEG bytes, unchanged, to replace the existing assets at these exact paths. The original `.jpg` extensions should stay to avoid HTML/CSS changes; JPG and JPEG are the same JPEG image format. Do not reconvert to WebP or recompress.

- `assets/images/technology/multimodal-embodied-ai-brain.jpg` ← `48EC1402-BB77-4C25-8C7C-7A9AFE5D2BB1_compressed_5(1).jpeg` (187410 bytes, SHA-256 begins `b1c24bc3007bcde1`)
- `assets/images/technology/digital-twin-ai-platform.jpg` ← `3F2534EC-168D-4CE5-B87F-EF20DE85875C_compressed(1).jpeg` (169793 bytes, SHA-256 begins `d800bd8f17a21ba2`)

A verified path-preserving ZIP is `PAI-Web-2-Replacement-Original-JPEG-Images.zip` in the conversation. This commit documents the change; binary image replacements must still be uploaded into the draft branch before merge. Do not mistakenly claim repository image bytes changed yet.
