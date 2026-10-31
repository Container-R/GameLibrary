"""Bounded native probe. Import is inert; main performs native calls only when launched."""
import ctypes as C
import hashlib
import json
import platform
import sys

LOADER = '/lib/x86_64-linux-gnu/libvulkan.so.1'
LOADER_SHA = 'bbd6827e9fe418e9b9740aea57ce6d21fcea03e9876b4b17835c5a9c58f849fc'

class CreateInfo(C.Structure):
    _fields_ = [('sType', C.c_int32), ('pNext', C.c_void_p), ('flags', C.c_uint32),
                ('pApplicationInfo', C.c_void_p), ('enabledLayerCount', C.c_uint32),
                ('ppEnabledLayerNames', C.POINTER(C.c_char_p)),
                ('enabledExtensionCount', C.c_uint32), ('ppEnabledExtensionNames', C.POINTER(C.c_char_p))]

def abi():
    actual = {'platform': platform.system(), 'machine': platform.machine(),
              'pointer_size': C.sizeof(C.c_void_p), 'pointer_alignment': C.alignment(C.c_void_p),
              'int32_size': C.sizeof(C.c_int32), 'uint32_size': C.sizeof(C.c_uint32),
              'size': C.sizeof(CreateInfo), 'alignment': C.alignment(CreateInfo),
              'offsets': [getattr(CreateInfo, n).offset for n, _ in CreateInfo._fields_]}
    expected = {'platform': 'Linux', 'machine': 'x86_64', 'pointer_size': 8,
                'pointer_alignment': 8, 'int32_size': 4, 'uint32_size': 4,
                'size': 64, 'alignment': 8, 'offsets': [0,8,16,24,32,40,48,56]}
    return actual, actual == expected

def classify_fill(result, capacity, count, nonnull):
    if result in (0, 5):
        if count > capacity or len(nonnull) != count or not all(nonnull):
            return 'PROTOCOL_ANOMALY'
        return 'ENUMERATED_PARTIAL' if result == 5 else ('ENUMERATED_NONZERO' if count else 'ENUMERATED_ZERO')
    return 'ENUMERATION_FAILED' if result < 0 else 'UNEXPECTED_RESULT'

def main(invocation_id):
    from pathlib import Path
    import traceback
    trace = []
    report = {'uuid': invocation_id, 'pid': __import__('os').getpid(), 'category': 'INTERRUPTED_OR_INCOMPLETE'}
    def emit(kind, value):
        print(json.dumps({'kind': kind, 'value': value}, allow_nan=False), flush=True)
    def call(name, function, *args):
        number = len(trace) // 2 + 1
        event = {'call': number, 'name': name, 'phase': 'attempt'}
        trace.append(event); emit('trace', event)
        result = function(*args)
        event = {'call': number, 'name': name, 'phase': 'returned', 'result': result}
        trace.append(event); emit('trace', event)
        return result
    instance = C.c_void_p()
    created = False
    destroy = None
    try:
        actual, valid = abi(); report['abi'] = actual
        if not valid:
            report['category'] = 'ABI_GUARD_FAILED'; return
        try:
            resolved = Path(LOADER).resolve(strict=True)
            digest = hashlib.sha256(resolved.read_bytes()).hexdigest()
            report['loader'] = {'requested': LOADER, 'resolved': str(resolved), 'sha256': digest}
        except OSError as exc:
            report.update(category='LOADER_UNAVAILABLE', error=str(exc)); return
        if digest != LOADER_SHA:
            report['category'] = 'SOURCE_PIN_MISMATCH'; return
        try:
            lib = C.CDLL(LOADER)
        except OSError as exc:
            report.update(category='LOADER_UNAVAILABLE', error=str(exc)); return
        try:
            create = lib.vkCreateInstance
            create.argtypes = [C.POINTER(CreateInfo), C.c_void_p, C.POINTER(C.c_void_p)]
            create.restype = C.c_int32
            enum = lib.vkEnumeratePhysicalDevices
            enum.argtypes = [C.c_void_p, C.POINTER(C.c_uint32), C.POINTER(C.c_void_p)]
            enum.restype = C.c_int32
            destroy = lib.vkDestroyInstance
            destroy.argtypes = [C.c_void_p, C.c_void_p]; destroy.restype = None
        except (AttributeError, TypeError) as exc:
            report.update(category='LOADER_BINDING_FAILED', error=str(exc)); return
        info = CreateInfo(); info.sType = 1
        result = call('create', create, C.byref(info), None, C.byref(instance))
        report['create_result'] = result
        if result != 0:
            report['category'] = 'INSTANCE_CREATION_FAILED' if result < 0 else 'UNEXPECTED_RESULT'
            if result == -9: report['result_name'] = 'VK_ERROR_INCOMPATIBLE_DRIVER'
            return
        if not instance.value:
            report['category'] = 'PROTOCOL_ANOMALY'; return
        created = True; report['instance_nonnull'] = True
        count = C.c_uint32(0)
        result = call('enumerate_count', enum, instance, C.byref(count), None)
        report['count_result'] = result
        if result != 0:
            report['category'] = 'ENUMERATION_FAILED' if result < 0 else 'UNEXPECTED_RESULT'; return
        capacity = count.value; report['count_query'] = capacity
        if not capacity:
            report['category'] = 'ENUMERATED_ZERO'; return
        if capacity > 64:
            report['category'] = 'COUNT_EXCEEDS_PROBE_BOUND'; return
        array = (C.c_void_p * capacity)()
        result = call('enumerate_fill', enum, instance, C.byref(count), array)
        report['fill_result'] = result; report['capacity'] = capacity
        if result in (0, 5):
            report['returned_count'] = count.value
            # Check capacity BEFORE indexing; neither error results nor out-of-range counts consume memory.
            nonnull = [bool(array[i]) for i in range(count.value)] if count.value <= capacity else []
            report['returned_nonnull'] = nonnull
            report['category'] = classify_fill(result, capacity, count.value, nonnull)
        else:
            report['category'] = classify_fill(result, capacity, 0, [])
    except Exception:
        report.update(category='PYTHON_EXCEPTION', traceback=traceback.format_exc())
    finally:
        if created:
            try:
                call('destroy', destroy, instance, None)
            except Exception:
                report.update(category='PYTHON_EXCEPTION', cleanup_traceback=traceback.format_exc())
        report['trace'] = trace
        emit('terminal', report)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('expected invocation UUID')
    main(sys.argv[1])
