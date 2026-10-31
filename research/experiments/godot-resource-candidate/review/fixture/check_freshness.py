"""Run only two pre-engine rejection paths in isolated copies; no engine execution."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'freshness-results'
OUT.mkdir(exist_ok=True)
results = []
for label in ('optimized', 'missing-engine'):
    with tempfile.TemporaryDirectory(prefix='resource-freshness-') as td:
        root = Path(td)
        for name in ('run.py', 'contract.json'):
            shutil.copyfile(ROOT / name, root / name)
        out = root / 'results'; out.mkdir()
        (out / 'summary.json').write_text('{"status":"PASS","invocation_id":"old-sentinel"}\n')
        env = dict(os.environ, GODOT_BIN=str(root / 'does-not-exist'))
        cmd = [sys.executable, '-B', *(['-O'] if label == 'optimized' else []), str(root / 'run.py')]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=10)
        receipt = json.loads((out / 'invocation.json').read_text())
        cleared = not (out / 'summary.json').exists()
        if p.returncode == 0 or not cleared or receipt['status'] != 'FAILED' or receipt['engine_processes_started'] != 0:
            raise RuntimeError('pre-engine rejection failed: ' + label)
        reason = 'Refusing optimized mode' if label == 'optimized' else 'engine does not exist'
        if reason not in receipt['error']:
            raise RuntimeError('unexpected rejection: ' + label)
        (OUT / (label + '.stdout.txt')).write_text(p.stdout)
        (OUT / (label + '.stderr.txt')).write_text(p.stderr)
        result = {'case': label, 'returncode': p.returncode, 'old_summary_removed': cleared,
                  'receipt': receipt, 'command': cmd}
        (OUT / (label + '.json')).write_text(json.dumps(result, indent=2) + '\n')
        results.append(result)
(OUT / 'summary.json').write_text(json.dumps({'cases': results, 'run_py_sha256': hashlib.sha256((ROOT/'run.py').read_bytes()).hexdigest(), 'engine_runs': 0}, indent=2) + '\n')
print('PASS: 2 isolated pre-engine failures remove old summary and record failed invocation')
