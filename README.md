# ShortsScope — inspect short videos, frame by frame

A model-agnostic CLI for agents: **fast frame extraction → optional final frame → numbered, timestamped contact sheet**. Developed for use inside OpenClaw, but not dependent on it. This community fork extends [claude-video](https://github.com/bradautomates/claude-video); original MIT copyright and license are retained. The goal is evidence-grounded analysis for making your own shorts.

Independent operations: **`extract`** prepares images locally; **`measure`** adds optional local motion/OCR/pose evidence; **`analyze`** prepares a structured visual-analysis request, imports any model's response, or explicitly runs an optional Codex backend. Designed to help a creator study short-video composition, actions and text styling. Neither operation automatically downloads references or makes a video.

`extract` never calls a model or uploads media. `analyze` defaults to offline preparation too; only `--backend codex` sends the selected images to your authenticated service. The calling AI chooses images, arguments and follow-up intervals. It is not a forced one-click summarizer.

## Install by asking your AI (copy/paste)

아래 프롬프트를 **로컬 도구를 사용할 수 있는 AI**에 붙여넣으세요. 저장소 복제 → 가상환경 → 호스트별 스킬 등록 → 실제 인식 확인 순서로 진행하도록 되어 있습니다.

```text
https://github.com/JangHyuckYun/shorts-scope 를 현재 AI 환경에 설치해줘.
먼저 그 저장소의 docs/install/README.md와 현재 호스트별 가이드를 읽어줘:
Codex는 docs/install/codex.md, Claude Code는 docs/install/claude.md,
OpenClaw는 docs/install/openclaw.md, Grok은 docs/install/grok.md.
모델 이름이 아니라 실제 실행 호스트를 기준으로 선택해줘.
영구 보관할 사용자 디렉터리에 git clone하고 기존 파일/변경은 보존해줘.
저장소 venv와 requirements-compact.txt를 설치하고 FFmpeg/ffprobe를 확인해줘.
설치 스크립트를 읽고 올바른 호스트/워크스페이스로 dry-run 후 스킬을 등록해줘.
설치된 실행기 작동과 호스트가 shorts-scope를 실제 인식하는지 각각 확인해줘.
관련 없는 설정 변경, 기존 스킬 덮어쓰기, 모델/가중치 자동 설치는 하지 마.
로컬 실행이나 등록 기능이 없으면 설치했다고 하지 말고 필요한 경로를 알려줘.
끝나면 설치 위치와 내가 이 스킬을 쓰는 예시를 보여줘.
```

Host-specific copy/paste prompts: [Codex](docs/install/codex.md) · [Claude Code](docs/install/claude.md) · [OpenClaw](docs/install/openclaw.md) · [Grok / model-vs-host](docs/install/grok.md).

Grok inside OpenClaw uses the OpenClaw installer. Native registration in ordinary Grok web chat has **not** been verified. The installer tests paths/launcher; the receiving agent must still verify runtime discovery. [Installation details and update behavior](docs/install/README.md).

## Install and extract

Requires Python3.10+, FFmpeg/ffprobe on PATH. Pillow is optional for upstream `/watch`, required for this extraction adapter.

```sh
git clone https://github.com/JangHyuckYun/shorts-scope.git
cd shorts-scope
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

## Optional frame-by-frame shorts analysis

Analysis reads **selected individual frames**, avoiding montage-coordinate ambiguity and preserving more detail than small grid cells. It records objects/estimated boxes/poses, visible text and styling, temporal comparisons, editing observations and evidence-linked creation suggestions.

```sh
# No model call: schema + prompt + image list for any image-capable AI
.venv/bin/python cli.py analyze output/overview/manifest.json --out output/request

# Import that AI's raw JSON response; validate and produce JSON + readable report
.venv/bin/python cli.py analyze output/overview/manifest.json --out output/analysis \
  --backend import --response response.json

# Or explicitly run the optional authenticated Codex backend (POSIX)
.venv/bin/python cli.py analyze output/overview/manifest.json --out output/codex-analysis \
  --backend codex --model gpt-5.6-luna --effort low --timeout 180
```

The Codex adapter requires a separately installed/authenticated CLI supporting `--image`, `--output-schema`, `--json`, `--ignore-user-config` and `--ephemeral`. Select an image-capable model available to your account. OpenClaw and Codex are **not** required for prepare/import.

`analysis.json` and `report.md` distinguish visible evidence from creative proposals. Font appearance, weight, stroke and shadow are **visual estimates**, not recovered editor settings; `exact_font_name` is always null. This is **sampled-frame analysis, not exhaustive analysis of every video frame**, verified tracking, audio analysis or guaranteed OCR. Follow-up suggestions are data, never automatically executed.

[Detailed usage, output fields and verification](docs/SHORTS_ANALYSIS.md)

## Ground the analysis in local evidence

```sh
# Optional local measurements (no remote model/API)
.venv/bin/python -m pip install -r requirements-evidence.txt
.venv/bin/python cli.py measure output/detail/manifest.json --out output/evidence \
  --motion-roi 0,0,1,0.35

# Keep dense measurements but send only chosen full frames to the AI
.venv/bin/python cli.py analyze output/detail/manifest.json --out output/grounded \
  --evidence output/evidence/evidence.json --select-frames 1,3,5,7
```

Choose a visible background ROI; the example top strip is not universally background. Optional OCR adds measured text boxes, detail crops and user-supplied font candidate ranking. Optional pose landmarks flag missing foot evidence; they **do not classify running/walking**. [Commands and limitations](docs/EVIDENCE.md) · [Actual before/after evidence](docs/BENCHMARK.md).

## What differs from upstream?

We reuse upstream keyframe extraction and deduplication. Our adapter adds explicit endpoint preservation, a bounded numbered contact sheet, agent-controlled layout/range/encoding, and machine-readable output. The separate analysis adapter adds a provider-neutral response contract, geometry/reference validation and reports. It is not a new vision model or a new image-grid research method.

## Evidence and limitations

One25.7s prototype test measured input21981→17638 tokens and preprocessing2.45→0.46s. These include changed prompts/resolutions and harness context; they are not claims of general accuracy, portable speed, billing savings or the current configurable CLI's performance. Walking/running classification remains unverified. Small cells lose detail; the model can confuse times, and large sheets may be downscaled. More frames need not improve understanding. Uniform mode currently performs per-timestamp seeks and is intended for focused follow-up, not claimed to be the fastest mode.

[Research and improvement directions](docs/RESEARCH.md) · [Development background](docs/OPENCLAW.md) · [License review](docs/LICENSE_REVIEW.md)

## License

MIT; see [LICENSE](LICENSE). Original copyright retained. No third-party videos, screenshots, comments or model weights bundled. External FFmpeg builds and third-party media have their own terms. Not affiliated with OpenClaw, Anthropic, OpenAI or xAI.
