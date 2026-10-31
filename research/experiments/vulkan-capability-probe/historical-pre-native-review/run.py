"""One explicitly invoked native child. Do not run before source-review approval."""
import datetime
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from consume import digest, strict, consume
from isolation import prepare_environment, validate_environment

ROOT = Path(__file__).resolve().parent
PROTOCOL = '8ec8c5746b1b8280ea0a9acfc1cedc2fb73e2572970675d90db90bfa858a0057'
HELPER = 'bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970'

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path, value): path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def main(output_parent):
    if platform.system() != 'Linux': raise RuntimeError('Linux process-group wrapper only')
    manifest = strict((ROOT / 'source-manifest.json').read_text())
    for name, sha in manifest.items():
        if Path(name).name != name or digest(ROOT / name) != sha: raise RuntimeError('source pin mismatch')
    if digest(ROOT / 'protocol.json') != PROTOCOL or digest(ROOT / 'isolation.py') != HELPER:
        raise RuntimeError('protocol/helper pin mismatch')
    invocation = str(uuid.uuid4())
    parent = Path(output_parent).resolve(strict=True)
    out = parent / invocation; out.mkdir()
    receipt = {'uuid': invocation, 'state': 'STARTED', 'started_utc': now(), 'parent_pid': os.getpid(),
               'python': sys.executable, 'python_version': sys.version, 'platform': platform.platform(),
               'source_sha256': manifest, 'timeout': False, 'termination_attempts': []}
    save(out/'receipt.json', receipt)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='vulkan-capability-') as temp:
        base = {'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C', 'XDG_CONFIG_DIRS':'/etc/xdg','XDG_DATA_DIRS':'/usr/local/share:/usr/share'}
        env, mapping = prepare_environment(base, temp)
        validate_environment(env, temp)
        receipt.update(base_environment=base, isolation=mapping)
        command = [sys.executable, str(ROOT/'child.py'), invocation]
        receipt['argv'] = command
        with (out/'stdout.txt').open('wb') as stdout, (out/'stderr.txt').open('wb') as stderr:
            proc = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, cwd=temp, start_new_session=True)
            receipt['child_pid'] = proc.pid; save(out/'receipt.json', receipt)
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                receipt['timeout'] = True
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    attempt = {'signal': sig.name}
                    try: os.killpg(proc.pid, sig); attempt['sent'] = True
                    except ProcessLookupError: attempt['sent'] = False
                    receipt['termination_attempts'].append(attempt)
                    try: proc.wait(timeout=2); break
                    except subprocess.TimeoutExpired: pass
            receipt['returncode'] = proc.poll()
    receipt.update(finished_utc=now(), elapsed_seconds=time.monotonic()-started)
    receipt['output_sha256'] = {name:digest(out/name) for name in ('stdout.txt','stderr.txt')}
    receipt['state'] = 'COMPLETE'
    receipt['category'] = 'TIMEOUT' if receipt['timeout'] else 'CHILD_CRASH'
    if receipt['returncode'] == 0 and not receipt['timeout']:
        try:
            events = [strict(line) for line in (out/'stdout.txt').read_text().splitlines()]
            receipt['category'] = events[-1]['value']['category']
        except (ValueError, KeyError, IndexError): receipt['category'] = 'PROTOCOL_ANOMALY'
    save(out/'receipt.json', receipt)
    if receipt['returncode'] == 0 and not receipt['timeout']:
        try: category = consume(out, ROOT, invocation)
        except Exception as exc:
            receipt.update(category='PROTOCOL_ANOMALY', consumer_error=str(exc)); save(out/'receipt.json', receipt)
            raise
        save(out/'consistency.json', {'category':category, 'consistent':True, 'not_execution_authentication':True})
    print(json.dumps({'output':str(out), 'category':receipt['category']}))
    return 0 if receipt['returncode'] == 0 and not receipt['timeout'] else 1

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--output-parent', required=True)
    raise SystemExit(main(parser.parse_args().output_parent))
