"""Fresh-root parent. Writing this file does not authorize execution."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    # Never overwrite an old invocation, including its PASS or failed evidence.
    if len(sys.argv) != 2:
        print('REJECTED: one fresh output directory required')
        return 1
    output = Path(sys.argv[1]).absolute()
    if '..' in output.parts or any(p.is_symlink() for p in (output, *output.parents)):
        print('REJECTED: output path')
        return 1
    try:
        output.mkdir(parents=False, exist_ok=False)
    except Exception:
        print('REJECTED: output must be new')
        return 1
    work = output / 'owned-work'
    receipt = {'schema': 1, 'status': 'FAILED_OR_INCOMPLETE',
               'input_hashes_before': None, 'input_hashes_after': None,
               'native_spawn_attempts': 0, 'native_children_started': 0,
               'child_exit': None, 'timed_out': False, 'cleanup_complete': False,
               'environment_validated': False, 'stderr_empty': False, 'stdout_sha256': None}
    succeeded = False
    proc = None
    out = b''
    err = b''
    checker = None
    termination_confirmed = True  # no launch attempted yet
    try:
        if sys.flags.optimize:
            raise RuntimeError('optimized parent rejected before imports or spawn')
        if sys.version_info < (3, 12):
            raise RuntimeError('Python 3.12 or newer required')
        checker = load('reviewed_checker', ROOT / 'checker.py')
        manifest = checker.parse((ROOT / 'INPUT-MANIFEST.json').read_bytes())
        before = checker.source_hashes(ROOT)
        receipt['input_hashes_before'] = before
        checker.require(checker.exact(manifest, before), 'source_manifest')
        isolation = load('reviewed_isolation', ROOT / 'isolation.py')
        work.mkdir(exist_ok=False)
        runtime = work / 'runtime'
        runtime.mkdir(exist_ok=False)
        env, selected = isolation.prepare_environment({'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, runtime)
        isolation.validate_environment(env, runtime)
        checker.require(all(not any(Path(p).iterdir()) for p in selected.values()), 'runtime_not_empty')
        receipt['environment_validated'] = True
        # Runtime dirs validated immediately before this single launch.
        receipt['native_spawn_attempts'] = 1
        receipt['native_children_started'] = None  # unknown until Popen returns
        termination_confirmed = False
        proc = subprocess.Popen([sys.executable, '-I', '-B', str(ROOT / 'child.py'), str(work / 'observation.sqlite')],
                                cwd=work, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        receipt['native_children_started'] = 1
        try:
            out, err = proc.communicate(timeout=15)
            termination_confirmed = proc.returncode is not None
        except subprocess.TimeoutExpired as exc:
            receipt['timed_out'] = True
            out, err = exc.output or b'', exc.stderr or b''
            raise
        receipt['child_exit'] = proc.returncode
        receipt['stderr_empty'] = err == b''
        checker.require(not receipt['timed_out'] and proc.returncode == 0 and not err, 'child_terminal')
        checker.validate_observation(checker.parse(out), before['child.py'])
        succeeded = True
    except BaseException:
        with (output / 'parent-error.internal.txt').open('w', encoding='utf-8') as handle:
            traceback.print_exc(file=handle)
    finally:
        if proc is not None and not termination_confirmed:
            succeeded = False
            try:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)  # only newly owned group
                except ProcessLookupError:
                    pass
                out, err = proc.communicate(timeout=5)
                termination_confirmed = proc.returncode is not None
                receipt['child_exit'] = proc.returncode
            except subprocess.TimeoutExpired as exc:
                out, err = exc.output or out, exc.stderr or err
                # A terminal leader alone does not establish pipe/descendant closure.
                termination_confirmed = False
            except BaseException:
                termination_confirmed = False
            finally:
                if not termination_confirmed:
                    for pipe in (proc.stdout, proc.stderr):
                        if pipe is not None:
                            pipe.close()
        # Raw unexpected diagnostics are internal until explicit privacy review.
        (output / 'stdout.json').write_bytes(out)
        (output / 'stderr.internal.txt').write_bytes(err)
        receipt['stdout_sha256'] = hashlib.sha256(out).hexdigest()
        try:
            if checker is not None:
                receipt['input_hashes_after'] = checker.source_hashes(ROOT)
                if not checker.exact(receipt['input_hashes_before'], receipt['input_hashes_after']):
                    succeeded = False
            if termination_confirmed:
                if work.exists():
                    shutil.rmtree(work)
                receipt['cleanup_complete'] = not work.exists()
            else:
                # Preserve owned work when termination cannot be established.
                succeeded = False
                receipt['cleanup_complete'] = False
        except BaseException:
            succeeded = False
            with (output / 'cleanup-error.internal.txt').open('w', encoding='utf-8') as handle:
                traceback.print_exc(file=handle)
        if succeeded and receipt['cleanup_complete']:
            receipt['status'] = 'PASS'
        (output / 'result.json').write_text(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(receipt['status'])
    return 0 if receipt['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
