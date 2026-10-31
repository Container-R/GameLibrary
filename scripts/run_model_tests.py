#!/usr/bin/env python3
"""Run repository-owned teaching models, isolated from one another.

This runs executable Python files: inspect repository changes before running.
It installs nothing and makes no network requests. Passing is not engine QA.
"""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    tests = sorted((root / 'research' / 'experiments').glob('*/test_*.py'))
    if not tests:
        print('ERROR: no model test files found', file=sys.stderr)
        return 1
    failed = []
    for test in tests:
        name = str(test.relative_to(root))
        print(f'\n=== {name} ===', flush=True)
        # No shell; each suite has its own module namespace.
        result = subprocess.run([sys.executable, str(test)], cwd=root)
        if result.returncode:
            failed.append(name)
    print(f'\nSuites: {len(tests)}; passed: {len(tests)-len(failed)}; failed: {len(failed)}', flush=True)
    for name in failed:
        print(f'FAILED: {name}', file=sys.stderr)
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
