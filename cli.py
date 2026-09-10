#!/usr/bin/env python3
"""Composable video tools. Currently exposes extraction only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent/'skills/watch/scripts'))


def main():
    if len(sys.argv)<2 or sys.argv[1] in ('-h','--help'):
        print('Usage: python cli.py extract SOURCE --out DIR [options]\n\nextract: keyframes/uniform sampling + optional endpoint + numbered contact sheet.\nRun python cli.py extract --help for all arguments. No model calls or uploads.')
        return
    if sys.argv[1]!='extract':
        raise SystemExit('Unknown command; available: extract')
    del sys.argv[1]
    from compact import main as extract
    extract()


if __name__=='__main__':
    main()
