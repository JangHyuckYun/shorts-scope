"""Offline contracts for composable analysis; model accuracy is not asserted here."""
import copy
import json
import os
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / 'skills/watch/scripts'))
from shorts import analyze, load_manifest, local_path, validate


@pytest.fixture
def bundle(tmp_path):
    # Preparation validates paths, not image content; no real service sees this placeholder.
    (tmp_path / 'frame.jpg').write_bytes(b'placeholder')
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'duration_seconds': 1, 'frames': [
        {'index': 1, 'time_seconds': 0, 'label': '0s', 'file': 'frame.jpg'}]}))
    return manifest


@pytest.fixture
def answer():
    return {
        'summary': 'A red box and a title.',
        'frames': [{'frame_index': 1, 'observation': 'Red box at left.',
            'objects': [{'track_hint': 'box', 'category': 'red rectangle',
                'bbox': [.1, .2, .3, .4], 'pose_or_state': 'upright', 'confidence': 'high'}],
            'text_regions': [{'text': 'HELLO', 'kind': 'title', 'bbox': [.1, .7, .9, .8],
                'font_family_appearance': 'sans', 'exact_font_name': None,
                'weight_appearance': 'bold', 'italic': False, 'text_color': 'white',
                'outline': 'black', 'shadow': 'lower right', 'background': 'none',
                'alignment': 'center', 'relative_height': .1, 'confidence': 'medium',
                'uncertainty': 'Estimated from raster pixels.'}],
            'composition': 'Vertical', 'lighting_color': 'Dark background',
            'uncertainty': 'Sample only.'}],
        'temporal_observations': [], 'editing_notes': ['No audio.'],
        'creation_suggestions': [{'suggestion': 'Use contrast.', 'evidence_frames': [1],
                                 'basis': 'Visible white text on a dark background.'}],
        'followup_ranges': [{'start_seconds': 0, 'end_seconds': .9, 'reason': 'Check motion.'}],
        'limitations': ['One sampled frame, no motion conclusion.'],
    }


