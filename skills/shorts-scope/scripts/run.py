#!/usr/bin/env python3
"""Run the verified ShortsScope checkout from a copied or repository-local skill."""
import json
import os
from pathlib import Path
import sys

skill_dir = Path(__file__).resolve().parents[1]
runtime = skill_dir / 'references/runtime.json'
if runtime.is_file():
    config = json.loads(runtime.read_text())
    repo, python = Path(config['repo']), Path(config['python'])
else:
    repo = Path(__file__).resolve().parents[3]
    python = repo / '.venv/bin/python'
    if not python.is_file(): python = Path(sys.executable)
if not (repo / 'cli.py').is_file() or not python.is_file():
    raise SystemExit('ShortsScope checkout or Python is missing; rerun the installation guide.')
os.execv(str(python), [str(python), str(repo / 'cli.py'), *sys.argv[1:]])
