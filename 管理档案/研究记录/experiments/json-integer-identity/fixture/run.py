"""One authorized Node invocation only. Raw diagnostics remain private until reviewed."""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from consume import source_map, digest, validate_archive, require
from isolation import prepare_environment, validate_environment, KEYS


def group_exists(group):
    try:
        os.killpg(group, 0)
        return True
    except ProcessLookupError:
        return False
    # Permission/other failures are deliberately not treated as absence.


def bounded_stop(process):
    """Only this freshly created session/group. Does not certify escaped descendants."""
    group = process.pid
    for sig in (signal.SIGTERM, signal.SIGKILL):
        if group_exists(group):
            try:
                os.killpg(group, sig)
            except ProcessLookupError:
                pass
        end = time.monotonic() + 2.0
        while time.monotonic() < end:
            process.poll()  # Reap owned leader when available.
            if process.returncode is not None and not group_exists(group):
                return True
            time.sleep(0.05)
    process.poll()
    return process.returncode is not None and not group_exists(group)


def write_receipt(root, receipt):
    # Close must succeed before the canonical record can become PASS.
    # Atomic replacement is not a crash-durability or external-exit guarantee.
    pending = root / 'receipt.pending.json'
    pending.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    pending.replace(root / 'receipt.json')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', required=True, help='Previously approved Node executable, absolute path')
    parser.add_argument('--output', required=True, help='New caller-owned directory; must not exist')
    args = parser.parse_args()
    root = Path(args.output)
    require(root.is_absolute() and '..' not in root.parts, 'output_absolute')
    require(not any(p.is_symlink() for p in (root, *root.parents)), 'output_symlink')
    require(not root.exists(), 'output_reuse')
    root.mkdir(exist_ok=False)  # Parent directory must already exist.
    receipt = dict(schema='json-integer-identity-receipt-v1', status='FAILED_OR_INCOMPLETE',
                   stage='setup', spawn_attempts=0, children_started=0, returncode=None,
                   timed_out=False, termination_confirmed=False, environment_validated=False,
                   error_category=None, inputs_before=None, inputs_after=None,
                   stdout_sha256=None, stderr_sha256=None, secondary_errors=[])
    diagnostics = []

    def fail(error, phase):
        # First cause is immutable even if cleanup or diagnostic persistence fails.
        kind = type(error).__name__
        receipt['status'] = 'FAILED_OR_INCOMPLETE'
        if receipt['error_category'] is None:
            receipt['error_category'] = kind
        else:
            receipt['secondary_errors'].append({'phase': phase, 'category': kind})
        diagnostics.append({'phase': phase, 'category': kind,
                            'trace': ''.join(traceback.format_exception(error))})

    process = None
    stop_attempted = False
    try:
        write_receipt(root, receipt)
        require(not sys.flags.optimize, 'optimized_parent_rejected')
        receipt['inputs_before'] = source_map()
        node = Path(args.node)
        require(node.is_absolute(), 'node_absolute')
        node = node.resolve(strict=True)
        require(node.is_file() and os.access(node, os.X_OK), 'node_unavailable')
        runtime = root / 'runtime'
        runtime.mkdir()
        env, _ = prepare_environment({'LANG': 'C', 'LC_ALL': 'C'}, runtime)
        with (root / 'stdout.txt').open('xb') as stdout, (root / 'stderr.internal.txt').open('xb') as stderr:
            validate_environment(env, runtime)
            require(len({env[k] for k in KEYS}) == 5, 'distinct_runtime_locations')
            require(all(not any(Path(env[k]).iterdir()) for k in KEYS), 'runtime_not_empty')
            receipt['environment_validated'] = True
            receipt['stage'] = 'spawn'
            receipt['spawn_attempts'] = 1
            write_receipt(root, receipt)
            process = subprocess.Popen([str(node), str(HERE / 'observe.mjs')], cwd=runtime,
                                       env=env, stdin=subprocess.DEVNULL, stdout=stdout,
                                       stderr=stderr, start_new_session=True, close_fds=True)
            receipt['children_started'] = 1
            receipt['stage'] = 'running'
            write_receipt(root, receipt)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                receipt['timed_out'] = True
                raise  # Preserve TimeoutExpired before finally attempts termination.
            receipt['returncode'] = process.returncode
            if group_exists(process.pid):
                raise ValueError('remaining_owned_group')
            receipt['termination_confirmed'] = True
        receipt['stage'] = 'collected'
        receipt['inputs_after'] = source_map()
        receipt['stdout_sha256'] = digest((root / 'stdout.txt').read_bytes())
        receipt['stderr_sha256'] = digest((root / 'stderr.internal.txt').read_bytes())
        receipt['status'] = 'PENDING_VALIDATION'
        write_receipt(root, receipt)
        validate_archive(root, allow_pending=True)
        receipt['status'] = 'PASS'
    except Exception as error:
        fail(error, receipt['stage'])
    finally:
        if process is not None:
            try:
                if not receipt['termination_confirmed'] and not stop_attempted:
                    stop_attempted = True
                    receipt['termination_confirmed'] = bounded_stop(process)
                receipt['returncode'] = process.poll()
                require(receipt['termination_confirmed'], 'unconfirmed_termination')
            except Exception as error:
                receipt['termination_confirmed'] = False
                fail(error, 'cleanup')
        try:
            receipt['inputs_after'] = source_map()
            require(receipt['inputs_before'] == receipt['inputs_after'], 'input_changed')
        except Exception as error:
            fail(error, 'final_input_check')
        for filename, key in [('stdout.txt', 'stdout_sha256'), ('stderr.internal.txt', 'stderr_sha256')]:
            try:
                path = root / filename
                if path.is_file():
                    receipt[key] = digest(path.read_bytes())
            except Exception as error:
                fail(error, 'final_output_hash')
        if diagnostics:
            try:
                (root / 'parent-error.internal.txt').write_text(
                    json.dumps(diagnostics, indent=2) + '\n', encoding='utf-8')
            except Exception as error:
                fail(error, 'diagnostic_save')
        try:
            write_receipt(root, receipt)
        except Exception as error:
            fail(error, 'receipt_save')
            # Independent best-effort diagnostic channel, never retry a PASS write.
            try:
                (root / 'terminal-errors.internal.json').write_text(
                    json.dumps(diagnostics, indent=2) + '\n', encoding='utf-8')
            except Exception as save_error:
                fail(save_error, 'fallback_diagnostic_save')
        # Never remove work. If storage is failing, the safe terminal line is a last channel.
    print(json.dumps({'status': receipt['status'], 'error_category': receipt['error_category'],
                      'secondary_errors': receipt['secondary_errors']}))
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        print('FAILED_OR_INCOMPLETE: startup or receipt failure', file=sys.stderr)
        raise SystemExit(1)
