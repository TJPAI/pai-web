from pathlib import Path
import base64
import hashlib

ROOT = Path('.tmp-home-assets')
ASSETS = {
    'ciie': (Path('assets/images/home/ciie-navigation.webp'), 43090, '75f1998d3f354c9abe533d7dbc35294a0fe48d5d12a5c42e4aa9d5be1d218162'),
    'mine': (Path('assets/images/home/datong-mine-magnetic-communication.webp'), 10094, '5055b8562740e4978907117e4d0e0f7b874b41796b4d890c7619c5a4da688fa6'),
    'microsoft': (Path('assets/images/home/microsoft-indoor-localization-competition.webp'), 24114, '3dbb0e511046e012d31ecbf143ca7aae5769b0ebccfb049b2f5907d7de32eb31'),
    'ieee': (Path('assets/images/home/ieee-president-visit.webp'), 9264, '15020a0af214f1cb34e0c524ff31c40860bf8d77b5b832459536f4d08fe71112'),
}

for prefix, (dst, expected_size, expected_sha) in ASSETS.items():
    parts = sorted(p for p in ROOT.glob(f'{prefix}.*') if p.suffix[1:].isdigit())
    if not parts:
        raise SystemExit(f'missing chunks for {prefix}')
    encoded = ''.join(p.read_text().strip() for p in parts)
    data = base64.b64decode(encoded, validate=True)
    actual_sha = hashlib.sha256(data).hexdigest()
    if len(data) != expected_size or actual_sha != expected_sha:
        raise SystemExit(f'{prefix} verification failed: size={len(data)} sha256={actual_sha}')
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)

replacements = {
    'https://alumni.tongji.edu.cn/_upload/article/images/fb/51/b84db8744a1bbde5e391c9c4f2ca/704165f6-fb67-4d2a-b952-f61cb2a2ea5a.png': 'ciie-navigation.webp',
    'https://news.tongji.edu.cn/_mediafile/tjnews/photos/images/2014/4/25/650/bdj4sjswou5jxkd.jpg': 'datong-mine-magnetic-communication.webp',
    'https://see.tongji.edu.cn/__local/9/93/3D/0B427C67959BBF2EB570EC25939_B112E241_781C3.png?e=.png': 'microsoft-indoor-localization-competition.webp',
    'https://news.tongji.edu.cn/__local/5/09/7C/9DF69DAA2AE2F9F656D71BAD4C7_46EED02F_A6634.png': 'ieee-president-visit.webp',
}

for html_path, prefix in [(Path('index.html'), 'assets/images/home/'), (Path('en/index.html'), '../assets/images/home/')]:
    text = html_path.read_text()
    for old, filename in replacements.items():
        count = text.count(old)
        if count != 1:
            raise SystemExit(f'{html_path}: expected exactly one occurrence of {old}, found {count}')
        text = text.replace(old, prefix + filename)
    html_path.write_text(text)

print('Homepage WebP assets reconstructed, verified, and localized.')
