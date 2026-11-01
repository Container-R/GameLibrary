"""Explicit, nonempty reviewed model selection. Lists only unless --run is supplied.

Never infer repository from tool location. Does not install or use network.
Execution of a selected model still requires code review and separate authority.
"""
import argparse
import json
import math
from pathlib import Path, PurePosixPath
import subprocess
import sys


def select(root, directory, expected_suites):
    root=root.resolve()
    if not root.is_dir():raise ValueError('missing root')
    if not isinstance(directory,str) or not directory or '\\' in directory or ':' in directory or any(ord(c)<32 for c in directory) or PurePosixPath(directory).is_absolute() or any(x in ('','.','..') for x in directory.split('/')):raise ValueError('invalid directory')
    base=(root/directory).resolve()
    if not base.is_relative_to(root) or not base.is_dir():raise ValueError('invalid model directory')
    if not isinstance(expected_suites,list) or not expected_suites or any(not isinstance(x,str) or not x for x in expected_suites) or len(set(expected_suites))!=len(expected_suites):raise ValueError('nonempty unique suites required')
    found=sorted(base.glob('*/test_*.py'));names=[]
    for p in found:
        if not p.is_file() or not p.resolve().is_relative_to(base):raise ValueError('suite escapes model directory')
        names.append(p.relative_to(base).as_posix())
    if not found or set(names)!=set(expected_suites):raise ValueError('suite selection differs from frozen list')
    return found


def positive_timeout(value):
    number=float(value)
    if not math.isfinite(number) or number<=0:raise argparse.ArgumentTypeError('timeout must be positive and finite')
    return number


def execute(root, tests, timeout):
    failed=[]
    for test in tests:
        command=[sys.executable]+(['-O'] if sys.flags.optimize else [])+[str(test)]
        try:
            result=subprocess.run(command,cwd=root,timeout=timeout)
            if result.returncode:failed.append({'suite':test.relative_to(root).as_posix(),'reason':'nonzero_exit','exit_code':result.returncode})
        except subprocess.TimeoutExpired:
            failed.append({'suite':test.relative_to(root).as_posix(),'reason':'timeout'})
    return failed


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,type=Path);p.add_argument('--models-dir',required=True)
    p.add_argument('--expected-suites',required=True,type=Path);p.add_argument('--run',action='store_true')
    p.add_argument('--timeout',type=positive_timeout,default=60.0)
    a=p.parse_args()
    try:tests=select(a.root,a.models_dir,json.loads(a.expected_suites.read_text()))
    except (ValueError,TypeError,OSError):print('ERROR: invalid or mismatched model selection',file=sys.stderr);return 1
    root=a.root.resolve()
    if not a.run:
        print(json.dumps({'status':'selected_not_executed','suites':[x.relative_to(root).as_posix() for x in tests]}));return 0
    failed=execute(root,tests,a.timeout)
    print(json.dumps({'status':'model_suites_finished','suites':len(tests),'failed':failed,'scope':'Selected teaching models only, not engine QA'}))
    return int(bool(failed))

if __name__=='__main__':raise SystemExit(main())
