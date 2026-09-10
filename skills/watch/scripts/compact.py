#!/usr/bin/env python3
"""OpenClaw-oriented optional contact-sheet adapter (MIT; upstream LICENSE retained)."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import time
from frames import extract_keyframes, extract_at_timestamps, get_metadata


def prepare(source, out, budget=8, width=240, *, columns=3, padding=12,
            max_height=None, quality=85, image_format="jpg", endpoint=True, dedup=True,
            sampler="keyframes", start=0.0, end=None):
    from PIL import Image, ImageDraw
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise ValueError('source must be an existing local video')
    out = Path(out).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('output directory must be empty; use a new directory')
    if not 2 <= budget <= 24 or not 160 <= width <= 640:
        raise ValueError('budget must be 2..24 and width 160..640')
    if not 1 <= columns <= 6 or not 0 <= padding <= 64 or not 1 <= quality <= 95:
        raise ValueError('columns 1..6, padding 0..64, quality 1..95 required')
    max_height = max_height if max_height is not None else 2*width
    if not 160 <= max_height <= 1280 or image_format not in ('jpg','png'):
        raise ValueError('max-height 160..1280 and format jpg/png required')
    if sampler not in ('keyframes','uniform') or not math.isfinite(start) or start < 0:
        raise ValueError('invalid sampler or start')
    info = get_metadata(str(source))
    duration = info['duration_seconds']
    end = duration if end is None else end
    if not math.isfinite(end) or not start < end <= duration:
        raise ValueError('require 0 <= start < end <= video duration')
    out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    if sampler == 'keyframes':
        items, meta = extract_keyframes(str(source), out / 'frames', resolution=width,
                    max_frames=budget-int(endpoint), start_seconds=start,
                    end_seconds=end, dedup=dedup)
    else:
        # Uniform locations are explicit coverage anchors; do not deduplicate them.
        n = budget-int(endpoint)
        ts = [start+(end-start)*i/n for i in range(n)]
        items, meta = extract_at_timestamps(str(source), out/'frames', ts,
                                            resolution=width, max_frames=n)
    if endpoint:
        last = out / 'end.jpg'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(max(start,end-1)),
                        '-to', str(end), '-i', str(source),
                        '-vf', f'reverse,scale={width}:-1', '-frames:v', '1', str(last)],
                       check=True, timeout=120)
        if not last.is_file():
            raise RuntimeError('could not decode final frame in selected range')
        items.append({'path': str(last), 'timestamp_seconds': None, 'reason': 'endpoint'})
    if not items:
        raise RuntimeError('no frames extracted')
    cols = min(columns, len(items))
    cell_h = max_height + 24 + 2*padding
    sheet = Image.new('RGB', (cols * (width + 2*padding), ((len(items)+cols-1)//cols)*cell_h), '#171717')
    draw = ImageDraw.Draw(sheet)
    records = []
    for i, item in enumerate(items):
        x = i % cols * (width+2*padding) + padding
        y = i // cols * cell_h + padding
        sec = item['timestamp_seconds']
        label = 'END' if sec is None else f'{sec:.2f}s'
        with Image.open(item['path']) as frame:
            frame.thumbnail((width, max_height))
            sheet.paste(frame, (x, y+24))
        draw.text((x, y), f'FRAME {i+1} | {label}', fill='white')
        records.append({'index': i+1, 'time_seconds': sec, 'label': label,
                        'file': str(Path(item['path']).relative_to(out))})
    sheet_name = 'sheet.'+image_format
    sheet.save(out / sheet_name, **({'quality':quality} if image_format=='jpg' else {}))
    prompt = ('Each numbered cell is a DIFFERENT TIME, not simultaneous people. '
              'Read left to right, top to bottom. Never merge adjacent cells into one scene. '
              'Describe visible actions, camera movement and the ending, citing frame numbers. '
              'Separate observation from inference; report uncertainty. Sparse frames do not prove motion speed.')
    (out / 'prompt.txt').write_text(prompt+'\n')
    result = {'duration_seconds': info['duration_seconds'], 'frames': records,
              'extractor': meta, 'sheet': sheet_name, 'options': {'sampler':sampler, 'max_frames':budget,
              'width':width,'max_height':max_height,'columns':columns,'padding':padding,
              'quality':quality if image_format=='jpg' else None,'format':image_format,
              'endpoint':endpoint,'dedup':dedup if sampler=='keyframes' else False,
              'start':start,'end':end}, 'seconds': time.perf_counter()-started,
              'audio_included': False, 'model_called': False}
    (out / 'manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='local video; no uploads or model calls')
    parser.add_argument('--out', required=True, help='new/empty output directory')
    parser.add_argument('--max-frames', type=int, default=8)
    parser.add_argument('--width', type=int, default=240)
    parser.add_argument('--columns', type=int, default=3)
    parser.add_argument('--padding', type=int, default=12)
    parser.add_argument('--max-height', type=int)
    parser.add_argument('--quality', type=int, default=85, help='JPEG quality; ignored for PNG')
    parser.add_argument('--format', choices=['jpg','png'], default='jpg')
    parser.add_argument('--sampler', choices=['keyframes','uniform'], default='keyframes')
    parser.add_argument('--start', type=float, default=0, help='range start in seconds')
    parser.add_argument('--end', type=float, help='exclusive range end in seconds')
    parser.add_argument('--no-endpoint', action='store_true')
    parser.add_argument('--no-dedup', action='store_true', help='keyframes only')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.source, args.out, args.max_frames, args.width,
              columns=args.columns,padding=args.padding,max_height=args.max_height,
              quality=args.quality,image_format=args.format,endpoint=not args.no_endpoint,
              dedup=not args.no_dedup,sampler=args.sampler,start=args.start,end=args.end), indent=2))
    except (ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'compact: {exc}\n')


if __name__ == '__main__':
    main()