def test_prepare_without_model(bundle, tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('offline preparation attempted to execute a process')
    monkeypatch.setattr('shorts.subprocess.Popen', forbidden)
    out = tmp_path / 'prepared'
    result = analyze(bundle, out)
    assert result['model_called'] is False
    request = json.loads((out / 'request.json').read_text())
    assert request['images'] == [str(tmp_path / 'frame.jpg')]
    assert request['timeline'][0]['index'] == 1
    assert not (out / 'analysis.json').exists()
    with pytest.raises(ValueError, match='empty'):
        analyze(bundle, out)


def test_manifest_path_boundary(tmp_path):
    root = tmp_path / 'root'
    root.mkdir()
    outside = tmp_path / 'private.jpg'
    outside.write_bytes(b'x')
    with pytest.raises(ValueError, match='outside'):
        local_path(root, '../private.jpg')
    with pytest.raises(ValueError, match='relative'):
        local_path(root, str(outside))
    (root / 'link.jpg').symlink_to(outside)
    with pytest.raises(ValueError, match='outside'):
        local_path(root, 'link.jpg')


@pytest.mark.parametrize('mutation', ['duration', 'time', 'duplicate', 'end'])
def test_bad_manifest(bundle, mutation):
    data = json.loads(bundle.read_text())
    if mutation == 'duration': data['duration_seconds'] = float('nan')
    if mutation == 'time': data['frames'][0]['time_seconds'] = 2
    if mutation == 'duplicate': data['frames'] *= 2
    if mutation == 'end': data['frames'][0].update(time_seconds=None, label='unknown')
    bundle.write_text(json.dumps(data))
    with pytest.raises(ValueError): load_manifest(bundle)


@pytest.mark.parametrize('mutation', [
    'bbox', 'nan', 'font', 'missing', 'extra', 'enum', 'duplicate', 'boolean',
    'evidence', 'followup', 'temporal',
])
def test_invalid_model_response(answer, mutation):
    data = copy.deepcopy(answer)
    frame = data['frames'][0]
    if mutation == 'bbox': frame['objects'][0]['bbox'] = [.9, 0, .1, 1]
    if mutation == 'nan': frame['objects'][0]['bbox'][0] = float('nan')
    if mutation == 'font': frame['text_regions'][0]['exact_font_name'] = 'Invented Font'
    if mutation == 'missing': del frame['composition']
    if mutation == 'extra': frame['made_up_field'] = 'unsupported'
    if mutation == 'enum': frame['objects'][0]['confidence'] = 'certain'
    if mutation == 'duplicate': data['frames'] *= 2
    if mutation == 'boolean': frame['objects'][0]['bbox'][0] = False
    if mutation == 'evidence': data['creation_suggestions'][0]['evidence_frames'] = [999]
    if mutation == 'followup': data['followup_ranges'][0]['end_seconds'] = 2
    if mutation == 'temporal': data['temporal_observations'] = [{
        'from_frame': 1, 'to_frame': 1, 'subject_motion': '', 'camera_motion': '',
        'transition': '', 'confidence': 'unknown', 'uncertainty': ''}]
    with pytest.raises(ValueError): validate(data, [1], 1)


def test_import_any_model_offline(bundle, tmp_path, answer, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('offline import attempted to execute a process')
    monkeypatch.setattr('shorts.subprocess.Popen', forbidden)
    raw = tmp_path / 'raw.json'
    raw.write_text(json.dumps(answer))
    out = tmp_path / 'imported'
    result = analyze(bundle, out, backend='import', response=raw)
    saved = json.loads((out / 'analysis.json').read_text())
    assert saved['analysis'] == answer
    assert saved['meta']['model_requested'] is None
    assert saved['meta']['seconds'] is None
    assert result['model_called'] is False
    assert 'HELLO' in (out / 'report.md').read_text()
    answer['frames'][0]['objects'][0]['bbox'] = [1, 0, 0, 1]
    raw.write_text(json.dumps(answer))
    with pytest.raises(ValueError):
        analyze(bundle, tmp_path / 'invalid', backend='import', response=raw)
    assert not (tmp_path / 'invalid/analysis.json').exists()


@pytest.fixture
def fake_codex(tmp_path, monkeypatch, answer):
    """Exercise actual subprocess/JSONL handling without a network or auth dependency."""
    raw = tmp_path / 'fake-response.json'
    raw.write_text(json.dumps(answer))
    binary = tmp_path / 'bin'
    binary.mkdir()
    script = binary / 'codex'
    script.write_text('#!' + sys.executable + '\n' + '''
import json,os,pathlib,sys,time
args=sys.argv[1:]
assert args[args.index('--sandbox')+1]=='read-only'
assert '-i' in args and '--output-schema' in args
mode=os.environ.get('FAKE_MODE','ok')
if mode=='timeout':time.sleep(30)
if mode=='failed':sys.exit(7)
data=json.loads(pathlib.Path(os.environ['FAKE_RESPONSE']).read_text())
if mode=='bad-shape':data['frames'][0]['objects'][0]['bbox']=[.9,0,.1,1]
pathlib.Path(args[args.index('-o')+1]).write_text(json.dumps(data))
if mode!='missing-event':print(json.dumps({'type':'turn.completed','usage':{'input_tokens':123}}))
''')
    script.chmod(0o755)
    monkeypatch.setenv('PATH', str(binary) + os.pathsep + os.environ.get('PATH', ''))
    monkeypatch.setenv('FAKE_RESPONSE', str(raw))


@pytest.mark.skipif(os.name != 'posix', reason='Codex process-group backend is POSIX')
def test_codex_success(bundle, tmp_path, fake_codex):
    result = analyze(bundle, tmp_path / 'run', backend='codex')
    saved = json.loads(Path(result['result']).read_text())
    assert saved['meta']['usage'][0]['input_tokens'] == 123
    assert saved['meta']['model_requested'] == 'gpt-5.6-luna'
    assert result['model_called'] is True


@pytest.mark.skipif(os.name != 'posix', reason='Codex process-group backend is POSIX')
@pytest.mark.parametrize('mode', ['failed', 'bad-shape', 'missing-event', 'timeout'])
def test_codex_failure_is_not_success(bundle, tmp_path, fake_codex, monkeypatch, mode):
    monkeypatch.setenv('FAKE_MODE', mode)
    out = tmp_path / 'failed-run'
    with pytest.raises((RuntimeError, ValueError)):
        analyze(bundle, out, backend='codex', timeout=.05 if mode == 'timeout' else 5)
    assert not (out / 'analysis.json').exists()
    assert not (out / 'report.md').exists()
