"""Add round 35's small pigment mark while preserving wall-v14 byte-for-byte elsewhere."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

spec = importlib.util.spec_from_file_location('png35', 'gathering/finish_wall.py')
png = importlib.util.module_from_spec(spec)
spec.loader.exec_module(png)

OLD = Path('artifacts/line-2/wall-v14.png')
NEW = Path('artifacts/line-2/wall-v15.png')
RECT = (1040, 890, 145, 135)


def blend(pixels, width, x, y, color, alpha):
    if not (0 <= x < width and 0 <= y < width):
        return
    pos = (y * width + x) * 3
    for c in range(3):
        pixels[pos + c] = round(pixels[pos + c] * (1 - alpha) + color[c] * alpha)


def stroke(pixels, width, start, end, radius, color, alpha):
    x0, y0 = start
    x1, y1 = end
    distance = max(abs(x1 - x0), abs(y1 - y0))
    for step in range(distance + 1):
        t = step / max(1, distance)
        cx = round(x0 + (x1 - x0) * t)
        cy = round(y0 + (y1 - y0) * t)
        wobble = ((step * 17 + x0 * 3 + y0) % 7) - 3
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    blend(pixels, width, cx + dx + (wobble if dy == 0 else 0), cy + dy,
                          color, alpha * (0.75 + ((step + dx + dy) % 3) * 0.08))


def main():
    ancestor = hashlib.sha256(OLD.read_bytes()).hexdigest()
    assert ancestor == '4105098ab30a8ea1f9c662d4620dc1f103876f35d97873536699c8be33078a4a'
    width, height, original = png.read_png(OLD)
    assert (width, height) == (1254, 1254)
    final = original[:]

    # A three-part ochre bundle converges on a chalk point: a visual shorthand
    # for several proven fields collected into one receipt.
    chalk = (207, 193, 161)
    ochre = (155, 57, 27)
    charcoal = (48, 33, 24)
    center = (1132, 958)
    for end in ((1070, 925), (1070, 962), (1080, 1001)):
        stroke(final, width, end, center, 4, ochre, 0.78)
        stroke(final, (width), (end[0] + 3, end[1] + 1), (center[0] - 4, center[1]), 1, charcoal, 0.55)
    # Irregular chalk center, deliberately small and pigment-like.
    for dy in range(-8, 9):
        for dx in range(-8, 9):
            if dx * dx + dy * dy <= 65 and (dx * 5 + dy * 3) % 4:
                blend(final, width, center[0] + dx, center[1] + dy, chalk, 0.72)

    changed = outside = 0
    for i in range(width * height):
        if final[3 * i:3 * i + 3] != original[3 * i:3 * i + 3]:
            changed += 1
            x, y = i % width, i // width
            outside += not (RECT[0] <= x < RECT[0] + RECT[2] and RECT[1] <= y < RECT[1] + RECT[3])
    assert changed > 1000 and outside == 0
    digest = png.write_png(NEW, width, height, final)

    continuation = Path('artifacts/line-2/wall.png')
    if continuation.is_symlink() or continuation.exists():
        continuation.unlink()
    continuation.symlink_to('wall-v15.png')

    rgba = bytearray()
    for y in range(512):
        ya, yb = y * height // 512, (y + 1) * height // 512
        for x in range(512):
            xa, xb = x * width // 512, (x + 1) * width // 512
            count = (yb - ya) * (xb - xa)
            for c in range(3):
                rgba.append(round(sum(final[(sy * width + sx) * 3 + c]
                                      for sy in range(ya, yb) for sx in range(xa, xb)) / count))
            rgba.append(255)
    js = """
const fs = require('fs');
const encode = require('./line-3/tools/corpus-change-receipt/vendor/jpeg-js/lib/encoder.js');
const result = encode({data:fs.readFileSync(0),width:512,height:512},78);
if (result.data.length > 100000) throw Error('JPEG too large');
fs.writeFileSync('dist/line-2/35.jpg', result.data);
"""
    subprocess.run(['node', '-e', js], input=rgba, check=True)

    images = []
    for path, kind, dimensions in ((NEW, 'PNG', [width, height]),
                                   (continuation, 'PNG', [width, height]),
                                   (Path('dist/line-2/35.jpg'), 'JPEG', [512, 512])):
        data = path.read_bytes()
        images.append({'path': str(path), 'format': kind, 'dimensions': dimensions,
                       'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    review = {
        'round': 35, 'ancestorSha256': ancestor, 'wallSha256': digest,
        'dimensions': [width, height], 'format': 'PNG', 'channels': 'RGB',
        'newMarkRectangle': list(RECT), 'changedPixels': changed,
        'changedPixelsOutsideRectangle': outside,
        'method': 'Installed image edit was inspected; final pigment was isolated to the declared unused-rock rectangle and composited over wall-v14.',
        'visualReview': 'Pepe retains heavy-lidded eyes, broad mouth, and two five-digit hands; warm rough rock, cracks, crystals, framing and ancestral marks remain. New mark is three worn ochre strokes converging on a chalk dot. No letters, numbers, captions, signatures, logos, watermarks, borders, real people or forbidden symbols observed.',
        'unmetVisualRequirements': [], 'images': images,
    }
    Path('line-2/REVIEW-35.json').write_text(json.dumps(review, indent=2) + '\n')
    record = {
        'name': 'The Gathered Proof',
        'image': 'https://api.imd.fun/artifacts/' + digest,
        'attributes': [
            {'trait_type': 'Cave', 'value': 'Crystal'},
            {'trait_type': 'Wall', 'value': 'Line 2'},
            {'trait_type': 'Number', 'value': 35},
            {'trait_type': 'Left behind', 'value': 'Proof Receipt'},
            {'trait_type': 'Meaning', 'value': 'Three ochre strokes gather proven parts around one checkable center.'},
            {'trait_type': 'One thing', 'value': 'Verify Ethereum account and storage proofs against trusted state roots'},
        ],
    }
    assert not Path('dist/line-2/35.json').exists()
    Path('dist/line-2/35.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    main()
