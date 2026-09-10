# Codex installation

For a local filesystem-enabled Codex host. Official discovery documentation: [Codex skills](https://developers.openai.com/codex/skills). User scope is `~/.agents/skills`; project scope is `<project>/.agents/skills`. Do not invent a `.codex/skills` default for this guide.

## Copy/paste into Codex

```text
Install ShortsScope from https://github.com/JangHyuckYun/shorts-scope for this Codex
environment. Read docs/install/README.md and docs/install/codex.md from that exact
repository first. Clone it into a persistent user-writable directory, preserving any
existing checkout or changes. Create its local Python venv and install requirements-
compact.txt; check FFmpeg/ffprobe. Review and run scripts/install_skill.py --host codex
--dry-run, then install for the current user. Do not change unrelated configuration or
install optional models. Verify the installed launcher and that Codex discovers shorts-
scope; report its actual path and an invocation example. If this environment has no
persistent local execution, explain the specific missing capability rather than claiming
installation. No need to ask again for ordinary authorized local setup.
```

## Commands after common setup

```sh
.venv/bin/python scripts/install_skill.py --host codex --dry-run
.venv/bin/python scripts/install_skill.py --host codex
```

Project-only alternative: add `--scope project --workspace /actual/project` to both commands. Do not commit `references/runtime.json` with workstation paths. In Codex use `/skills` to verify discovery and invoke `$shorts-scope`. If the host hasn't refreshed inventory, start a fresh session.

Example request: **“Use $shorts-scope to extract an overview of this local short. If motion is ambiguous, choose a narrow interval and measure the background. Do not call another model.”** The host's current AI can perform analysis through prepare/import; Codex backend calls remain an explicit option.
