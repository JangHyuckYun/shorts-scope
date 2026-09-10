# Claude Code installation

For **Claude Code with local tools**, not a promise about the Claude web chat. Official documentation: [Claude Code skills](https://code.claude.com/docs/en/skills). User scope is `~/.claude/skills`; project scope is `<project>/.claude/skills`.

## Copy/paste into Claude Code

```text
Install ShortsScope from https://github.com/JangHyuckYun/shorts-scope for this Claude Code
environment. Read docs/install/README.md and docs/install/claude.md from that exact
repository first. Clone into a persistent user-writable directory without overwriting any
existing work. Set up the repository venv with requirements-compact.txt and check
FFmpeg/ffprobe. Review scripts/install_skill.py, run --host claude --dry-run, then install
for this user. Verify the installed launcher and that Claude Code discovers the shorts-scope
skill. Report the actual directory and how to invoke it. Do not modify unrelated settings,
install optional models or call paid analysis backends during setup. If local
tools/persistent storage are unavailable, explain that limitation instead of reporting
success.
```

## Commands after common setup

```sh
.venv/bin/python scripts/install_skill.py --host claude --dry-run
.venv/bin/python scripts/install_skill.py --host claude
```

Project-only alternative: add `--scope project --workspace /actual/project`. Start a fresh session if needed, then invoke `/shorts-scope`. Do not install the upstream `/watch` plugin and assume it exposes this fork's `measure`/`analyze` workflow; these are different skill entry points.

Example: **“/shorts-scope Inspect the attached local clip's text placement and camera movement. Prepare only the tools you need, use your own image capability and save the validated report.”**
