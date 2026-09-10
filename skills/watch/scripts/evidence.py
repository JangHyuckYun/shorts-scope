"""Local motion, OCR/crop and optional pose evidence for ShortsScope (no LLM calls)."""
import argparse
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import time

from shorts import load_manifest


def roi_arg(value):
    values = tuple(float(x) for x in value.split(','))
    if (len(values) != 4 or not all(math.isfinite(x) and 0 <= x <= 1 for x in values)
            or values[0] >= values[2] or values[1] >= values[3]):
        raise argparse.ArgumentTypeError('ROI is normalized left,top,right,bottom in 0..1')
    return values


def fingerprint(manifest):
    _, _, paths, timeline = load_manifest(manifest)
    payload = [(item, hashlib.sha256(path.read_bytes()).hexdigest())
               for item, path in zip(timeline, paths)]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def motion_pair(first, second, roi=(0, 0, 1, 1)):
    import cv2
    import numpy as np
    if first.shape != second.shape:
        return {'status': 'unknown', 'reason': 'different image dimensions'}
    height, width = first.shape[:2]
    gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    other = cv2.cvtColor(second, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(gray)
    left, top, right, bottom = [round(v * size) for v, size in zip(roi, (width, height, width, height))]
    mask[top:bottom, left:right] = 255
    points = cv2.goodFeaturesToTrack(gray, maxCorners=400, qualityLevel=.015,
                                    minDistance=7, mask=mask)
    if points is None or len(points) < 12:
        return {'status': 'unknown', 'reason': 'insufficient textured features'}
    tracked, status, _ = cv2.calcOpticalFlowPyrLK(gray, other, points, None,
                                                winSize=(21, 21), maxLevel=3)
    if tracked is None:
        return {'status': 'unknown', 'reason': 'tracking failed'}
    back, back_status, _ = cv2.calcOpticalFlowPyrLK(other, gray, tracked, None,
                                                   winSize=(21, 21), maxLevel=3)
    if back is None:
        return {'status': 'unknown', 'reason': 'backward tracking failed'}
    good = (status.ravel() == 1) & (back_status.ravel() == 1)
    good &= np.linalg.norm((back - points).reshape(-1, 2), axis=1) < 1.5
    old, new = points.reshape(-1, 2)[good], tracked.reshape(-1, 2)[good]
    if len(old) < 12:
        return {'status': 'unknown', 'reason': 'too few consistent tracks'}
    matrix, inliers = cv2.estimateAffinePartial2D(old, new, method=cv2.RANSAC,
                                                ransacReprojThreshold=2, maxIters=1000)
    if matrix is None:
        return {'status': 'unknown', 'reason': 'no coherent image transform'}
    keep = inliers.ravel().astype(bool)
    ratio = float(keep.mean())
    # Require support over multiple spatial cells, not a tiny moving foreground patch.
    cells = {(min(3, int(x / width * 4)), min(3, int(y / height * 4))) for x, y in old[keep]}
    if ratio < .6 or int(keep.sum()) < 12 or len(cells) < 3:
        return {'status': 'unknown', 'reason': 'weak or spatially concentrated consensus',
                'inlier_ratio': round(ratio, 3)}
    center = np.array([width / 2, height / 2, 1.0])
    shift = matrix @ center - center[:2]
    angle = math.degrees(math.atan2(matrix[1, 0], matrix[0, 0]))
    scale = math.hypot(matrix[0, 0], matrix[1, 0])
    displacement = [float(shift[0] / width), float(shift[1] / height)]
    moved = (math.hypot(*displacement) > .004 or abs(angle) > .25 or abs(scale - 1) > .005)
    residual = np.linalg.norm(old @ matrix[:, :2].T + matrix[:, 2] - new, axis=1)
    return {'status': 'moved' if moved else 'stable',
            'image_displacement_xy': [round(x, 5) for x in displacement],
            'rotation_degrees': round(angle, 3), 'scale': round(scale, 5),
            'inlier_ratio': round(ratio, 3), 'tracks': int(keep.sum()),
            'median_residual_pixels': round(float(np.median(residual[keep])), 3)}


def font_candidates(crop, text, fonts):
    """Rank only supplied font files by normalized glyph-shape overlap; never identify exactly."""
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    border = np.concatenate((gray[0], gray[-1], gray[:, 0], gray[:, -1]))
    mode = cv2.THRESH_BINARY if np.median(border) < 128 else cv2.THRESH_BINARY_INV
    _, ink = cv2.threshold(gray, 0, 255, mode | cv2.THRESH_OTSU)

    def normalize(mask):
        ys, xs = np.where(mask > 0)
        if len(xs) < 3: return None
        return cv2.resize(mask[ys.min():ys.max()+1, xs.min():xs.max()+1],
                          (256, 64), interpolation=cv2.INTER_NEAREST) > 0

    observed = normalize(ink)
    if observed is None: return []
    ranked = []
    for file in fonts:
        font = ImageFont.truetype(str(file), 64)
        box = font.getbbox(text)
        canvas = Image.new('L', (max(1, box[2]-box[0]+4), max(1, box[3]-box[1]+4)))
        ImageDraw.Draw(canvas).text((2-box[0], 2-box[1]), text, font=font, fill=255)
        candidate = normalize(np.array(canvas))
        if candidate is None: continue
        score = float((candidate & observed).sum() / (candidate | observed).sum())
        ranked.append({'font_file': Path(file).name, 'shape_overlap': round(score, 4)})
    return sorted(ranked, key=lambda item: item['shape_overlap'], reverse=True)[:3]


def ocr_frame(image, out, index, executable, lang, psm, roi, min_confidence, fonts):
    import cv2
    from PIL import Image
    height, width = image.shape[:2]
    l, t, r, b = [round(v*size) for v, size in zip(roi, (width, height, width, height))]
    area = image[t:b, l:r]
    if not area.size: raise ValueError('empty OCR region')
    with tempfile.TemporaryDirectory(prefix='shorts-ocr-') as temp:
        png = Path(temp) / 'input.png'
        cv2.imwrite(str(png), cv2.resize(area, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC))
        proc = subprocess.run([executable, str(png), 'stdout', '-l', lang,
                               '--psm', str(psm), 'tsv'], capture_output=True, text=True, timeout=30,
                              env={**os.environ, 'OMP_THREAD_LIMIT': os.environ.get('OMP_THREAD_LIMIT', '1')})
        if proc.returncode:
            raise RuntimeError('Tesseract failed: ' + proc.stderr[-600:])
    lines = {}
    for word in csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'):
        text = (word.get('text') or '').strip()
        confidence = float(word['conf'])
        if not text or confidence < min_confidence: continue
        x, y = l + int(word['left'])/2, t + int(word['top'])/2
        w, h = int(word['width'])/2, int(word['height'])/2
        key = (word['block_num'], word['par_num'], word['line_num'])
        lines.setdefault(key, []).append((text, confidence, x, y, x+w, y+h))
    results = []
    for words in list(lines.values())[:32]:
        text = ' '.join(w[0] for w in words)
        x1, y1 = min(w[2] for w in words), min(w[3] for w in words)
        x2, y2 = max(w[4] for w in words), max(w[5] for w in words)
        a, c, d, e = max(0, int(x1)-5), max(0, int(y1)-5), min(width, math.ceil(x2)+5), min(height, math.ceil(y2)+5)
        crop = image[c:e, a:d]
        name = f'text-{index}-{len(results)+1}.png'
        cv2.imwrite(str(out / name), crop)
        rgb = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
        quantized = rgb.quantize(colors=5).convert('RGB')
        palette = sorted(quantized.getcolors(crop.shape[0]*crop.shape[1]), reverse=True)
        results.append({'text': text, 'engine_confidence': round(sum(w[1] for w in words)/len(words), 2),
                        'bbox': [round(x1/width, 5), round(y1/height, 5), round(x2/width, 5), round(y2/height, 5)],
                        'crop': name, 'palette_hex': ['#%02x%02x%02x' % color for _, color in palette],
                        'font_candidates': font_candidates(crop, text, fonts) if fonts else []})
    return results


def pose_frames(paths, model):
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    names = {23: 'left_hip', 24: 'right_hip', 25: 'left_knee', 26: 'right_knee',
             27: 'left_ankle', 28: 'right_ankle', 29: 'left_heel', 30: 'right_heel',
             31: 'left_toe', 32: 'right_toe'}
    options = vision.PoseLandmarkerOptions(base_options=python.BaseOptions(model_asset_path=str(model)),
                                           num_poses=1)
    output = []
    with vision.PoseLandmarker.create_from_options(options) as detector:
        for path in paths:
            detected = detector.detect(mp.Image.create_from_file(str(path)))
            points = []
            if detected.pose_landmarks:
                for number, name in names.items():
                    point = detected.pose_landmarks[0][number]
                    visible = (0 <= point.x <= 1 and 0 <= point.y <= 1
                               and point.visibility >= .6 and point.presence >= .6)
                    points.append({'joint': name, 'xy': [round(point.x, 4), round(point.y, 4)],
                                   'usable': bool(visible), 'visibility': round(point.visibility, 3)})
            usable_feet = sum(p['usable'] for p in points if any(k in p['joint'] for k in ('ankle', 'heel', 'toe')))
            output.append({'landmarks': points, 'feet_sufficiently_visible': usable_feet >= 4,
                           'gait_class': 'unknown',
                           'reason': 'pose availability is not a walking/running classifier'})
    return output


def measure(manifest, out, motion_roi=(0, 0, 1, 1), ocr=False, tesseract='tesseract',
            lang='eng', psm=11, text_roi=(0, 0, 1, 1), min_confidence=60, fonts=(), pose_model=None):
    import cv2
    started = time.perf_counter()
    m, ids, paths, timeline = load_manifest(manifest)
    for roi in (motion_roi, text_roi): roi_arg(','.join(map(str, roi)))
    if not 0 <= min_confidence <= 100 or psm not in range(3, 14) or len(fonts) > 16:
        raise ValueError('confidence 0..100, PSM 3..13 and at most16 font candidates required')
    out = Path(out).expanduser().resolve()
    if out.exists() and any(out.iterdir()): raise ValueError('output directory must be empty')
    images = [cv2.imread(str(path)) for path in paths]
    if any(image is None for image in images): raise ValueError('unreadable input image')
    out.mkdir(parents=True, exist_ok=True)
    cv2.setNumThreads(1)
    cv2.setRNGSeed(0)
    pairs = []
    for i in range(1, len(images)):
        pair = motion_pair(images[i-1], images[i], motion_roi)
        pairs.append({'from_frame': ids[i-1], 'to_frame': ids[i], **pair})
    poses = pose_frames(paths, pose_model) if pose_model else [None]*len(images)
    frames = []
    for index, image, pose in zip(ids, images, poses):
        texts = ocr_frame(image, out, index, tesseract, lang, psm, text_roi, min_confidence, fonts) if ocr else []
        frames.append({'frame_index': index, 'ocr_enabled': ocr, 'text_regions': texts, 'pose': pose})
    result = {'version': 'shorts-evidence/1', 'manifest_fingerprint': fingerprint(manifest),
              'timeline': timeline, 'motion_roi': list(motion_roi), 'motion_pairs': pairs,
              'frames': frames, 'seconds': time.perf_counter()-started,
              'method': {'motion': 'forward/backward LK tracks + RANSAC affine in caller ROI',
                         'ocr': 'Tesseract TSV + local crops' if ocr else None,
                         'pose_model_sha256': hashlib.sha256(Path(pose_model).read_bytes()).hexdigest() if pose_model else None},
              'limitations': ['ROI displacement is image-plane motion, not measured camera extrinsics; foreground/cuts/parallax may invalidate it.',
                              'OCR can be wrong; palette colors are not automatically foreground/outline/shadow labels.',
                              'Font candidates are nearest supplied shapes, never exact identity.',
                              'Missing feet do not imply walking; pose visibility does not classify gait.']}
    (out / 'evidence.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'status': 'measured', 'evidence': str(out/'evidence.json'), 'seconds': result['seconds'], 'model_called': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest'); parser.add_argument('--out', required=True)
    parser.add_argument('--motion-roi', type=roi_arg, default=(0, 0, 1, 1))
    parser.add_argument('--ocr', action='store_true'); parser.add_argument('--tesseract', default='tesseract')
    parser.add_argument('--ocr-lang', default='eng'); parser.add_argument('--ocr-psm', type=int, default=11)
    parser.add_argument('--text-roi', type=roi_arg, default=(0, 0, 1, 1))
    parser.add_argument('--min-confidence', type=float, default=60)
    parser.add_argument('--font', action='append', default=[], help='local candidate font file; repeat up to16')
    parser.add_argument('--pose-model', help='local MediaPipe Pose Landmarker .task; optional')
    args = parser.parse_args()
    try:
        print(json.dumps(measure(args.manifest, args.out, args.motion_roi, args.ocr, args.tesseract,
                                 args.ocr_lang, args.ocr_psm, args.text_roi, args.min_confidence,
                                 args.font, args.pose_model)))
    except (ValueError, OSError, RuntimeError, ImportError, subprocess.SubprocessError) as exc:
        parser.exit(1, f'measure: {exc}\n')


if __name__ == '__main__': main()
