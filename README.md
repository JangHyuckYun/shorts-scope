# Composable video frame extraction

A model-agnostic CLI for agents: **fast frame extraction → optional final frame → numbered, timestamped contact sheet**. Developed for use inside OpenClaw, but not dependent on it. This community fork extends [claude-video](https://github.com/bradautomates/claude-video); original MIT copyright and license are retained. A new project name has not yet been selected.

This tool prepares visual inputs. **It does not call an AI model, summarize, upload media, or infer why a video is popular.** An agent chooses the arguments, reads the resulting images, and decides whether to inspect a smaller interval.

## Install and extract

Requires Python3.10+, FFmpeg/ffprobe on PATH. Pillow is optional for upstream `/watch`, required for this extraction adapter.

```sh
git clone https://github.com/JangHyuckYun/claude-video.git
cd claude-video
python3 -m venv .venv
.venv/bin/pip install -r requirements-compact.txt
.venv/bin/python cli.py extract video.mp4 --out output/overview
```

`stdout` is a JSON result; nonzero exit indicates failure. Output directories must be empty. `sheet.jpg` (or PNG), individual frames, `manifest.json`, and optional-use `prompt.txt` remain local. The JSON contains relative frame paths, timestamps, selected options and processing time. Read the image as an actual image, not just its path. END means the last decoded frame **within the selected range**, not an exact timestamp. All frames have stable indices.

## Agent-controllable options

- `--sampler keyframes|uniform`: default keyframes reuses upstream fast extraction and fallback. Uniform requests evenly spaced positions for inspecting motion.
- `--start SECONDS`, `--end SECONDS`: selected interval; end exclusive, default whole video.
- `--max-frames N`: total budget including endpoint,2–24, default8. Actual count may be lower.
- `--no-endpoint`: do not reserve/add the final frame.
- `--no-dedup`: disable upstream keyframe deduplication. Uniform coverage anchors are never deduplicated.
- `--width N`: frame width160–640, default240.
- `--max-height N`: cell image height limit160–1280; default twice width, aspect ratio preserved.
- `--columns N`:1–6, default3.
- `--padding N`: cell gutter0–64px, default12. Zero gutters may increase temporal confusion.
- `--format jpg|png`: default jpg.
- `--quality N`: JPEG quality1–95, default85; ignored for PNG.
- `--out DIR`: required fresh/empty output directory.

```sh
# Coarse overview, a narrow grid, no model call
.venv/bin/python cli.py extract video.mp4 --out output/coarse \
  --max-frames 6 --columns 3 --width 240

# Agent decided 10–14s needs closer inspection: denser local sequence
.venv/bin/python cli.py extract video.mp4 --out output/detail \
  --start 10 --end 14 --sampler uniform --max-frames 12 \
  --columns 4 --width 320 --padding 16 --format png

# Preserve only selected keyframe candidates, without endpoint/dedup
.venv/bin/python cli.py extract video.mp4 --out output/raw \
  --no-endpoint --no-dedup
```

The legacy `python skills/watch/scripts/compact.py ...` entry point remains supported. No OpenClaw runtime config or installed skill is changed. The inherited `/watch` implementation is separate; see the [upstream documentation](https://github.com/bradautomates/claude-video#readme) for its URL/caption/Whisper flow. Its plugin installer does not automatically invoke this CLI.

## What differs from upstream?

We reuse upstream keyframe extraction and deduplication. Our adapter adds explicit endpoint preservation, a bounded numbered contact sheet, agent-controlled layout/range/encoding, and machine-readable output. It is not a new vision model or a new image-grid research method.

## Evidence and limitations

One25.7s prototype test measured input21981→17638 tokens and preprocessing2.45→0.46s. These include changed prompts/resolutions and harness context; they are not claims of general accuracy, portable speed, billing savings or the current configurable CLI's performance. Walking/running classification remains unverified. Small cells lose detail; the model can confuse times, and large sheets may be downscaled. More frames need not improve understanding. Uniform mode currently performs per-timestamp seeks and is intended for focused follow-up, not claimed to be the fastest mode.

[Research and improvement directions](docs/RESEARCH.md) · [Development background](docs/OPENCLAW.md) · [License review](docs/LICENSE_REVIEW.md)

## License

MIT; see [LICENSE](LICENSE). Original copyright retained. No third-party videos, screenshots, comments or model weights bundled. External FFmpeg builds and third-party media have their own terms. Not affiliated with OpenClaw or Anthropic.
