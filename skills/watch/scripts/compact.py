#!/usr/bin/env python3
"""OpenClaw-oriented optional contact-sheet adapter (MIT; upstream LICENSE retained)."""
import argparse
import json
from pathlib import Path
import subprocess
import time
from frames import extract_keyframes, get_metadata


def prepare(source, out, budget=8, width=240):
    from PIL import Image, ImageDraw
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ValueError('source must be an existing local video')
    out = Path(out).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('output directory must be empty; use a new directory')
    if not 2 <= budget <= 12 or not 160 <= width <= 640:
        raise ValueError('budget must be 2..12 and width 160..640')
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    info = get_metadata(str(source))
    items, meta = extract_keyframes(str(source), out / 'frames', resolution=width,
                                    max_frames=budget - 1)
    # Decode only the final second, reverse it, and retain the last decoded frame.
    # END is not an exact PTS: this also works with variable-frame-rate inputs.
    endpoint = out / 'end.jpg'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-1', '-i', str(source),
                    '-vf', f'reverse,scale={width}:-1', '-frames:v', '1', str(endpoint)],
                   check=True, timeout=120)
    if not endpoint.is_file():
        raise RuntimeError('could not decode final video frame')
    items.append({'path': str(endpoint), 'timestamp_seconds': None, 'reason': 'endpoint'})
    cols = min(3, len(items))
    cell_h = 2 * width + 44
    sheet = Image.new('RGB', (cols * (width + 24), ((len(items)+cols-1)//cols)*cell_h), '#171717')
    draw = ImageDraw.Draw(sheet)
    records = []
    for i, item in enumerate(items):
        x = i % cols * (width+24) + 12
        y = i // cols * cell_h + 10
        sec = item['timestamp_seconds']
        label = 'END' if sec is None else f'{sec:.2f}s'
        with Image.open(item['path']) as frame:
            frame.thumbnail((width, 2*width))
            sheet.paste(frame, (x, y+24))
        draw.text((x, y), f'FRAME {i+1} | {label}', fill='white')
        records.append({'index': i+1, 'time_seconds': sec, 'label': label,
                        'file': str(Path(item['path']).relative_to(out))})
    sheet.save(out / 'sheet.jpg')
    prompt = ('Each numbered cell is a DIFFERENT TIME, not simultaneous people. '
              'Read left to right, top to bottom. Never merge adjacent cells into one scene. '
              'Describe visible actions, camera movement and the ending, citing frame numbers. '
              'Separate observation from inference; report uncertainty. Sparse frames do not prove motion speed.')
    (out / 'prompt.txt').write_text(prompt+'\n')
    result = {'duration_seconds': info['duration_seconds'], 'frames': records,
              'extractor': meta, 'sheet': 'sheet.jpg', 'seconds': time.perf_counter()-started,
              'audio_included': False, 'model_called': False}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='local video; no uploads or model calls')
    parser.add_argument('--out', required=True, help='new/empty output directory')
    parser.add_argument('--max-frames', type=int, default=8)
    parser.add_argument('--width', type=int, default=240)
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.source, args.out, args.max_frames, args.width), indent=2))
    except (ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'compact: {exc}\n')


if __name__ == '__main__':
    main()
