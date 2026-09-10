"""Numerical motion ground truth and offline evidence/installation boundaries."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

needs_cv = pytest.mark.skipif(importlib.util.find_spec('cv2') is None, reason='optional CV dependencies')

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / 'skills/watch/scripts'))
from shorts import analyze
from evidence import fingerprint, measure, motion_pair


def texture(seed=12):
    cv2 = pytest.importorskip('cv2')
    np = pytest.importorskip('numpy')
    rng = np.random.default_rng(seed)
    return cv2.GaussianBlur(rng.integers(0, 256, (240, 320, 3), dtype=np.uint8), (3, 3), 0)


@pytest.mark.parametrize('dx,dy', [(7, -3), (-9, 4), (0, 0)])
@needs_cv
def test_known_translation(dx, dy):
    import cv2
    import numpy as np
    first = texture()
    second = cv2.warpAffine(first, np.float32([[1, 0, dx], [0, 1, dy]]), (320, 240))
    result = motion_pair(first, second)
    assert result['status'] == ('moved' if dx or dy else 'stable')
    actual = np.array(result['image_displacement_xy']) * [320, 240]
    assert np.linalg.norm(actual - [dx, dy]) < .5


@needs_cv
def test_stationary_background_with_moving_foreground():
    import cv2
    first = texture()
    second = first.copy()
    cv2.rectangle(first, (25, 130), (100, 220), (0, 0, 255), -1)
    cv2.rectangle(second, (150, 130), (225, 220), (0, 0, 255), -1)
    assert motion_pair(first, second, (0, 0, 1, .45))['status'] == 'stable'


@needs_cv
def test_rotation_and_unobservable_motion():
    import cv2
    import numpy as np
    first = texture()
    second = cv2.warpAffine(first, cv2.getRotationMatrix2D((160, 120), 2, 1), (320, 240))
    result = motion_pair(first, second)
    assert result['status'] == 'moved'
    assert abs(abs(result['rotation_degrees']) - 2) < .2
    blank = np.zeros_like(first)
    assert motion_pair(blank, blank)['status'] == 'unknown'
    assert motion_pair(first, texture(937))['status'] == 'unknown'


@pytest.fixture
def bundle(tmp_path):
    from PIL import Image
    frames = []
    for i in range(1, 4):
        Image.new('RGB', (320, 240), (i * 20, 0, 0)).save(tmp_path / f'{i}.png')
        frames.append({'index': i, 'time_seconds': (i-1)*.1, 'label': f'{i}', 'file': f'{i}.png'})
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'duration_seconds': 1, 'frames': frames}))
    return manifest


def test_evidence_selected_order_content_binding_and_crop_boundary(bundle, tmp_path):
    pytest.importorskip('cv2')
    out = tmp_path / 'measure'
    result = measure(bundle, out)
    assert result['model_called'] is False
    evidence = out / 'evidence.json'
    measured = json.loads(evidence.read_text())
    # Deliberately unsorted caller IDs must still yield chronological images.
    analyze(bundle, tmp_path / 'request', evidence=evidence, select_frames=[3, 1])
    request = json.loads((tmp_path / 'request/request.json').read_text())
    assert [x['index'] for x in request['timeline']] == [1, 3]
    assert not request['detail_images']
    with pytest.raises(ValueError, match='unique IDs'):
        analyze(bundle, tmp_path / 'bad-selection', select_frames=[1, 1])
    measured['frames'][0]['text_regions'] = [{'text': 'X', 'engine_confidence': 80,
        'bbox': [0, 0, .1, .1], 'palette_hex': [], 'font_candidates': [], 'crop': '../1.png'}]
    evidence.write_text(json.dumps(measured))
    with pytest.raises(ValueError, match='outside'):
        analyze(bundle, tmp_path / 'bad-crop', evidence=evidence)
    # Same manifest text with replaced pixels must not reuse stale measurements.
    old = fingerprint(bundle)
    (tmp_path / '1.png').write_bytes(b'replaced')
    assert fingerprint(bundle) != old
    with pytest.raises(ValueError, match='does not match'):
        analyze(bundle, tmp_path / 'stale', evidence=evidence)


@needs_cv
def test_ocr_coordinates_use_roi_and_scale(tmp_path, monkeypatch):
    import numpy as np
    from types import SimpleNamespace
    from evidence import ocr_frame
    tsv = 'level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n5\t1\t1\t1\t1\t1\t20\t10\t60\t20\t92\tTEST\n'
    monkeypatch.setattr('evidence.subprocess.run', lambda *a, **k: SimpleNamespace(returncode=0, stdout=tsv))
    image = np.zeros((200, 100, 3), dtype=np.uint8)
    result = ocr_frame(image, tmp_path, 1, 'tesseract', 'eng', 11, (.2, .5, .9, .9), 60, [])
    assert result[0]['bbox'] == pytest.approx([.3, .525, .6, .575])
    assert (tmp_path / result[0]['crop']).is_file()


spec = importlib.util.spec_from_file_location('install_skill', ROOT / 'scripts/install_skill.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


@pytest.mark.parametrize('host,relative', [('codex', '.agents/skills/shorts-scope'),
                                        ('claude', '.claude/skills/shorts-scope'),
                                        ('openclaw', 'workspace/skills/shorts-scope')])
def test_host_install_isolated_and_idempotent(tmp_path, host, relative):
    kwargs = dict(host=host, home=tmp_path, python=sys.executable)
    if host == 'openclaw': kwargs['workspace'] = tmp_path / 'workspace'
    result = installer.install(**kwargs, dry_run=True)
    target = tmp_path / relative
    assert Path(result['target']) == target
    assert not target.exists()
    result = installer.install(**kwargs)
    assert result['launcher_verified'] and not result['runtime_discovery_verified']
    assert installer.install(**kwargs)['status'] == 'already-installed'
    (target / 'SKILL.md').write_text('user content')
    with pytest.raises(ValueError, match='preserved'):
        installer.install(**kwargs)
    assert (target / 'SKILL.md').read_text() == 'user content'


def test_host_registry_must_be_known(tmp_path):
    with pytest.raises(ValueError, match='actual active'):
        installer.destination('openclaw', 'user', tmp_path)
    with pytest.raises(ValueError, match='verified'):
        installer.destination('generic', 'user', tmp_path)
    project = installer.destination('codex', 'project', tmp_path, tmp_path/'project')
    assert project == tmp_path/'project/.agents/skills/shorts-scope'


def test_bundle_runner_matches_reviewable_source():
    import zipfile
    with zipfile.ZipFile(ROOT/'assets/shorts-scope.skill.zip') as archive:
        assert archive.read('scripts/run.py') == (ROOT/'skills/shorts-scope/scripts/run.py').read_bytes()
        assert archive.read('SKILL.md').startswith(b'---\nname: "shorts-scope"\n')
