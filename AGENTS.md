# ShortsScope repository guide

ShortsScope is a model-neutral, agent-controlled CLI for inspecting short videos. Public repository: https://github.com/JangHyuckYun/shorts-scope. Preserve the original MIT license and attribution documented in UPSTREAM.md.

## Product and boundaries

- `extract` prepares local video frames, endpoint and numbered contact sheet. No remote model call.
- `measure` optionally adds local image-plane motion, OCR/crops/font candidates and pose availability. Missing feet are not a gait classification.
- `analyze` defaults to offline request preparation; import accepts another AI's raw JSON. `--backend codex` explicitly calls a separately authenticated external service.
- Keep these independent primitives. Do not force automatic summarization, download, model calls, configuration changes or background jobs.
- Keep README.md in English and README.ko.md in Korean, with reciprocal language links and separate Codex/Claude Code/Grok/OpenClaw installation prompt blocks.

## Layout and distribution

- `cli.py`: public CLI entry point.
- `skills/watch/scripts/`: Python implementation. Historical directory name retained for compatibility with existing imports. Some inherited utilities are kept as source, not advertised or registered as a `/watch` skill.
- `assets/shorts-scope.skill.zip`: exported ShortsScope skill instructions and launcher.
- `skills/shorts-scope/scripts/run.py`: reviewable launcher source, matching the archive.
- `scripts/install_skill.py`: copies the exported bundle and points it at the full clone/venv. No network or pip calls; refuses changed existing targets. Keep the checkout available after installation.
- `docs/install/`: actual host-specific registration guides. Grok model identity alone does not define a registry.
- `docs/EVIDENCE.md`, `docs/SHORTS_ANALYSIS.md`, `docs/BENCHMARK.md`: behavior, contracts and measured limits.
- `examples/`: original reproducible fixtures/evaluations; no third-party video required.

There are no upstream marketplace manifests, auto-setup hooks or inherited tag-triggered releases in this fork. Do not restore the old `/watch` publication workflow or point install metadata at the upstream project. New release versions must describe ShortsScope, not inherit upstream version claims. Generic plugin/skills CLIs are not the documented installer for this full-checkout adapter.

## Checks

Base: Python3.10+, FFmpeg/ffprobe and requirements-compact.txt. Optional measurements: requirements-evidence.txt, with Tesseract/pose assets separately provided. Run `python -m pytest -q` in a suitable venv; synthetic CV checks require evidence extras. `python examples/evaluate_motion.py` runs known-transform checks. Model tests are offline and never count as model-accuracy evidence.

Keep tests, docs and the skill ZIP in source archives: they are needed to inspect, install and verify this repository. Do not add export-ignore rules that exclude the required bundle.

## Honesty and local data

Never commit credentials, private runtime.json paths, third-party media or raw service logs. Schema validation is not factual verification. Do not claim exact font recovery, calibrated object tracking, exhaustive video coverage or reliable walking/running classification without evidence. Preserve requested/actual settings and distinguish remote timeouts from successful analysis. File installation and launcher smoke tests do not prove host discovery; verify the selected runtime separately.
