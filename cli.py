#!/usr/bin/env python3
"""Composable video tools. Extraction and optional structured analysis."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent/'skills/watch/scripts'))


def main():
    if len(sys.argv)<2 or sys.argv[1] in ('-h','--help'):
        print('Usage: python cli.py extract SOURCE --out DIR [options]\n\nextract: keyframes/uniform sampling + optional endpoint + numbered contact sheet.\nRun python cli.py extract --help for all arguments. extract never calls a model.\nanalyze MANIFEST --out DIR [--backend prepare|codex|import] prepares or runs structured shorts analysis.')
        return
    if sys.argv[1] not in ('extract','analyze'):
        raise SystemExit('Unknown command; available: extract, analyze')
    command = sys.argv.pop(1)
    if command == "extract":
        from compact import main as run
    else:
        from shorts import main as run
    run()


if __name__=='__main__':
    main()
