# OpenClaw installation

Official sources: [Skills](https://docs.openclaw.ai/tools/skills) and [skills CLI](https://docs.openclaw.ai/cli/skills). Identify the **actual active agent workspace** first; custom agents and remote Gateways may use a different filesystem. This guide installs to `<workspace>/skills/shorts-scope` and does not edit `openclaw.json`, bypass policy, activate cron jobs or select a different model.

## Copy/paste into OpenClaw

```text
Install ShortsScope from https://github.com/JangHyuckYun/shorts-scope for the active
OpenClaw agent. Read docs/install/README.md and docs/install/openclaw.md first. Determine
the real agent workspace and execution machine from trusted runtime context, not a guessed
default. Clone the repository into a persistent directory available on that machine,
preserving existing work, set up its Python venv with requirements-compact.txt, and check
FFmpeg/ffprobe. Review scripts/install_skill.py; run --host openclaw --workspace <actual-
workspace> --dry-run, then install. Verify the launcher and use the supported skills
list/info/check commands for the same agent/Gateway to confirm discovery. Respect any
existing installation policy; do not change allowlists or bypass a rejection. Do not invoke
a paid model or install optional weights during setup. Report the installed path and a
usable invocation, distinguishing file installation from runtime discovery.
```

## Commands after common setup

Replace the placeholder with the active agent's actual workspace, on the execution machine:

```sh
.venv/bin/python scripts/install_skill.py --host openclaw --workspace /actual/agent/workspace --dry-run
.venv/bin/python scripts/install_skill.py --host openclaw --workspace /actual/agent/workspace
openclaw skills list
openclaw skills info shorts-scope
openclaw skills check
```

Where supported, use `--agent <actual-agent-id>` to query the same agent. The selected Gateway is authoritative; local files on a different machine do not establish installation there. An allowlist or unmet requirement is a real discovery blocker, not permission to override configuration. Refresh the agent session if its skill snapshot is stale.

Example: **“Use the shorts-scope skill to inspect this short. Start with a cheap overview, measure a background region if the camera movement is unclear, and analyze only selected frames.”** Works the same when the configured model is Grok, Claude or OpenAI, provided that host supplies local tool and image access. No specific slash-command routing is assumed for OpenClaw chat channels.
