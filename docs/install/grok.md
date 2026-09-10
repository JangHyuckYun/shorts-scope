# Grok: identify the host before installing

**Grok is a model/product name, not a verified local skill-registry path.** We have not verified a native Grok web-chat `SKILL.md` installation interface. Do not invent `~/.grok/skills` or claim ordinary Grok chat can clone a repository on your computer.

- **Grok through OpenClaw:** use [OpenClaw installation](openclaw.md). OpenClaw executes the CLI and manages skill discovery; Grok is the model.
- **Another local tool-enabled agent using Grok:** check that host's documented skill registry and filesystem access. Install there only when its actual contract supports Agent Skills.
- **Grok web without local execution:** it can read/reason about instructions, but that is not local installation. Use a local host or implement a tool-execution bridge.
- **xAI API:** [function calling](https://docs.x.ai/docs/guides/function-calling) supports caller-defined tools; the application executes those calls. This repo does not ship a Grok API connector or execute arbitrary tool arguments automatically.

## Copy/paste into your Grok-powered agent

```text
I want to install ShortsScope from https://github.com/JangHyuckYun/shorts-scope. First
identify the host running you, whether it has persistent local shell/filesystem access, and
its documented skill registry. Read docs/install/README.md and docs/install/grok.md. If you
are inside OpenClaw, follow docs/install/openclaw.md, clone into a persistent directory, set
up the venv and verify skill discovery for the actual agent. If another host explicitly
supports Agent Skills, use its verified registry and the generic installer dry-run before
installation. Do not invent a Grok registration API or ~/.grok/skills directory. If this is
ordinary Grok web chat without local execution, state that no local skill has been installed
and give the OpenClaw/local-host setup route. Do not request API keys in chat or change
unrelated host configuration.
```

## Verified generic registry only

After the common clone/venv setup, the following installs into an **exact skill directory supplied by the host operator** (not a parent registry):

```sh
.venv/bin/python scripts/install_skill.py --host generic --target /verified/registry/shorts-scope --dry-run
.venv/bin/python scripts/install_skill.py --host generic --target /verified/registry/shorts-scope
```

A successful copy/launcher smoke test is not proof the host discovered the skill. Confirm using that host's supported inventory/invocation before claiming success. If the host lacks Agent Skills but supports local commands, it can call `cli.py extract`, `measure`, and `analyze` directly; skill registration is optional, not a prerequisite for using the CLI.
