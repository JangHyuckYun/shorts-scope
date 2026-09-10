"""Synthetic-media integration checks; no third-party footage/network."""
import sys
from pathlib import Path
import subprocess
import pytest
sys.path.insert(0, str(Path(__file__).parents[1]/'skills/watch/scripts'))
from compact import prepare


def test_short_clip_endpoint_and_budget(tmp_path):
    pytest.importorskip('PIL')
    src=tmp_path/'short.mp4'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=red:s=64x64:r=30:d=0.3',str(src)],check=True)
    out=tmp_path/'out'
    result=prepare(src,out,budget=2,width=160)
    assert 1 <= len(result['frames']) <= 2
    assert result['frames'][-1]['label']=='END'
    assert (out/'sheet.jpg').is_file()
    assert result['model_called'] is False
    with pytest.raises(ValueError,match='empty'):
        prepare(src,out)


def test_invalid_source(tmp_path):
    pytest.importorskip('PIL')
    with pytest.raises(ValueError,match='existing'):
        prepare(tmp_path/'missing.mp4',tmp_path/'out')
