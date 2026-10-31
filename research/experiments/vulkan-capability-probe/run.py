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
def group_exists(pid):
    try: os.killpg(pid, 0); return True
    except ProcessLookupError: return False

def terminate_group(proc, receipt):
    for sig in (signal.SIGTERM, signal.SIGKILL):
        if not group_exists(proc.pid): break
        attempt = {'signal': sig.name}
        try: os.killpg(proc.pid, sig); attempt['sent'] = True
        except ProcessLookupError: attempt['sent'] = False
        receipt['termination_attempts'].append(attempt)
        try: proc.wait(timeout=2)
        except subprocess.TimeoutExpired: pass
    receipt['group_remaining'] = group_exists(proc.pid)

def main(output_parent):
    if platform.system() != 'Linux': raise RuntimeError('Linux process-group wrapper only')
    invocation = str(uuid.uuid4())
    parent = Path(output_parent).resolve(strict=True)
    out = parent / invocation; out.mkdir()
    receipt = {'uuid': invocation, 'state': 'STARTED', 'started_utc': now(), 'parent_pid': os.getpid(),
               'python': sys.executable, 'python_version': sys.version, 'platform': platform.platform(),
               'source_root':str(ROOT), 'timeout': False, 'termination_attempts': [], 'returncode':None}
    save(out/'receipt.json', receipt)
    started = time.monotonic(); proc = None
    for name in ('stdout.txt','stderr.txt'): (out/name).touch(exist_ok=False)
    phase = 'pins'
    try:
        manifest = strict((ROOT / 'source-manifest.json').read_text())
        receipt['source_sha256'] = manifest
        for name, sha in manifest.items():
            if Path(name).name != name or digest(ROOT / name) != sha: raise RuntimeError('source pin mismatch')
        if digest(ROOT / 'protocol.json') != PROTOCOL or digest(ROOT / 'isolation.py') != HELPER:
            raise RuntimeError('protocol/helper pin mismatch')
        phase = 'environment'
        with tempfile.TemporaryDirectory(prefix='vulkan-capability-') as temp:
            base = {'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C', 'XDG_CONFIG_DIRS':'/etc/xdg','XDG_DATA_DIRS':'/usr/local/share:/usr/share'}
            env, mapping = prepare_environment(base, temp)
            validate_environment(env, temp)
            receipt.update(base_environment=base, isolation=mapping, owned_runtime_root=temp)
            command = [sys.executable, str(ROOT/'child.py'), invocation]
            receipt['argv'] = command
            phase = 'spawn'
            with (out/'stdout.txt').open('wb') as stdout, (out/'stderr.txt').open('wb') as stderr:
                proc = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, cwd=temp, start_new_session=True)
                receipt['child_pid'] = proc.pid; save(out/'receipt.json', receipt)
                phase = 'wait'
                try: proc.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    receipt['timeout'] = True
                    terminate_group(proc, receipt)
                receipt['returncode'] = proc.poll()
                if not receipt['timeout']:
                    receipt['group_remaining'] = group_exists(proc.pid)
                    if receipt['group_remaining']:
                        receipt['unexpected_descendants'] = True
                        terminate_group(proc, receipt)
            receipt['category'] = 'TIMEOUT' if receipt['timeout'] else 'CHILD_CRASH'
            if receipt.get('unexpected_descendants'):
                receipt['category'] = 'PROTOCOL_ANOMALY'
            elif receipt['returncode'] == 0 and not receipt['timeout']:
                try:
                    events = [strict(line) for line in (out/'stdout.txt').read_text().splitlines()]
                    receipt['category'] = events[-1]['value']['category']
                except (ValueError, KeyError, IndexError): receipt['category'] = 'PROTOCOL_ANOMALY'
    except Exception as exc:
        import traceback
        receipt.update(category={'pins':'SOURCE_PIN_MISMATCH','environment':'ENVIRONMENT_SETUP_FAILED'}.get(phase,'PYTHON_EXCEPTION'),
                       exception_phase=phase, exception=str(exc), traceback=traceback.format_exc())
        if proc is not None:
            terminate_group(proc, receipt); receipt['returncode'] = proc.poll()
    finally:
        receipt.update(finished_utc=now(), elapsed_seconds=time.monotonic()-started, state='COMPLETE')
        receipt['output_sha256'] = {name:digest(out/name) for name in ('stdout.txt','stderr.txt')}
        try: receipt['source_after_sha256'] = {name:digest(ROOT/name) for name in receipt.get('source_sha256',{})}
        except OSError as exc: receipt['source_after_unavailable'] = str(exc)
        if receipt.get('source_after_sha256') != receipt.get('source_sha256'):
            receipt.update(prior_category=receipt.get('category'),category='SOURCE_PIN_MISMATCH')
        save(out/'receipt.json', receipt)
    consistent = False
    if receipt['returncode'] == 0 and not receipt['timeout'] and not receipt.get('unexpected_descendants') and 'exception' not in receipt:
        try:
            category = consume(out, ROOT, invocation); consistent = True
            save(out/'consistency.json', {'category':category, 'consistent':True, 'not_execution_authentication':True})
        except Exception as exc:
            receipt.update(prior_category=receipt['category'],category='PROTOCOL_ANOMALY', consumer_error=str(exc)); save(out/'receipt.json', receipt)
    print(json.dumps({'output':str(out), 'category':receipt['category'], 'archive_consistent':consistent}))
    return 0 if consistent else 1

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument('--output-parent', required=True)
    raise SystemExit(main(parser.parse_args().output_parent))
