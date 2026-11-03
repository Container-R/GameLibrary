"""Five-case offline arithmetic only. Does not import/load any audio implementation."""
import base64
import binascii
import hashlib
import json
import math
import struct

CASES = (
    ('inverse-reference', 'AL_INVERSE_DISTANCE_CLAMPED', 1, 10, 1),
    ('inverse-max', 'AL_INVERSE_DISTANCE_CLAMPED', 1, 10, 10),
    ('inverse-beyond', 'AL_INVERSE_DISTANCE_CLAMPED', 1, 10, 20),
    ('inverse-short-max', 'AL_INVERSE_DISTANCE_CLAMPED', 1, 5, 20),
    ('linear-max', 'AL_LINEAR_DISTANCE_CLAMPED', 1, 10, 10),
)
PARTS = ('warmup', 'window1', 'window2')

class Invalid(ValueError):
    pass

def need(condition, reason):
    if not condition:
        raise Invalid(reason)

def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def reject_constant(value):
    raise Invalid('nonfinite JSON constant')

def read_json_lines(text):
    lines = text.splitlines()
    need(bool(lines), 'empty stream')
    result = []
    for line in lines:
        need(bool(line.strip()), 'blank event')
        try:
            row = json.loads(line, object_pairs_hook=unique, parse_constant=reject_constant)
        except (ValueError, TypeError) as exc:
            raise Invalid('invalid JSON event') from exc
        need(type(row) is dict and set(row) == {'seq', 'event', 'case', 'data'}, 'event keys')
        need(type(row['seq']) is int and row['seq'] == len(result), 'sequence')
        need(type(row['event']) is str and type(row['data']) is dict, 'event types')
        result.append(row)
    return result

def decode_window(data, part):
    need(type(data) is dict and set(data) == {'part','frame_count','byte_count','sha256','base64'}, 'window keys')
    need(data['part'] == part, 'window part')
    need(type(data['frame_count']) is int and data['frame_count'] == 4800, 'frame count')
    need(type(data['byte_count']) is int and data['byte_count'] == 19200, 'byte count')
    need(type(data['base64']) is str and len(data['base64']) == 25600, 'base64 length/type')
    try:
        raw = base64.b64decode(data['base64'], validate=True)
    except (ValueError, binascii.Error) as exc:
        raise Invalid('invalid base64') from exc
    need(len(raw) == 19200, 'decoded length')
    need(base64.b64encode(raw).decode('ascii') == data['base64'], 'noncanonical base64')
    need(type(data['sha256']) is str and hashlib.sha256(raw).hexdigest() == data['sha256'], 'window digest')
    samples = struct.unpack('<4800f', raw)
    need(all(math.isfinite(v) for v in samples), 'nonfinite binary32 sample')
    return math.sqrt(math.fsum(v*v for v in samples) / 4800)

def expected_factor(model, reference, maximum, distance):
    clamped = min(max(distance, reference), maximum)
    if model == 'AL_INVERSE_DISTANCE_CLAMPED':
        return reference / (reference + (clamped-reference))
    need(model == 'AL_LINEAR_DISTANCE_CLAMPED', 'model')
    return 1 - (clamped-reference) / (maximum-reference)

def check_cases(cases):
    """Internal decoded records: id, parameters tuple, exactly three window objects."""
    need(type(cases) is list and len(cases) == 5, 'five complete cases required')
    baseline = None
    results = []
    for actual, specification in zip(cases, CASES):
        name, model, reference, maximum, distance = specification
        need(actual['id'] == name, 'case identity/order')
        need(actual['parameters'] == specification[1:], 'case parameters')
        need(type(actual['windows']) is list and len(actual['windows']) == 3, 'three windows required')
        rms = [decode_window(w, part) for w,part in zip(actual['windows'], PARTS)]
        a,b = rms[1:]
        need(abs(a-b) <= 1e-6, 'window stability')
        if baseline is None:
            need(a >= .001 and b >= .001, 'baseline lower bound')
            baseline = (a,b)
        ratios = [a/baseline[0], b/baseline[1]]
        expected = expected_factor(model, reference, maximum, distance)
        need(all(abs(v-expected) <= .001 for v in ratios), 'ratio threshold')
        if model == 'AL_LINEAR_DISTANCE_CLAMPED':
            need(a <= 1e-6 and b <= 1e-6, 'linear absolute bound')
        results.append({'case':name,'rms':rms[1:],'ratios':ratios,'expected_factor':expected})
    return results

def typed_equal(actual, expected):
    if type(actual) != type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(typed_equal(actual[k], v) for k,v in expected.items())
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(typed_equal(a,b) for a,b in zip(actual,expected))
    return actual == expected

