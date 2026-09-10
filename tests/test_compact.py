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


def test_uniform_range_and_layout(tmp_path):
    Image=pytest.importorskip('PIL.Image')
    src=tmp_path/'range.mp4'
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=s=64x64:r=20:d=2',str(src)],check=True)
    result=prepare(src,tmp_path/'out',budget=4,width=160,sampler='uniform',
                   start=.5,end=1.5,endpoint=False,columns=2,padding=8,
                   max_height=160,image_format='png')
    assert len(result['frames'])==4
    assert all(.5<=f['time_seconds']<1.5 for f in result['frames'])
    assert all(f['label']!='END' for f in result['frames'])
    assert result['options']['dedup'] is False
    with Image.open(tmp_path/'out'/result['sheet']) as sheet:
        assert sheet.size==(352,400)
    with pytest.raises(ValueError,match='start'):
        prepare(src,tmp_path/'invalid',start=1.5,end=.5)
    assert not (tmp_path/'invalid').exists()
