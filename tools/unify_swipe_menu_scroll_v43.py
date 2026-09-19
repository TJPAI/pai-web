from pathlib import Path
import re

js_path=Path('assets/js/site.js')
js=js_path.read_text()

# Canonical destination scroll source shared by menu and swipe.
needle="const rememberedPageScroll=path=>Math.max(0,Number(pageScrollPositions[path])||0);"
replacement="""const rememberedPageScroll=path=>Math.max(0,Number(pageScrollPositions[path])||0);
  const destinationScrollForPath=path=>rememberedPageScroll(path);"""
if needle not in js:
    raise SystemExit('rememberedPageScroll declaration not found')
js=js.replace(needle,replacement,1)

js=js.replace("options={preserveScrollY:rememberedPageScroll(normalizedPath(url.pathname))};",
              "options={preserveScrollY:destinationScrollForPath(normalizedPath(url.pathname))};",1)

js=js.replace("const targetScroll=rememberedPageScroll(targetPath);",
              "const targetScroll=destinationScrollForPath(targetPath);",1)

old="""    /* Handoff at exactly the vertical position the user already sees in the preview.
       Re-reading an unclamped remembered value here can cause a visible correction jump. */
    const targetScroll=Number.isFinite(preview.previewScroll)?preview.previewScroll:rememberedPageScroll(normalizedPath(targetUrl.pathname));
"""
new="""    /* Menu and swipe must land from the exact same saved position source.
       applyPage performs the same final clamp against the real document in both cases. */
    const targetScroll=Number.isFinite(preview.targetScroll)
      ?preview.targetScroll
      :destinationScrollForPath(normalizedPath(targetUrl.pathname));
"""
if old not in js:
    raise SystemExit('v41 commit scroll block not found')
js=js.replace(old,new,1)

js=js.replace("/* Direct link/menu navigation restores the target page's last position.\n         Swipe navigation remains intentionally top-aligned via preserveScrollY: 0. */",
              "/* Direct/menu navigation and swipe navigation share one saved position source. */",1)

js_path.write_text(js)

# Force the same cache generation across all HTML so Safari cannot mix geometry versions.
for path in Path('.').rglob('*.html'):
    text=path.read_text()
    text=re.sub(r'(assets/css/site\.css)(?:\?v=[^\"\']+)?', r'\1?v=20260920-43', text)
    text=re.sub(r'(assets/js/site\.js)(?:\?v=[^\"\']+)?', r'\1?v=20260920-43', text)
    path.write_text(text)

# trigger workflow
