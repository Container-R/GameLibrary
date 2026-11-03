"""Preparation only: same-driver loopback capability, never render or play."""
import ctypes as C
import json
import re
import sys

class Stop(Exception):
    pass


def main():
    report = {'schema': 1, 'status': 'FAIL', 'stage': 'abi', 'checks': [],
              'cleanup': [], 'cleanup_ok': False, 'configuration_fully_excluded': False,
              'source_calls': 0, 'buffer_calls': 0, 'render_calls': 0}
    lib = None
    dev = ctx = None
    current = False
    def check(label, code):
        report['checks'].append({'stage': label, 'error': int(code)})
        if code != 0:
            raise Stop(label)
    def bind(name, result, args):
        f = getattr(lib, name)
        f.restype, f.argtypes = result, args
        return f
    def safe_string(name, value):
        if value is None:
            raise Stop('null_string')
        try:
            s = value.decode('ascii', 'strict')
        except UnicodeError:
            report['status'] = 'SOURCE_VERSION_REVIEW_REQUIRED'
            raise Stop('unrecognized_technical_string')
        if name == 'version':
            if not re.fullmatch(r'1\.1(?: ALSOFT [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})?', s):
                report['status'] = 'SOURCE_VERSION_REVIEW_REQUIRED'
                raise Stop('unrecognized_version')
        elif s != 'OpenAL Soft':
            report['status'] = 'SOURCE_VERSION_REVIEW_REQUIRED'
            raise Stop('unrecognized_renderer')
        return s
    try:
        if C.sizeof(C.c_int) != 4 or C.sizeof(C.c_char) != 1:
            raise Stop('abi')
        report['stage'] = 'load'
        lib = C.CDLL('libopenal.so.1')  # Linux loader selection; not vendor identity proof.
        err = bind('alcGetError', C.c_int, [C.c_void_p])
        ext = bind('alcIsExtensionPresent', C.c_byte, [C.c_void_p, C.c_char_p])
        proc = bind('alcGetProcAddress', C.c_void_p, [C.c_void_p, C.c_char_p])
        create = bind('alcCreateContext', C.c_void_p, [C.c_void_p, C.POINTER(C.c_int)])
        make = bind('alcMakeContextCurrent', C.c_byte, [C.c_void_p])
        destroy = bind('alcDestroyContext', None, [C.c_void_p])
        close = bind('alcCloseDevice', C.c_byte, [C.c_void_p])
        getint = bind('alcGetIntegerv', None, [C.c_void_p, C.c_int, C.c_int, C.POINTER(C.c_int)])
        alerr = bind('alGetError', C.c_int, [])
        string = bind('alGetString', C.c_char_p, [C.c_int])
        report['stage'] = 'extension'
        check('initial_alc', err(None))
        supported = bool(ext(None, b'ALC_SOFT_loopback'))
        check('extension', err(None))
        report['loopback_extension'] = supported
        if not supported:
            report['status'] = 'UNSUPPORTED'
            raise Stop('loopback_extension')
        entries = {}
        for name in ('alcLoopbackOpenDeviceSOFT', 'alcIsRenderFormatSupportedSOFT', 'alcRenderSamplesSOFT'):
            entries[name] = proc(None, name.encode('ascii'))
            check('resolve_' + name, err(None))
            if not entries[name]:
                raise Stop('missing_loopback_entry')
        report['entries_present'] = True
        open_loop = C.CFUNCTYPE(C.c_void_p, C.c_char_p)(entries['alcLoopbackOpenDeviceSOFT'])
        format_ok = C.CFUNCTYPE(C.c_byte, C.c_void_p, C.c_int, C.c_int, C.c_int)(entries['alcIsRenderFormatSupportedSOFT'])
        # Render entry is only checked non-null; never bound or called.
        report['stage'] = 'loopback_open'
        dev = open_loop(None)
        check('loopback_open', err(dev))
        if not dev:
            raise Stop('loopback_open_null')
        report['stage'] = 'device_extensions'
        for key, name in [('hrtf_extension', b'ALC_SOFT_HRTF'), ('limiter_extension', b'ALC_SOFT_output_limiter')]:
            supported = bool(ext(dev, name))
            check(key, err(dev))
            report[key] = supported
            if not supported:
                report['status'] = 'UNSUPPORTED'
                raise Stop(key)
        report['stage'] = 'format'
        ok = bool(format_ok(dev, 48000, 0x1500, 0x1406))
        check('format', err(dev))
        report['format_supported'] = ok
        if not ok:
            report['status'] = 'UNSUPPORTED'
            raise Stop('format_48000_mono_float')
        report['stage'] = 'context'
        attrs = (C.c_int * 11)(0x1007, 48000, 0x1990, 0x1500, 0x1991, 0x1406, 0x1992, 0, 0x199A, 0, 0)
        ctx = create(dev, attrs)
        check('create_context', err(dev))
        if not ctx:
            raise Stop('context_null')
        current = bool(make(ctx))
        check('make_current', err(dev))
        if not current:
            raise Stop('make_current_false')
        check('initial_al', alerr())
        report['stage'] = 'technical_strings'
        for name, token in [('version', 0xB002), ('renderer', 0xB003)]:
            value = string(token)
            check('get_' + name, alerr())
            report[name] = safe_string(name, value)
        if report['version'] != '1.1 ALSOFT 1.24.2':
            report['status'] = 'SOURCE_VERSION_REVIEW_REQUIRED'
            raise Stop('source_version_mismatch')
        report['stage'] = 'actual_attributes'
        report['actual_format'] = {}
        for name, token, expected in [('frequency', 0x1007, 48000), ('channels', 0x1990, 0x1500), ('type', 0x1991, 0x1406), ('hrtf', 0x1992, 0), ('limiter', 0x199A, 0)]:
            value = C.c_int(-1)
            getint(dev, token, 1, C.byref(value))
            check('get_' + name, err(dev))
            report['actual_format'][name] = value.value
            if value.value != expected:
                raise Stop('attribute_readback')
        value = C.c_int(-1)
        getint(dev, 0x1993, 1, C.byref(value))
        check('get_hrtf_status', err(dev))
        report['hrtf_status'] = value.value  # diagnostic enum, not forced to generic disabled
        report['status'] = 'SUPPORTED'
        report['stage'] = 'complete'
    except BaseException as exc:
        if report['status'] not in ('UNSUPPORTED', 'SOURCE_VERSION_REVIEW_REQUIRED'):
            report['status'] = 'FAIL'
        report['failure_category'] = type(exc).__name__
        report['failure_reason'] = exc.args[0] if isinstance(exc, Stop) else 'unexpected_exception'
        # Stop arguments are exclusively fixed labels in this file, never external text.
    finally:
        clean = True
        if dev:
            if ctx:
                # Detach even if a previous make-current returned unexpectedly.
                try:
                    ok = bool(make(None)); code = err(dev)
                    report['cleanup'].append({'stage': 'detach', 'ok': ok, 'error': code})
                    clean = clean and ok and code == 0
                except BaseException:
                    clean = False
                try:
                    destroy(ctx); code = err(dev)
                    report['cleanup'].append({'stage': 'destroy_context', 'error': code})
                    clean = clean and code == 0
                except BaseException:
                    clean = False
            try:
                ok = bool(close(dev))
                report['cleanup'].append({'stage': 'close_loopback', 'ok': ok})
                clean = clean and ok
                # Device pointer is invalid after successful close: no error query.
            except BaseException:
                clean = False
        report['cleanup_ok'] = bool(clean)
        if not clean:
            report.setdefault('failure_reason', 'cleanup_failed')
            report['status'] = 'FAIL'
    print(json.dumps(report, sort_keys=True, allow_nan=False), flush=True)
    return 0 if report['status'] in ('SUPPORTED', 'UNSUPPORTED', 'SOURCE_VERSION_REVIEW_REQUIRED') and report['cleanup_ok'] else 1

if __name__ == '__main__':
    sys.exit(main())
