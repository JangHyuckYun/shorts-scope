# Compact video input for OpenClaw

This community fork was created to prepare visual inputs for video analysis inside OpenClaw. It is not affiliated with OpenClaw or Anthropic. It does not train a model or provide native video understanding.

Upstream: https://github.com/bradautomates/claude-video
Baseline revision: 83da59fa78c3eee9e20f515fe75c438bb5166efd

Current configurable CLI reference: [README](../README.md). This document records the initial adapter background.

## Run locally

Requires Python 3.10+, ffmpeg/ffprobe and optional Pillow. No API key is required. The original `/watch` skill remains unchanged; its installer does not automatically enable this adapter.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-compact.txt
.venv/bin/python skills/watch/scripts/compact.py video.mp4 --out output/run-1
```

Send `sheet.jpg` as an image and `prompt.txt` as the accompanying instruction to your OpenClaw image-capable model. Do not send only the file path as text. `manifest.json` lists frame ordering. This adapter does not call a model, upload files, transcribe audio, install hooks or change OpenClaw configuration.

Changes: fast upstream keyframe extraction; reserve one slot for the last decoded frame; bounded frame count; numbered time-separated contact sheet; explicit temporal instructions. Default maximum8 cells, width240; adjustable `--max-frames 2..24`, `--width 160..640`. Use a fresh output directory; nonempty directories are refused. END is the last decoded frame in the selected interval, not an exact timestamp. A keyframe close to END may be redundant but END is intentionally retained.

## Exploratory evidence, not a benchmark claim

One cached25.7s portrait video was tested with Luna:max. Early prototypes measured2.45s scene sampling versus0.46s keyframe+endpoint+sheet, and21981 versus17638 total input tokens (~20% reduction). Tokens include harness context, and layout/prompt/resolution changed. These are single-run prototype figures, not portable guarantees or measurements of this packaged CLI. No source video, screenshots, comments, private logs or credentials are included.

An early sheet caused the model to merge different moments into “two people.” Gutters, numbering and temporal instructions fixed that in one rerun. Accurate running-versus-walking recognition was NOT established. Tiny text, fast action and audio-dependent content can be missed. Encoding keyframes are not semantic key moments. Test on your own representative videos before deployment; use individual larger frames for detailed inspection.

## Commercial use and rights

The upstream MIT license permits modification, distribution and commercial use, provided the original copyright and license notice are retained. See LICENSE and LICENSE_REVIEW.md. The software license does not grant rights to third-party videos, music, faces, captions, comments, trademarks, platform access or model services. Use media you have permission to process/share. No third-party media is redistributed here.
