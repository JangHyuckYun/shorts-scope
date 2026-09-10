# Install ShortsScope as an agent skill

This installs the **ShortsScope CLI skill**, not the upstream `/watch` plugin. Keep the cloned repository: the installed launcher delegates to that checkout. No model credentials, background jobs, host configuration changes or automatic paid model calls are part of installation.

Choose the **host running the agent**, not the model name:

- [Codex CLI / local Codex host](codex.md)
- [Claude Code](claude.md), not an assumption about claude.ai web
- [OpenClaw](openclaw.md), including when its model is Grok/Claude/OpenAI
- [Grok and custom tool-enabled hosts](grok.md)

## Common setup (Linux/macOS; Windows through WSL)

Clone into a persistent user-writable location, not a temporary directory. If that location exists, inspect its remote and worktree first; do not reset or overwrite local edits. Start by reading this guide and the installer source, then:

```sh
git clone https://github.com/JangHyuckYun/shorts-scope.git
cd shorts-scope
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-compact.txt
ffmpeg -version
ffprobe -version
.venv/bin/python cli.py extract --help
```

Python 3.10+ and external FFmpeg/ffprobe are required. If FFmpeg is missing, use the platform's supported package manager within the user's permitted scope; do not attempt sudo without permission. Core installation does not need NumPy, MediaPipe, Tesseract, a GPU or an API key. Measurement dependencies are separate and opt-in: [Evidence guide](../EVIDENCE.md).

Use the host guide below to run `scripts/install_skill.py`. The installer itself never runs pip or fetches network resources. `--dry-run` reports its destination before writing. It installs an exported `SKILL.md`, a small launcher, and local `references/runtime.json` containing the checkout/interpreter paths. Keep those private machine paths out of public commits.

## Installation is not runtime discovery

A successful installer reports `launcher_verified: true` only after executing the launcher. It always reports `runtime_discovery_verified: false`: **the receiving host must actually discover the skill**, then the agent should run the installed launcher and demonstrate one small extraction. Use a fresh session if the host caches skill inventory. Never claim a generic directory copy is proof of discovery.

This release tested isolated Codex, Claude Code and OpenClaw destination layouts, launcher execution, idempotent installation and refusal to overwrite changed files. It did **not** run every provider's interactive UI. Host settings, allowlists and remote execution boundaries may affect discovery. In a cloud agent with no persistent filesystem, local installation is not available through a chat prompt alone.

## Updating / removal

The installed launcher uses its original clone, so do not move/delete that checkout. Review updates and use a fast-forward pull only in a clean, matching clone. Re-run installer dry-run afterward. Identical installs are a no-op; changed skill contents are refused, preserving the old target. Review and back up the existing directory before explicitly replacing it; this installer has no force option. To uninstall, remove only the reported `shorts-scope` skill directory and, if no longer needed, its clone/venv. Do not remove a shared skills root.

## Bundle provenance

`assets/shorts-scope.skill.zip` is a Skill Workshop-authored export containing exactly `SKILL.md` and `scripts/run.py`; the installer rejects unexpected archive paths. The same launcher source is reviewable at `skills/shorts-scope/scripts/run.py`. Inspect the instruction artifact with `unzip -p assets/shorts-scope.skill.zip SKILL.md` before installation. `skills/shorts-scope/` alone is **not** a standalone `npx skills add` package; the dedicated installer provisions the runtime link. Inherited `/watch` plugin packaging/registration and auto-setup hooks have been removed; only the dedicated ShortsScope installation path is advertised. Reused Python utilities remain as source.
