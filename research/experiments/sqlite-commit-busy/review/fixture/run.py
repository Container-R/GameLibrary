import base64
import hashlib
import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    output = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else ROOT / 'results'
    output.mkdir(parents=True, exist_ok=True)
    out = output / str(uuid.uuid4()); out.mkdir()
    record = dict(invocation_id=out.name, started_utc=datetime.now(timezone.utc).isoformat(),
                  status='STARTED', platform=platform.platform(), python=sys.version,
                  executable=str(pathlib.Path(sys.executable).resolve()),
                  executable_sha256=sha(pathlib.Path(sys.executable).resolve()),
                  source_sha256={p: sha(ROOT / p) for p in ('run.py', 'worker.py', 'protocol.md')},
                  processes=[])
    def save():
        (out / 'summary.json').write_text(json.dumps(record, indent=2) + '\n')
    save()
    try:
        with tempfile.TemporaryDirectory(prefix='sqlite-commit-busy-') as tmp:
            db = pathlib.Path(tmp) / 'ledger.db'
            for role in ('scenario', 'observe'):
                command = [sys.executable, '-B', str(ROOT / 'worker.py'), role, str(db)]
                if sys.flags.optimize:
                    command.insert(1, '-O')
                try:
                    p = subprocess.run(command, capture_output=True, timeout=10)
                except subprocess.TimeoutExpired as e:
                    (out / (role + '.stdout')).write_bytes(e.stdout or b'')
                    (out / (role + '.stderr')).write_bytes(e.stderr or b'')
                    record['processes'].append(dict(command=command, timed_out=True))
                    raise
                (out / (role + '.stdout')).write_bytes(p.stdout)
                (out / (role + '.stderr')).write_bytes(p.stderr)
                record['processes'].append(dict(command=command, exit_code=p.returncode, timed_out=False))
                if p.returncode:
                    raise RuntimeError(role + ' failed')
                rows = [json.loads(line) for line in p.stdout.splitlines()]
                expected = 'scenario_pass' if role == 'scenario' else 'independent_read_pass'
                if not rows or rows[-1].get('kind') != expected:
                    raise RuntimeError('missing terminal result')
                (out / (role + '.json')).write_text(json.dumps(rows, indent=2) + '\n')
            raw = db.read_bytes()
            (out / 'ledger.db.base64').write_text(base64.b64encode(raw).decode() + '\n')
            record['database'] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()).copy()
        record['status'] = 'PASS'
    except BaseException as e:
        record['status'] = 'FAIL'; record['error'] = repr(e)
        raise
    finally:
        record['outputs_sha256'] = {p.name: sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != 'summary.json'}
        save(); print(json.dumps(dict(output=str(out), status=record['status'])), flush=True)

if __name__ == '__main__':
    main()
