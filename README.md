# ShortsScope — inspect short videos, frame by frame

**English** · [한국어](README.ko.md)

A model-agnostic CLI for agents: **fast frame extraction → optional final frame → numbered, timestamped contact sheet**. Developed for use inside OpenClaw, but not dependent on it. This community fork extends [claude-video](https://github.com/bradautomates/claude-video); original MIT copyright and license are retained. The goal is evidence-grounded analysis for making your own shorts.

Independent operations: **`extract`** prepares images locally; **`measure`** adds optional local motion/OCR/pose evidence; **`analyze`** prepares a structured visual-analysis request, imports any model's response, or explicitly runs an optional Codex backend. Designed to help a creator study short-video composition, actions and text styling. None of these operations automatically downloads references or makes a video.

`extract` never calls a model or uploads media. `analyze` defaults to offline preparation too; only `--backend codex` sends the selected images to your authenticated service. The calling AI chooses images, arguments and follow-up intervals. It is not a forced one-click summarizer.

## Install by asking your AI (copy/paste)

Paste the block for your **actual agent host**. Each prompt covers cloning the repository, creating its venv, installing the skill and verifying discovery. These require local tools and persistent storage, not just a model's web chat.

### Codex

```text
Install ShortsScope from https://github.com/JangHyuckYun/shorts-scope for this Codex environment. Read docs/install/README.md and docs/install/codex.md from that exact repository first. Clone it into a persistent user-writable directory, preserving any existing checkout or changes. Create its local Python venv and install requirements-compact.txt; check FFmpeg/ffprobe. Review and run scripts/install_skill.py --host codex --dry-run, then install for the current user. Do not change unrelated configuration or install optional models. Verify the installed launcher and that Codex discovers shorts-scope; report its actual path and an invocation example. If this environment has no persistent local execution, explain the specific missing capability rather than claiming installation. No need to ask again for ordinary authorized local setup.
```

[Detailed Codex installation guide](docs/install/codex.md).

### Claude Code

```text
Install ShortsScope from https://github.com/JangHyuckYun/shorts-scope for this Claude Code environment. Read docs/install/README.md and docs/install/claude.md from that exact repository first. Clone into a persistent user-writable directory without overwriting any existing work. Set up the repository venv with requirements-compact.txt and check FFmpeg/ffprobe. Review scripts/install_skill.py, run --host claude --dry-run, then install for this user. Verify the installed launcher and that Claude Code discovers the shorts-scope skill. Report the actual directory and how to invoke it. Do not modify unrelated settings, install optional models or call paid analysis backends during setup. If local tools/persistent storage are unavailable, explain that limitation instead of reporting success.
```

[Detailed Claude Code installation guide](docs/install/claude.md).

### Grok

```text
I want to install ShortsScope from https://github.com/JangHyuckYun/shorts-scope. First identify the host running you, whether it has persistent local shell/filesystem access, and its documented skill registry. Read docs/install/README.md and docs/install/grok.md. If you are inside OpenClaw, follow docs/install/openclaw.md, clone into a persistent directory, set up the venv and verify skill discovery for the actual agent. If another host explicitly supports Agent Skills, use its verified registry and the generic installer dry-run before installation. Do not invent a Grok registration API or ~/.grok/skills directory. If this is ordinary Grok web chat without local execution, state that no local skill has been installed and give the OpenClaw/local-host setup route. Do not request API keys in chat or change unrelated host configuration.
```

[Detailed Grok installation guide](docs/install/grok.md).

### OpenClaw

```text
Install ShortsScope from https://github.com/JangHyuckYun/shorts-scope for the active OpenClaw agent. Read docs/install/README.md and docs/install/openclaw.md first. Determine the real agent workspace and execution machine from trusted runtime context, not a guessed default. Clone the repository into a persistent directory available on that machine, preserving existing work, set up its Python venv with requirements-compact.txt, and check FFmpeg/ffprobe. Review scripts/install_skill.py; run --host openclaw --workspace <actual-workspace> --dry-run, then install. Verify the launcher and use the supported skills list/info/check commands for the same agent/Gateway to confirm discovery. Respect any existing installation policy; do not change allowlists or bypass a rejection. Do not invoke a paid model or install optional weights during setup. Report the installed path and a usable invocation, distinguishing file installation from runtime discovery.
```

[Detailed OpenClaw installation guide](docs/install/openclaw.md).

Grok inside OpenClaw uses the OpenClaw installer. Native registration in ordinary Grok web chat has **not** been verified. The installer checks paths and launcher execution; the receiving host must separately verify skill discovery. [Installation details and updates](docs/install/README.md).

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

The legacy `python skills/watch/scripts/compact.py ...` entry point remains supported. No OpenClaw runtime config or installed skill is changed. The upstream `/watch` plugin registration, marketplace manifests, setup hooks and release automation have been removed from this fork. Historical Python utilities remain for source compatibility; use the ShortsScope installer above. [Origin and retained attribution](UPSTREAM.md).

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

One 25.7s prototype test measured input 21,981→17,638 tokens and preprocessing 2.45→0.46s. These include changed prompts/resolutions and harness context; they are not claims of general accuracy, portable speed, billing savings or the current configurable CLI's performance. Walking/running classification remains unverified. Small cells lose detail; the model can confuse times, and large sheets may be downscaled. More frames need not improve understanding. Uniform mode currently performs per-timestamp seeks and is intended for focused follow-up, not claimed to be the fastest mode.

[Research and improvement directions](docs/RESEARCH.md) · [Development background](docs/OPENCLAW.md) · [License review](docs/LICENSE_REVIEW.md)

## License

MIT; see [LICENSE](LICENSE). Original copyright retained. No third-party videos, screenshots, comments or model weights bundled. External FFmpeg builds and third-party media have their own terms. Not affiliated with OpenClaw, Anthropic, OpenAI or xAI.
