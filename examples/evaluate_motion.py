#!/usr/bin/env python3
"""Reproducible image-plane motion evaluation; no network, models or third-party media."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/watch/scripts'))
from evidence import motion_pair


def evaluate():
    import cv2
    import numpy as np
    cv2.setNumThreads(1)
    cv2.setRNGSeed(0)
    rng = np.random.default_rng(12)
    first = cv2.GaussianBlur(rng.integers(0, 256, (240, 320, 3), dtype=np.uint8), (3, 3), 0)
    rows = []
    for dx, dy in [(7, -3), (-9, 4), (0, 0)]:
        second = cv2.warpAffine(first, np.float32([[1, 0, dx], [0, 1, dy]]), (320, 240))
        result = motion_pair(first, second)
        error = float(np.linalg.norm(np.array(result['image_displacement_xy']) * [320, 240] - [dx, dy]))
        rows.append({'case': f'translation_{dx}_{dy}', 'truth_pixels': [dx, dy],
                     'result': result, 'error_pixels': round(error, 4),
                     'passed': error < .5 and result['status'] == ('moved' if dx or dy else 'stable')})
    second = cv2.warpAffine(first, cv2.getRotationMatrix2D((160, 120), 2, 1), (320, 240))
    result = motion_pair(first, second)
    rows.append({'case': 'rotation_2_degrees', 'result': result,
                 'passed': result['status'] == 'moved' and abs(abs(result['rotation_degrees'])-2) < .2})
    a, b = first.copy(), first.copy()
    cv2.rectangle(a, (25, 130), (100, 220), (0, 0, 255), -1)
    cv2.rectangle(b, (150, 130), (225, 220), (0, 0, 255), -1)
    result = motion_pair(a, b, (0, 0, 1, .45))
    rows.append({'case': 'static_background_moving_foreground', 'result': result,
                 'passed': result['status'] == 'stable'})
    blank = np.zeros_like(first)
    unrelated = cv2.GaussianBlur(np.random.default_rng(937).integers(0, 256, first.shape, dtype=np.uint8), (3, 3), 0)
    for name, a, b in [('untextured', blank, blank), ('unrelated_frames', first, unrelated)]:
        result = motion_pair(a, b)
        rows.append({'case': name, 'result': result, 'passed': result['status'] == 'unknown'})
    return {'opencv': cv2.__version__, 'numpy': np.__version__, 'cases': rows,
            'all_passed': all(row['passed'] for row in rows),
            'scope': 'Synthetic planar transforms only; not camera extrinsics or gait accuracy.'}


if __name__ == '__main__':
    report = evaluate()
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['all_passed'] else 1)
