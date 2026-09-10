#!/usr/bin/env python3
"""Create an original, known-geometry fixture; provide a locally licensed TrueType font."""
import argparse
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', required=True, help='local bold sans-serif TrueType font')
    parser.add_argument('--out', required=True, help='fresh/empty directory')
    args = parser.parse_args()
    font = ImageFont.truetype(args.font, 32)
    out = Path(args.out).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('output directory must be empty')
    out.mkdir(parents=True, exist_ok=True)
    expected = []
    for index, x in enumerate((30, 100, 170)):
        frame = Image.new('RGB', (360, 640), '#183044')
        draw = ImageDraw.Draw(frame)
        draw.rectangle((x, 200, x + 80, 300), fill='red')
        draw.text((43, 493), 'HELLO SHORTS', font=font, fill='black',
                  stroke_width=3, stroke_fill='black')
        draw.text((40, 490), 'HELLO SHORTS', font=font, fill='white',
                  stroke_width=1, stroke_fill='black')
        frame.save(out / f'{index:02}.png')
        expected.append({'index': index + 1, 'time_seconds': index,
                         'rectangle_bbox': [x/360, 200/640, (x+81)/360, 301/640],
                         'visible_text': 'HELLO SHORTS'})
    subprocess.run(['ffmpeg', '-v', 'error', '-framerate', '1', '-i', str(out / '%02d.png'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(out / 'video.mp4')],
                   check=True, timeout=60)
    ground_truth = {'frames': expected, 'motion': 'rightward discrete position changes',
                    'text_fill': 'white', 'foreground_stroke_px': 1,
                    'shadow_offset_px': [3, 3], 'shadow_stroke_px': 3,
                    'source_font_filename': Path(args.font).name,
                    'note': 'Editor/source truth; not fields the VLM is expected to recover exactly.'}
    (out / 'expected.json').write_text(json.dumps(ground_truth, indent=2))
    print(json.dumps({'video': str(out / 'video.mp4'), 'expected': str(out / 'expected.json')}))


if __name__ == '__main__':
    main()
