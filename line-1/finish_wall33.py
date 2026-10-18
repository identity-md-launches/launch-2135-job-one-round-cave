"""Flatten the generated motif onto ancestor rock; never repaint inherited pixels.

One-time finishing operation, expecting imagegen pigment at wall-v15.png.
The source motif is consumed, not delivered as another image.
"""
import hashlib
import json
from pathlib import Path
import subprocess
from finish_wall24 import read_png, write_png


def main():
    ancestor = Path('artifacts/line-1/wall-v14.png').read_bytes()
    ancestor_sha = hashlib.sha256(ancestor).hexdigest()
    assert ancestor_sha == '4d1da8e0f9b36c75f25cf3f95f63e4a19e7e1f8d37cbd314b4b48abb66e7059f'
    output = Path('artifacts/line-1/wall-v15.png')
    motif_sha = hashlib.sha256(output.read_bytes()).hexdigest()
    width, height, original = read_png(ancestor)
    mw, mh, motif = read_png(output)
    assert (mw, mh) in ((1774, 887), (1254, 1254))
    final = original[:]
    x0, y0, rw, rh = 900, 235, 220, 75
    # Crop empty black margins in memory. Add pigment only, never its background.
    sx0, sy0, sw, sh = 130, 250, 1500, 340
    for y in range(rh if (mw, mh) == (1774, 887) else 0):
        for x in range(rw):
            sx, sy = sx0 + int(x * sw / rw), sy0 + int(y * sh / rh)
            color = motif[(sy * mw + sx) * 3:(sy * mw + sx) * 3 + 3]
            strength = max(color)
            if strength < 40:
                continue
            alpha = min(.80, (strength - 40) / 160)
            alpha *= min(1, x / 4, y / 4, (rw - 1 - x) / 4, (rh - 1 - y) / 4)
            i = ((y0 + y) * width + x0 + x) * 3
            for c in range(3):
                final[i + c] = round(original[i + c] * (1 - alpha) + color[c] * alpha)
    if (mw, mh) == (width, height):
        # Resume a previously composed wall after an encoding interruption.
        final = motif
        motif_sha = None
    changed = outside = 0
    for pixel in range(width * height):
        if original[pixel * 3:pixel * 3 + 3] != final[pixel * 3:pixel * 3 + 3]:
            changed += 1
            x, y = pixel % width, pixel // width
            outside += not (x0 <= x < x0 + rw and y0 <= y < y0 + rh)
    assert changed > 0 and outside == 0
    assert len(list(Path('dist/line-1').glob('*.json'))) == 32
    assert not Path('dist/line-1/33.json').exists()
    digest = write_png(output, width, height, final)
    assert read_png(output)[2] == final
    Path('artifacts/line-1/wall.png').write_bytes(output.read_bytes())
    jpeg = Path('dist/line-1/33.jpg')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-i', str(output), '-vf', 'scale=512:512', '-frames:v', '1',
                    '-q:v', '4', str(jpeg)], check=True)
    assert jpeg.stat().st_size < 100000
    evidence = {
        'ancestor_sha256': ancestor_sha, 'generated_motif_sha256': motif_sha,
        'wall': str(output), 'continued_wall': 'artifacts/line-1/wall.png',
        'sha256': digest, 'dimensions': [width, height], 'format': 'PNG', 'mode': 'RGB',
        'thumbnail': {'path': str(jpeg), 'dimensions': [512, 512], 'format': 'JPEG',
                      'bytes': jpeg.stat().st_size,
                      'sha256': hashlib.sha256(jpeg.read_bytes()).hexdigest()},
        'mark_rectangle': [x0, y0, rw, rh], 'changed_pixels': changed,
        'changed_pixels_outside_rectangle': outside,
        'method': 'Installed imagegen generated pigment; flattened pigment only onto unchanged ancestor.',
        'visual_review': 'Pending full wall and thumbnail inspection.',
        'unmet_visual_requirements': [],
        'location_conflict': 'Followed explicit dist/line-1/33.jpg requirement over general no-pictures-outside-artifacts sentence.'}
    Path('line-1/IMAGE-33.json').write_text(json.dumps(evidence, indent=2) + '\n')
    record = {'name': 'The watched absence',
              'image': 'https://api.imd.fun/artifacts/' + digest,
              'attributes': [
                  {'trait_type': 'Cave', 'value': 'Crystal'},
                  {'trait_type': 'Wall', 'value': 'Line 1'},
                  {'trait_type': 'Number', 'value': 33},
                  {'trait_type': 'Left behind', 'value': 'Deletion Audit'},
                  {'trait_type': 'Meaning', 'value': 'A chalk eye watches a gap so removed words do not silently return.'},
                  {'trait_type': 'One thing', 'value': 'Reviewable three-way text merging'}]}
    Path('dist/line-1/33.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
