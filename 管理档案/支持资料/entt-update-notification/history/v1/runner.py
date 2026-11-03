"""One authorized attempt only. No automatic retry. Logs are local pending review."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
BASE = Path(__file__).resolve().parent
HEADER = BASE/'source/entt.hpp'
HEADER_SHA = '31be51708c7325ecb7877182fa9ee68a20fb2121ce6bcd6c1687506f0fb1c8b5'
FILES = ('PROTOCOL.md','fixture.cpp','checker.py','expected.json','runner.py','source/LICENSE')
KEYS = ('HOME','TMPDIR','XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME')
def digest(data): return hashlib.sha256(data).hexdigest()
def identities():
    return {**{name:digest((BASE/name).read_bytes()) for name in FILES},'source/entt.hpp':digest(HEADER.read_bytes())}
def stop_group(child):
    errors = []
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try: os.killpg(child.pid, sig)
        except ProcessLookupError: pass
        except Exception as exc: errors.append(type(exc).__name__)
    try: child.wait(timeout=3)
    except Exception as exc: errors.append(type(exc).__name__)
    return errors
def command(argv, timeout, root, env, label, receipt):
    record = {'argv':argv,'timeout_seconds':timeout,'status':'pending'}
    receipt['processes'].append(record)
    child = None
    out = err = b''
    failure = None
    try:
        for key in KEYS:
            p = root/label/key
            if env[key] != str(p) or not p.is_dir() or p.is_symlink() or any(p.iterdir()):
                raise ValueError('environment precondition')
        child = subprocess.Popen(argv, cwd=root, env=env, stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        out, err = child.communicate(timeout=timeout)
        record['returncode'] = child.returncode
        if child.returncode != 0: raise ValueError('nonzero process')
        if err or (label == 'build' and out): raise ValueError('unreviewed diagnostics')
        record['status'] = 'returned_zero'
    except BaseException as exc:
        failure = exc
        record['status'] = 'failed'
        record['error_type'] = type(exc).__name__
        if isinstance(exc, subprocess.TimeoutExpired):
            out, err = exc.output or b'', exc.stderr or b''
    finally:
        if child is not None:
            cleanup = stop_group(child)
            if cleanup:
                record['cleanup_errors'] = cleanup
                if failure is None: failure = RuntimeError('cleanup incomplete')
        for suffix, data in (('stdout',out),('stderr',err)):
            record[suffix+'_sha256'] = digest(data)
            record[suffix+'_bytes'] = len(data)
            try: (root/(label+'.'+suffix)).write_bytes(data)
            except BaseException as exc:
                record.setdefault('finalization_errors',[]).append(type(exc).__name__)
                if failure is None: failure = exc
    if failure is not None: raise failure
    return out, err
def environment(root, label):
    parent = root/label
    parent.mkdir()
    env = {'PATH':os.defpath,'LANG':'C','LC_ALL':'C'}
    for key in KEYS:
        p = parent/key
        p.mkdir()
        env[key] = str(p)
    return env
def main():
    if len(sys.argv) != 2: raise ValueError('one fresh output directory required')
    root = Path(sys.argv[1]).absolute()
    if any(p.is_symlink() for p in (root,*root.parents)): raise ValueError('symlink root')
    root.mkdir(exist_ok=False)
    receipt = {'schema':1,'status':'failed','processes':[],'scope':'one input, three independent registries'}
    primary = None
    before = None
    try:
        if sys.flags.optimize: raise ValueError('optimized runner rejected')
        manifest = json.loads((BASE/'INPUT-MANIFEST.json').read_text())
        before = identities()
        if before != manifest or before['source/entt.hpp'] != HEADER_SHA: raise ValueError('input identity')
        receipt['input_hashes'] = before
        (root/'source').mkdir()
        for name in FILES: shutil.copyfile(BASE/name,root/name)
        shutil.copyfile(HEADER,root/'source/entt.hpp')
        if any(digest((root/name).read_bytes()) != value for name,value in before.items()):
            raise ValueError('copy identity')
        compiler = shutil.which('c++',path=os.defpath)
        if compiler is None: raise ValueError('compiler unavailable')
        # argv uses PATH-selected c++; no compiler version or extra capability probe.
        command(['c++','-std=c++17','-O0','-Wall','-Wextra','-pedantic','-Isource','fixture.cpp','-o','fixture'],
                60,root,environment(root,'build'),'build',receipt)
        out,err = command(['./fixture'],10,root,environment(root,'native'),'native',receipt)
        # Frozen copied checker is imported only after input binding.
        import importlib.util
        spec = importlib.util.spec_from_file_location('finite_checker',root/'checker.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        receipt['consumer'] = module.validate(out,err,root/'expected.json')
    except BaseException as exc:
        primary = exc
        receipt['error_type'] = type(exc).__name__
    finally:
        try:
            after = identities()
            receipt['input_hashes_after'] = after
            if before is None or after != before: raise ValueError('input changed')
            if any(digest((root/name).read_bytes()) != value for name,value in before.items()):
                raise ValueError('copied input changed')
        except BaseException as exc:
            receipt['after_check_error'] = type(exc).__name__
            if primary is None: primary = exc
    if primary is None: receipt['status'] = 'pass'
    # Close pending file successfully before publishing the canonical receipt.
    pending = root/'receipt.pending.json'
    with pending.open('x',encoding='utf-8') as handle:
        json.dump(receipt,handle,ensure_ascii=False,indent=2,allow_nan=False)
        handle.write('\n')
    pending.replace(root/'receipt.json')
    if primary is not None: raise primary
    print('PASS: three finite cases; require receipt and external exit 0')
if __name__ == '__main__':
    try: main()
    except BaseException as exc:
        print('STOP: '+type(exc).__name__,file=sys.stderr)
        sys.exit(1)
