#!/usr/bin/env python3
"""Install the reviewed ShortsScope skill bundle; never run pip or alter host configuration."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def destination(host, scope, home, workspace=None, target=None):
    if host == 'generic':
        if target is None: raise ValueError('generic requires a registry directory verified for your host (--target)')
        return Path(target).expanduser().resolve()
    if target is not None: raise ValueError('--target is only for a verified generic host')
    if host == 'openclaw':
        if workspace is None: raise ValueError('OpenClaw requires its actual active --workspace')
        return Path(workspace).expanduser().resolve() / 'skills/shorts-scope'
    base = Path(home) if scope == 'user' else Path(workspace or Path.cwd()).expanduser().resolve()
    return base / ('.agents' if host == 'codex' else '.claude') / 'skills/shorts-scope'


def install(host, scope='user', workspace=None, target=None, python=None, dry_run=False, home=None):
    repo = Path(__file__).resolve().parents[1]
    python = Path(python or repo / '.venv/bin/python').expanduser().absolute()
    if not python.is_file(): raise ValueError('Python not found; create the repo venv or pass --python')
    target = destination(host, scope, Path.home() if home is None else home, workspace, target)
    archive = repo / 'assets/shorts-scope.skill.zip'
    with zipfile.ZipFile(archive) as bundle:
        if set(bundle.namelist()) != {'SKILL.md', 'scripts/run.py'}:
            raise ValueError('unexpected skill bundle contents; refusing installation')
        files = {name: bundle.read(name) for name in bundle.namelist()}
    files['references/runtime.json'] = json.dumps({'repo': str(repo), 'python': str(python)}, indent=2).encode()
    result = {'host': host, 'target': str(target), 'repo': str(repo),
              'runtime_discovery_verified': False, 'dry_run': dry_run}
    if target.exists() or target.is_symlink():
        if not target.is_symlink() and target.is_dir() and all(
                (target/name).is_file() and (target/name).read_bytes() == data for name, data in files.items()):
            return {**result, 'status': 'already-installed'}
        raise ValueError('existing target differs; preserved without overwrite. Review/backup it before updating.')
    if dry_run: return {**result, 'status': 'planned'}
    subprocess.run([str(python), str(repo/'cli.py'), '--help'], check=True, capture_output=True, timeout=15)
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.shorts-scope-install-', dir=target.parent))
    try:
        for name, data in files.items():
            file = stage / name; file.parent.mkdir(parents=True, exist_ok=True); file.write_bytes(data)
        subprocess.run([str(python), str(stage/'scripts/run.py'), '--help'], check=True, capture_output=True, timeout=15)
        stage.rename(target)
    except BaseException:
        shutil.rmtree(stage)
        raise
    return {**result, 'status': 'installed', 'launcher_verified': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=['codex', 'claude', 'openclaw', 'generic'], required=True)
    parser.add_argument('--scope', choices=['user', 'project'], default='user')
    parser.add_argument('--workspace'); parser.add_argument('--target')
    parser.add_argument('--python'); parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try: print(json.dumps(install(args.host, args.scope, args.workspace, args.target, args.python, args.dry_run)))
    except (ValueError, OSError, subprocess.SubprocessError) as exc: parser.exit(1, f'install: {exc}\n')


if __name__ == '__main__': main()
