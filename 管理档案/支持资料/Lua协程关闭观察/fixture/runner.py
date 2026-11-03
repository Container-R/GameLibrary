#!/usr/bin/env python3
"""Finite local fixture. Requires separate approval before execution."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tarfile

INPUTS = {'lua-5.4.8.tar.gz', 'case.lua', 'PROTOCOL.md', 'runner.py'}
ARCHIVE_SHA = '4f18ddae154e793e46eeab727c59ef1c0c0c2b744e7b94219710d76f530629ae'
C_SOURCES = '''lapi.c lcode.c lctype.c ldebug.c ldo.c ldump.c lfunc.c lgc.c llex.c lmem.c lobject.c lopcodes.c lparser.c lstate.c lstring.c ltable.c ltm.c lundump.c lvm.c lzio.c lauxlib.c lbaselib.c lcorolib.c ldblib.c liolib.c lmathlib.c loadlib.c loslib.c lstrlib.c ltablib.c lutf8lib.c linit.c lua.c'''.split()
HEADERS = '''lapi.h lauxlib.h lcode.h lctype.h ldebug.h ldo.h lfunc.h lgc.h ljumptab.h llex.h llimits.h lmem.h lobject.h lopcodes.h lopnames.h lparser.h lprefix.h lstate.h lstring.h ltable.h ltm.h lua.h luaconf.h lualib.h lundump.h lvm.h lzio.h'''.split()
FLAGS = ['-std=c99', '-O2', '-Wall', '-Wextra', '-DLUA_COMPAT_5_3']
EXPECTED = b'''normal|yield|n=2|ok=true|value=waiting|state=suspended|closes=0|events=enter
normal|finish|n=2|ok=true|value=done|state=dead|closes=1|close_error_nil=true|events=enter,after-yield,close
close|yield|n=2|ok=true|value=waiting|state=suspended|closes=0|events=enter
close|finish|n=1|ok=true|state=dead|closes=1|close_error_nil=true|events=enter,close
error|yield|n=2|ok=true|value=waiting|state=suspended|closes=0|events=enter
error|resume-error|n=2|ok=false|error_identity=true|state=dead|closes=0|events=enter,before-error
error|finish|n=2|ok=false|error_identity=true|state=dead|closes=1|close_error_identity=true|events=enter,before-error,close
'''

def sha(data):
    return hashlib.sha256(data).hexdigest()

def no_links(path):
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('symlink_rejected')

def directory(path, existing=False):
    no_links(path)
    path.mkdir(mode=0o700, exist_ok=existing)
    if not path.is_dir() or path.stat().st_mode & 0o777 != 0o700:
        raise ValueError('directory_mode_rejected')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-name', required=True)
    args = ap.parse_args()
    if os.name != 'posix' or not re.fullmatch('[a-z][a-z0-9-]{0,39}', args.run_name):
        raise SystemExit('unsupported_platform_or_name')
    script = Path(os.path.abspath(__file__))
    no_links(script)
    root = script.parent
    mp = root / 'manifest.json'
    no_links(mp)
    raw = mp.read_bytes()
    manifest = json.loads(raw)
    if set(manifest['inputs']) != INPUTS:
        raise SystemExit('input_set_mismatch')
    originals = {}
    for name, digest in manifest['inputs'].items():
        p = root / name
        no_links(p)
        if not p.is_file():
            raise SystemExit('input_type_mismatch')
        originals[name] = p.read_bytes()
        if sha(originals[name]) != digest:
            raise SystemExit('input_hash_mismatch')
    if sha(originals['lua-5.4.8.tar.gz']) != ARCHIVE_SHA or len(originals['lua-5.4.8.tar.gz']) != 374332:
        raise SystemExit('release_identity_mismatch')
    directory(root / 'runs', True)
    run = root / 'runs' / args.run_name
    directory(run)
    result = {'status': 'failed', 'stage': 'preparation',
              'manifest_sha256': sha(raw), 'inputs_sha256': manifest['inputs'],
              'copied_inputs_verified': False, 'environment_prepared': False,
              'compile_returncode': None, 'run_returncode': None,
              'compile_options': FLAGS + ['-lm'],
              'scope': 'Three original table/event coroutine cases only; no game or host resource execution'}
    def save():
        (run / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    save()
    try:
        work, logs, envroot = run / 'work', run / 'private-logs', run / 'environment'
        for path in (work, logs, envroot):
            directory(path)
        for name, data in originals.items():
            (work / name).write_bytes(data)
        if any(sha((work / n).read_bytes()) != h for n, h in manifest['inputs'].items()):
            raise ValueError('copy_hash_mismatch')
        result['copied_inputs_verified'] = True
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8', 'TZ': 'UTC'}
        for key in ('HOME', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME', 'XDG_STATE_HOME', 'XDG_RUNTIME_DIR', 'XDG_CONFIG_DIRS', 'XDG_DATA_DIRS', 'TMPDIR', 'TMP', 'TEMP'):
            path = envroot / key.lower()
            directory(path)
            probe = path / 'write-check'
            probe.write_bytes(b'check')
            probe.unlink()
            env[key] = str(path)
        result['environment_prepared'] = True
        src = work / 'src'
        directory(src)
        # Do not use extractall: archive paths cannot choose output locations.
        with tarfile.open(work / 'lua-5.4.8.tar.gz', 'r:gz') as archive:
            members = archive.getmembers()
            for name in C_SOURCES + HEADERS:
                matches = [m for m in members if m.name == 'lua-5.4.8/src/' + name]
                if len(matches) != 1 or not matches[0].isfile() or not 0 < matches[0].size <= 1000000:
                    raise ValueError('source_member_rejected')
                data = archive.extractfile(matches[0]).read()
                if len(data) != matches[0].size:
                    raise ValueError('source_member_truncated')
                (src / name).write_bytes(data)
        result['source_members_verified'] = True
        save()
        def invoke(command, label, seconds):
            with (logs / (label + '-stdout.txt')).open('wb') as out, (logs / (label + '-stderr.txt')).open('wb') as err:
                proc = subprocess.Popen(command, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                        stdout=out, stderr=err, start_new_session=True)
                try:
                    code = proc.wait(timeout=seconds)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    finally:
                        proc.wait()
                    raise
            result[label + '_stdout_empty'] = (logs / (label + '-stdout.txt')).stat().st_size == 0
            result[label + '_stderr_empty'] = (logs / (label + '-stderr.txt')).stat().st_size == 0
            return code
        result['stage'] = 'compile'
        save()
        result['compile_returncode'] = invoke(['cc'] + FLAGS + ['src/' + n for n in C_SOURCES] + ['-o', 'lua-local', '-lm'], 'compile', 120)
        if result['compile_returncode'] != 0:
            result['failure_kind'] = 'compile_exit'
            return 1
        result['compile_diagnostics_require_review'] = (
            not result['compile_stdout_empty'] or not result['compile_stderr_empty'])
        binary = work / 'lua-local'
        no_links(binary)
        if not binary.is_file():
            raise ValueError('missing_binary')
        result['stage'] = 'run'
        save()
        result['run_returncode'] = invoke(['./lua-local', '-E', 'case.lua'], 'run', 5)
        if result['run_returncode'] != 0:
            result['failure_kind'] = 'run_exit'
            return 1
        if not result['run_stderr_empty']:
            result['failure_kind'] = 'run_diagnostics'
            return 1
        stdout = (logs / 'run-stdout.txt').read_bytes()
        if stdout != EXPECTED:
            result['failure_kind'] = 'oracle_mismatch'
            return 1
        (run / 'output.txt').write_bytes(stdout)
        result['output_sha256'] = sha(stdout)
        result['output_lines'] = len(stdout.splitlines())
        # Passing means oracle matched, not that unreviewed diagnostics are benign.
        result['status'] = 'passed'
        result['publication_review_required'] = result['compile_diagnostics_require_review']
        result['stage'] = 'complete'
        return 0
    except subprocess.TimeoutExpired:
        result['failure_kind'] = 'timeout'
        return 1
    except Exception:
        result['failure_kind'] = 'preparation_or_output_error'
        return 1
    finally:
        save()

if __name__ == '__main__':
    raise SystemExit(main())
