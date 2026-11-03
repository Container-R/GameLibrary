"""Preparation only. One fresh child; no retry, no ordinary audio device."""
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

FILES = ('PROTOCOL.md', 'driver.py', 'runner.py', 'isolation.py', 'alsoft.conf')
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

def validate_report(r):
    base_checks = ['initial_alc','extension','resolve_alcLoopbackOpenDeviceSOFT',
                   'resolve_alcIsRenderFormatSupportedSOFT','resolve_alcRenderSamplesSOFT',
                   'loopback_open','hrtf_extension','limiter_extension','format',
                   'create_context','make_current','initial_al','get_version','get_renderer',
                   'get_frequency','get_channels','get_type','get_hrtf','get_limiter','get_hrtf_status']
    reasons = set(base_checks) | {'abi','null_string','unrecognized_version','unrecognized_renderer',
        'unrecognized_technical_string','loopback_extension','missing_loopback_entry','loopback_open_null',
        'format_48000_mono_float','context_null','make_current_false','attribute_readback',
        'source_version_mismatch','unexpected_exception','cleanup_failed'}
    def exact(a, b):
        if type(a) is not type(b): return False
        if type(a) is dict:
            return a.keys() == b.keys() and all(exact(a[k], b[k]) for k in a)
        if type(a) is list:
            return len(a) == len(b) and all(exact(x,y) for x,y in zip(a,b))
        return a == b
    def require(value, message):
        if not value: raise Rejected(message)
    require(type(r) is dict, 'schema')
    allowed = {'schema','status','stage','checks','cleanup','cleanup_ok','loopback_extension',
               'entries_present','format_supported','actual_format','version','renderer','failure_category',
               'failure_reason','configuration_fully_excluded','source_calls','buffer_calls','render_calls',
               'hrtf_extension','limiter_extension','hrtf_status'}
    require(not (set(r)-allowed) and exact(r.get('schema'),1), 'report_keys')
    require(r.get('status') in ('SUPPORTED','UNSUPPORTED','SOURCE_VERSION_REVIEW_REQUIRED','FAIL'), 'status')
    require(r.get('configuration_fully_excluded') is False, 'configuration_scope')
    for key in ('source_calls','buffer_calls','render_calls'):
        require(exact(r.get(key),0), 'call_scope')
    require(type(r.get('cleanup_ok')) is bool, 'cleanup_type')
    if 'version' in r:
        require(type(r['version']) is str and re.fullmatch(r'1\.1(?: ALSOFT [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})?',r['version']), 'version')
    if 'renderer' in r: require(r['renderer'] == 'OpenAL Soft', 'renderer')
    if 'failure_reason' in r: require(r['failure_reason'] in reasons, 'failure_reason')
    def safe(v):
        if type(v) is str:
            require(re.fullmatch(r'[A-Za-z0-9_. ]{1,100}',v), 'unsafe_string')
        elif type(v) is dict:
            for k,val in v.items(): safe(k); safe(val)
        elif type(v) is list:
            for val in v: safe(val)
        else: require(type(v) in (bool,int), 'unexpected_type')
    safe(r)
    for field in ('checks','cleanup'):
        require(type(r.get(field)) is list, 'list_type')
        for item in r[field]:
            require(type(item) is dict, 'entry_type')
            if 'error' in item: require(type(item['error']) is int, 'error_type')
            if 'ok' in item: require(type(item['ok']) is bool, 'ok_type')
    close_only = [{'stage':'close_loopback','ok':True}]
    full_cleanup = [{'stage':'detach','ok':True,'error':0},{'stage':'destroy_context','error':0},*close_only]
    if r['status'] == 'FAIL':
        require(r.get('failure_reason') in reasons, 'failed_reason')
        return r  # retained, but parent cannot accept this as completed capability
    require(r['cleanup_ok'] is True, 'cleanup_failed')
    n = len(r['checks'])
    require(exact(r['checks'],[{'stage':x,'error':0} for x in base_checks[:n]]) and n <= len(base_checks), 'check_sequence')
    if r['status'] == 'UNSUPPORTED':
        reason = r.get('failure_reason')
        if reason == 'loopback_extension':
            require(n == 2 and r.get('stage') == 'extension' and r.get('loopback_extension') is False and r['cleanup'] == [], 'unsupported_extension')
        else:
            require(r.get('loopback_extension') is True and r.get('entries_present') is True and exact(r['cleanup'],close_only), 'unsupported_device')
            if reason == 'hrtf_extension':
                require(n == 7 and r.get('stage') == 'device_extensions' and r.get('hrtf_extension') is False, 'unsupported_hrtf')
            elif reason == 'limiter_extension':
                require(n == 8 and r.get('stage') == 'device_extensions' and r.get('hrtf_extension') is True and r.get('limiter_extension') is False, 'unsupported_limiter')
            else:
                require(reason == 'format_48000_mono_float' and n == 9 and r.get('stage') == 'format' and r.get('format_supported') is False and r.get('hrtf_extension') is True and r.get('limiter_extension') is True, 'unsupported_format')
        return r
    require(all(r.get(k) is True for k in ('loopback_extension','entries_present','hrtf_extension','limiter_extension','format_supported')), 'capability_flags')
    require(exact(r['cleanup'],full_cleanup), 'cleanup_sequence')
    if r['status'] == 'SOURCE_VERSION_REVIEW_REQUIRED':
        reason = r.get('failure_reason')
        require(r.get('stage') == 'technical_strings' and 'actual_format' not in r and 'hrtf_status' not in r, 'source_review_scope')
        if reason == 'source_version_mismatch':
            require(n == 14 and 'version' in r and r['version'] != '1.1 ALSOFT 1.24.2' and r.get('renderer') == 'OpenAL Soft', 'source_version')
        elif reason == 'unrecognized_version':
            require(n == 13 and 'version' not in r and 'renderer' not in r, 'source_version')
        elif reason == 'unrecognized_renderer':
            require(n == 14 and 'version' in r and 'renderer' not in r, 'source_renderer')
        else:
            require(reason == 'unrecognized_technical_string' and ((n == 13 and 'version' not in r and 'renderer' not in r) or (n == 14 and 'version' in r and 'renderer' not in r)), 'source_string')
        return r
    require(r.get('stage') == 'complete' and n == len(base_checks) and 'failure_reason' not in r, 'supported_scope')
    require(r.get('version') == '1.1 ALSOFT 1.24.2' and r.get('renderer') == 'OpenAL Soft', 'source_version')
    require(exact(r.get('actual_format'),{'frequency':48000,'channels':0x1500,'type':0x1406,'hrtf':0,'limiter':0}), 'actual_attributes')
    require(type(r.get('hrtf_status')) is int, 'hrtf_status')
    return r

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
        report = validate_report(strict_json(out))
        state['observation'] = report
        if child.returncode != 0 or err or report['cleanup_ok'] is not True or report['status'] == 'FAIL':
            raise Rejected('child_or_cleanup_failure')
        state['status'] = report['status']  # capability only, never numeric PASS
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
    return 0 if state['status'] in ('SUPPORTED','UNSUPPORTED','SOURCE_VERSION_REVIEW_REQUIRED') else 1

if __name__ == '__main__':
    sys.exit(main())
