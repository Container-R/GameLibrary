"""One bounded numeric child. No retry, no ordinary audio device."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import importlib.util

class Rejected(Exception):
    pass

FILES = ('PROTOCOL.md','driver.py','runner.py','consumer.py','contract.py','isolation.py','alsoft.conf')
EXTRA = ('XDG_CONFIG_DIRS', 'XDG_DATA_DIRS', 'XDG_STATE_HOME', 'XDG_RUNTIME_DIR')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def strict_json(data):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise Rejected('duplicate_json_key')
            out[k] = v
        return out
    def bad(value):
        raise Rejected('nonfinite_json')
    return json.loads(data.decode('utf-8', 'strict'), object_pairs_hook=pairs, parse_constant=bad)


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}', sys.argv[1]):
        raise SystemExit('usage: runner.py fresh-run-name')
    base = Path(__file__).absolute().parent
    # Resolve is intentionally not used before ancestor symlink rejection.
    for p in (base, *base.parents):
        if p.is_symlink(): raise SystemExit('symlink_fixture')
    manifest_bytes = (base / 'INPUT-SHA256.json').read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    expected = strict_json(manifest_bytes)
    if set(expected) != set(FILES) or any(type(v) is not str or not re.fullmatch('[0-9a-f]{64}',v) for v in expected.values()):
        raise SystemExit('invalid_input_manifest')
    if {n:digest(base/n) for n in FILES} != expected:
        raise SystemExit('input_hash_mismatch')
    spec = importlib.util.spec_from_file_location('capability_isolation', base/'isolation.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    prepare_environment, validate_environment = helper.prepare_environment, helper.validate_environment
    spec = importlib.util.spec_from_file_location('numeric_consumer', base/'consumer.py')
    consumer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(consumer)
    root = base / ('run-' + sys.argv[1])
    root.mkdir(mode=0o700, exist_ok=False)
    private = root / 'private'; private.mkdir(mode=0o700)
    state = {'schema':1,'status':'FAIL','termination_confirmed':False,'input_postcheck':False,
             'configuration_isolation':'selected_user_locations_only_system_and_executable_config_not_excluded',
             'configuration_fully_excluded':False, 'input_manifest_sha256':manifest_sha256,
             'manifest_postcheck':False, 'cleanup_failure':[]}
    child = None
    cleanup_attempted = False
    out = err = b''
    try:
        env, _ = prepare_environment({'LANG':'C','LC_ALL':'C','ALSOFT_DRIVERS':'null'}, root)
        for key in EXTRA:
            path = root/key; path.mkdir(mode=0o700, exist_ok=False); env[key] = str(path)
        env['TMP'] = env['TEMP'] = env['TMPDIR']
        conf = root/'alsoft.conf'; conf.write_bytes((base/'alsoft.conf').read_bytes())
        env['ALSOFT_CONF'] = str(conf)
        validate_environment(env, root)
        for key in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR',*EXTRA):
            p = root/key
            if env[key] != str(p) or p.is_symlink() or not p.is_dir():
                raise Rejected('environment_directory')
            probe=p/'write-check'; probe.write_bytes(b'check'); probe.unlink()
        if env['TMP'] != env['TMPDIR'] or env['TEMP'] != env['TMPDIR'] or conf.is_symlink() or digest(conf) != expected['alsoft.conf']:
            raise Rejected('environment_mapping')
        if set(env) != {'LANG','LC_ALL','ALSOFT_DRIVERS','HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR',*EXTRA,'TMP','TEMP','ALSOFT_CONF'}:
            raise Rejected('environment_allowlist')
        child = subprocess.Popen([sys.executable,'-I','-B',str(base/'driver.py')],cwd=root,env=env,
                                 stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                 start_new_session=True)
        try:
            out, err = child.communicate(timeout=15)
        except subprocess.TimeoutExpired as exc:
            out, err = exc.output or b'', exc.stderr or b''
            state.setdefault('failure_reason', 'child_timeout')
            cleanup_attempted = True
            try:
                child.kill()
            except BaseException:
                state['cleanup_failure'].append('kill_exception')
            try:
                out, err = child.communicate(timeout=2)
            except subprocess.TimeoutExpired as cleanup_exc:
                out = cleanup_exc.output if cleanup_exc.output is not None else out
                err = cleanup_exc.stderr if cleanup_exc.stderr is not None else err
                state['cleanup_failure'].append('reap_timeout')
            except BaseException:
                state['cleanup_failure'].append('reap_exception')
            raise Rejected('child_timeout')
        finally:
            state['termination_confirmed'] = child.poll() is not None
        state['returncode'] = child.returncode
        report = consumer.consume(out)
        state['observation'] = report
        if child.returncode != 0 or err or report['status'] != 'PASS':
            raise Rejected('child_or_cleanup_failure')
        state['status'] = report['status']  # finite five-case numeric observation only
    except BaseException as exc:
        state['status'] = 'FAIL'
        state['failure_category'] = type(exc).__name__
        state.setdefault('failure_reason', exc.args[0] if isinstance(exc, Rejected) else 'wrapper_exception')
        if child is not None and child.poll() is None and not cleanup_attempted:
            try:
                cleanup_attempted = True
                child.kill(); out,err=child.communicate(timeout=2)
            except BaseException:
                pass
            state['termination_confirmed'] = child.poll() is not None
        try:
            (private/'exception.txt').write_text(repr(exc),encoding='utf-8')
        except BaseException:
            state['private_diagnostic_write_failed'] = True
    finally:
        (private/'stdout.bin').write_bytes(out)
        (private/'stderr.bin').write_bytes(err)
        try:
            state['manifest_postcheck'] = (base/'INPUT-SHA256.json').read_bytes() == manifest_bytes
            state['input_postcheck'] = {n:digest(base/n) for n in FILES} == expected
        except BaseException:
            state['input_postcheck'] = False
        if not state['manifest_postcheck']:
            state.setdefault('failure_reason', 'manifest_postcheck_failed')
            state['status'] = 'FAIL'
        if not state['input_postcheck']:
            state.setdefault('failure_reason', 'input_postcheck_failed')
            state['status'] = 'FAIL'
        if not state['termination_confirmed']:
            state.setdefault('failure_reason', 'termination_unconfirmed')
            state['status'] = 'FAIL'
        temp = root/'result.pending'
        temp.write_text(json.dumps(state,ensure_ascii=True,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
        temp.replace(root/'result.json')
    print(json.dumps({'status':state['status'],'termination_confirmed':state['termination_confirmed']},sort_keys=True))
    return 0 if state['status'] in ('PASS',) else 1

if __name__ == '__main__':
    sys.exit(main())