def no_errors(data):
    checks = data.get('checks')
    need(type(checks) is list and bool(checks), 'missing checks')
    for check in checks:
        need(type(check) is dict and set(check) == {'stage','error'}, 'check shape')
        need(type(check['stage']) is str and type(check['error']) is int and check['error'] == 0, 'reported API error')

def consume(text):
    need(text.endswith('\n'), 'unterminated stream')
    events = read_json_lines(text)
    cursor = 0
    def take(event, case):
        nonlocal cursor
        need(cursor < len(events), 'missing event/window')
        row = events[cursor]
        need(row['event'] == event and typed_equal(row['case'],case), 'event order/case')
        cursor += 1
        return row['data']
    begin = take('begin',None)
    for key,value in {'schema':1,'configuration_fully_excluded':False,'case_count':5,'sample_rate':48000,'frame_count_per_part':4800,'parts_per_case':3,'sample_format':'float32-le','pcm_format':'s16-le','pcm_positive_count':24,'pcm_negative_count':24,'pcm_amplitude':1024,'ordinary_device_calls':0,'capture_calls':0,'effect_calls':0}.items():
        need(key in begin and typed_equal(begin[key],value), 'begin configuration')
    global_data = take('global_ready',None)
    need(global_data.get('loopback_extension') is True and global_data.get('entries_present') is True, 'global capability')
    pcm = struct.pack('<48h', *([1024]*24+[-1024]*24))
    need(global_data.get('pcm_sha256') == hashlib.sha256(pcm).hexdigest(), 'PCM identity')
    no_errors(global_data)
    records=[]
    reported=[]
    for name,model,reference,maximum,distance in CASES:
        enum = 0xD002 if model.startswith('AL_INVERSE') else 0xD004
        expected=expected_factor(model,reference,maximum,distance)
        config=take('case_begin',name)
        need(typed_equal(config,{'id':name,'model':enum,'maximum':maximum,'distance':distance,'ratio':float(expected)}), 'case parameters')
        ready=take('ready',name);no_errors(ready)
        need(ready.get('version')=='1.1 ALSOFT 1.24.2' and ready.get('renderer')=='OpenAL Soft','reported version')
        need(typed_equal(ready.get('format'),{'frequency':48000,'channels':0x1500,'type':0x1406,'hrtf':0,'limiter':0}),'actual format')
        need(type(ready.get('distance_model')) is int and ready['distance_model']==enum,'actual model')
        source=ready.get('source');need(type(source) is dict,'source properties')
        for key,value in {'reference':1.0,'maximum':float(maximum),'rolloff':1.0,'position':[0.0,0.0,-float(distance)]}.items():
            need(typed_equal(source.get(key),value),'actual distance parameters')
        play=take('playing',name);no_errors(play);need(type(play.get('state')) is int and play['state']==0x1012,'not playing')
        windows=[]
        for part in PARTS:
            w=take('window',name);decode_window(w,part);windows.append(w)
            checked=take('window_checked',name);no_errors(checked)
            need(checked.get('part')==part and type(checked.get('state')) is int and checked['state']==0x1012,'window state')
        reported.append(take('case_metrics',name))
        cleanup=take('cleanup',name);no_errors(cleanup)
        need(cleanup.get('ok') is True and typed_equal(cleanup.get('failures'),[]),'cleanup failure')
        need(typed_equal(take('case_pass',name),{'numeric_ok':True,'cleanup_ok':True}),'case failure')
        records.append({'id':name,'parameters':(model,reference,maximum,distance),'windows':windows})
    need(typed_equal(take('success',None),{'cases':5,'render_calls':15,'frames':72000,'source_objects':5,'buffer_objects':5,'configuration_fully_excluded':False}),'success counts')
    need(cursor == len(events),'extra events')
    results=check_cases(records)
    for values,observed in zip(results,reported):
        need(type(observed) is dict and set(observed)=={'rms','ratios'},'reported metrics shape')
        for key in ('rms','ratios'):
            need(type(observed[key]) is list and len(observed[key])==2,'reported metric count')
            need(all(type(v) is float and math.isfinite(v) for v in observed[key]),'reported metric type')
            need(observed[key]==values[key],'reported metrics mismatch')
    return {'status':'PASS','scope':'offline arithmetic, not API trace or isolation certification','cases':results}

if __name__ == '__main__':
    import sys
    from pathlib import Path
    try:
        need(len(sys.argv)==2,'one JSONL input required')
        answer=consume(Path(sys.argv[1]).read_text(encoding='utf-8'))
    except (Invalid, UnicodeError, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({'status':'FAIL','category':type(exc).__name__},allow_nan=False))
        raise SystemExit(1)
    print(json.dumps(answer,allow_nan=False,sort_keys=True))
