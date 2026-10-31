"""Six isolated -O rejection probes; never run the engine or mutate archives."""
import ast
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

NAMES = ('godot-fixed-step', 'godot-pause-input', 'godot-focus-boundary',
         'godot-import-boundary', 'godot-navigation-sync', 'godot-animation-events')
SENTINEL = b'{"status":"PASS","audit_sentinel":"historical-not-current"}\n'
def digest(data):
    return hashlib.sha256(data).hexdigest()
def gate_check(data):
    """Fail closed unless the first executable statement is the reviewed rejection."""
    tree = ast.parse(data)
    nodes = list(tree.body)
    if nodes and isinstance(nodes[0], ast.Expr) and isinstance(nodes[0].value, ast.Constant) and isinstance(nodes[0].value.value, str):
        nodes.pop(0)
    while nodes and isinstance(nodes[0], (ast.Import, ast.ImportFrom)):
        node = nodes.pop(0)
        modules = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module]
        if any(m not in {'hashlib','json','os','pathlib','platform','re','shutil','subprocess','sys','tempfile','time','math'} for m in modules):
            raise ValueError('Unreviewed import')
    gate = nodes[0]
    expected = {'sys.flags.optimize', 'not __debug__'}
    if not (isinstance(gate, ast.If) and ast.unparse(gate.test) in expected and not gate.orelse
            and len(gate.body) == 1 and isinstance(gate.body[0], ast.Raise)
            and isinstance(gate.body[0].exc, ast.Call)
            and isinstance(gate.body[0].exc.func, ast.Name)
            and gate.body[0].exc.func.id in {'RuntimeError','SystemExit'}
            and len(gate.body[0].exc.args) == 1 and isinstance(gate.body[0].exc.args[0], ast.Constant)
            and not gate.body[0].exc.keywords):
        raise ValueError('Rejection gate changed; refuse execution')
    return gate.lineno

def main():
    root = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    if out == root or root in out.parents:
        raise ValueError('Output must be outside archive')
    out.mkdir(parents=True, exist_ok=True)
    receipt = {'date_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'python': platform.python_version(), 'executable': sys.executable,
               'platform': platform.platform(), 'audit_source_sha256': digest(Path(__file__).read_bytes()),
               'scope': 'Six current run.py copies only; -O rejection, no engine invocation', 'cases': []}
    for name in NAMES:
        source = root/'research/experiments'/name/'run.py'
        data = source.read_bytes()
        line = gate_check(data)
        with tempfile.TemporaryDirectory(prefix='runner-rejection-') as temp:
            fixture = Path(temp)
            (fixture/'run.py').write_bytes(data)
            (fixture/'results').mkdir()
            summary = fixture/'results/summary.json'
            summary.write_bytes(SENTINEL)
            # No project/GDScript/assets/binary copied. Guard is checked before execution.
            command = [sys.executable, '-I', '-B', '-O', str(fixture/'run.py')]
            env = dict(os.environ, PATH='')
            p = subprocess.run(command, cwd=fixture, env=env, capture_output=True, timeout=10)
            stdout = f'{name}.stdout.txt'; stderr = f'{name}.stderr.txt'
            (out/stdout).write_bytes(p.stdout); (out/stderr).write_bytes(p.stderr)
            after = summary.read_bytes() if summary.exists() else None
            files = sorted(str(f.relative_to(fixture)) for f in fixture.rglob('*') if f.is_file())
            case = {'fixture': name, 'source': str(source.relative_to(root)), 'source_sha256': digest(data),
                    'guard_line': line, 'command': command, 'returncode': p.returncode,
                    'stdout_path': stdout, 'stderr_path': stderr,
                    'stdout_sha256': digest(p.stdout), 'stderr_sha256': digest(p.stderr),
                    'sentinel_before_sha256': digest(SENTINEL),
                    'sentinel_after_sha256': digest(after) if after is not None else None,
                    'sentinel_unchanged': after == SENTINEL, 'temporary_files_after': files,
                    'source_unchanged': source.read_bytes() == data}
            if p.returncode != 1 or p.stdout or after != SENTINEL or not case['source_unchanged']:
                raise RuntimeError(case)
            receipt['cases'].append(case)
    (out/'results.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print('6/6 rejected with exit 1; six historical PASS sentinels unchanged; no engine runs')

if __name__ == '__main__':
    main()
