#!/usr/bin/env python3
from pathlib import Path
import math, re, struct, zlib

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / 'assets/images/brand/pai-logo.svg'
OUT = ROOT / 'assets/images/social/pai-logo-share.png'
BASE_URL = 'https://tjpai.github.io/pai-web/'
OLD_IMAGE = BASE_URL + 'assets/images/social/pai-share-v4.jpg'
ICON_IMAGE = BASE_URL + 'assets/icons/icon-512.png'
NEW_IMAGE = BASE_URL + 'assets/images/social/pai-logo-share.png'

# WeChat renders link thumbnails in an almost-square viewport. Keep a square
# source, but let the approved PAI mark occupy most of the frame so it remains
# recognizable at the small thumbnail size used by WeChat.
WIDTH, HEIGHT = 1200, 1200
SS = 3
CANVAS_W, CANVAS_H = WIDTH * SS, HEIGHT * SS
BG = (255, 255, 255)
INK = (23, 26, 31)
TARGET_LOGO_W = 1040.0
VISUAL_SHIFT_X = 14.0

svg = SVG.read_text(encoding='utf-8')
path_match = re.search(r'<path\b[^>]*\bd="([^"]+)"', svg)
view_match = re.search(r'viewBox="([^"]+)"', svg)
stroke_match = re.search(r'stroke-width="([0-9.]+)"', svg)
if not (path_match and view_match and stroke_match):
    raise SystemExit('Canonical PAI logo SVG is missing expected path/viewBox/stroke-width data')

nums = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', path_match.group(1))]
if len(nums) < 4 or len(nums) % 2:
    raise SystemExit('Unexpected PAI logo path geometry')
points = list(zip(nums[0::2], nums[1::2]))
_, _, view_w, view_h = [float(v) for v in view_match.group(1).split()]
stroke_w = float(stroke_match.group(1))
scale = TARGET_LOGO_W / view_w
logo_h = view_h * scale
left = (WIDTH - TARGET_LOGO_W) / 2 + VISUAL_SHIFT_X
top = (HEIGHT - logo_h) / 2

pixels = bytearray(BG * (CANVAS_W * CANVAS_H))
ink_bytes = bytes(INK)

def set_px(x, y):
    if 0 <= x < CANVAS_W and 0 <= y < CANVAS_H:
        i = (y * CANVAS_W + x) * 3
        pixels[i:i+3] = ink_bytes

radius = max(1, int(round(stroke_w * scale * SS / 2)))

def draw_disk(cx, cy, r):
    x0 = max(0, int(cx - r))
    x1 = min(CANVAS_W - 1, int(cx + r))
    y0 = max(0, int(cy - r))
    y1 = min(CANVAS_H - 1, int(cy + r))
    rr = r * r
    for y in range(y0, y1 + 1):
        dy = y - cy
        for x in range(x0, x1 + 1):
            dx = x - cx
            if dx * dx + dy * dy <= rr:
                set_px(x, y)

def tx(p):
    x, y = p
    return ((left + x * scale) * SS, (top + y * scale) * SS)

for a, b in zip(points, points[1:]):
    x1, y1 = tx(a)
    x2, y2 = tx(b)
    dist = math.hypot(x2 - x1, y2 - y1)
    steps = max(1, int(math.ceil(dist / max(1, radius * 0.65))))
    for i in range(steps + 1):
        t = i / steps
        draw_disk(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t, radius)

small = bytearray(WIDTH * HEIGHT * 3)
for y in range(HEIGHT):
    for x in range(WIDTH):
        r = g = b = 0
        for sy in range(SS):
            row = ((y * SS + sy) * CANVAS_W + x * SS) * 3
            for sx in range(SS):
                i = row + sx * 3
                r += pixels[i]
                g += pixels[i+1]
                b += pixels[i+2]
        o = (y * WIDTH + x) * 3
        div = SS * SS
        small[o:o+3] = bytes((r // div, g // div, b // div))

def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)

raw = bytearray()
stride = WIDTH * 3
for y in range(HEIGHT):
    raw.append(0)
    raw.extend(small[y * stride:(y + 1) * stride])
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
OUT.write_bytes(png)

changed = 0
for path in ROOT.rglob('*.html'):
    if 'geosketch-mvp' in path.parts or path.name == '404.html':
        continue
    text = path.read_text(encoding='utf-8')
    if 'class="site-header"' not in text:
        continue
    updated = text.replace(OLD_IMAGE, NEW_IMAGE).replace(ICON_IMAGE, NEW_IMAGE)
    updated = re.sub(r'<meta property="og:image:width" content="\d+">', '<meta property="og:image:width" content="1200">', updated)
    updated = re.sub(r'<meta property="og:image:height" content="\d+">', '<meta property="og:image:height" content="1200">', updated)
    updated = updated.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary">')
    if updated != text:
        path.write_text(updated, encoding='utf-8')
        changed += 1

print(f'Generated {OUT.relative_to(ROOT)} and prepared square logo share metadata in {changed} HTML file(s).')
