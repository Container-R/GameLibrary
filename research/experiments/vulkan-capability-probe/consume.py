"""Read-only consistency checks; not authenticated execution evidence."""
import hashlib
import json
from pathlib import Path
from child import classify_fill, LOADER, LOADER_SHA

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check(condition, message):
    if not condition: raise ValueError(message)

def strict(text):
    def pairs(items):
        out = {}
        for k, v in items:
            check(k not in out, 'duplicate JSON key'); out[k] = v
        return out
    def bad(x): raise ValueError('nonfinite JSON')
    def number(x):
        import math
        v = float(x); check(math.isfinite(v), 'nonfinite JSON'); return v
    return json.loads(text, object_pairs_hook=pairs, parse_constant=bad, parse_float=number)

EXPECTED_ABI = {'platform':'Linux','machine':'x86_64','pointer_size':8,'pointer_alignment':8,
                'int32_size':4,'uint32_size':4,'size':64,'alignment':8,'offsets':[0,8,16,24,32,40,48,56]}

def validate_report(report, streamed):
    trace = report['trace']
    check(trace == streamed, 'trace differs from streamed events')
    check(len(trace) % 2 == 0, 'unfinished native call')
    names = []
    for i in range(0, len(trace), 2):
        a, b = trace[i:i+2]
        check(a == {'call': i//2+1, 'name': a['name'], 'phase': 'attempt'}, 'bad attempt')
        check(b['call'] == a['call'] and b['name'] == a['name'] and b['phase'] == 'returned', 'bad return')
        check(b['result'] is None if a['name'] == 'destroy' else type(b['result']) is int, 'bad result type')
        if a['name'] != 'destroy': check(-(2**31) <= b['result'] < 2**31, 'VkResult out of signed32 range')
        names.append(a['name'])
    check(names in ([], ['create'], ['create','destroy'], ['create','enumerate_count','destroy'],
                    ['create','enumerate_count','enumerate_fill','destroy']), 'invalid call order')
    results = {trace[i]['name']: trace[i+1]['result'] for i in range(0,len(trace),2)}
    for name, field in [('create','create_result'), ('enumerate_count','count_result'), ('enumerate_fill','fill_result')]:
        if name in results: check(report.get(field) == results[name], 'result mismatch')
    category = report['category']
    actual_abi = report.get('abi')
    check(type(actual_abi) is dict and set(actual_abi) == set(EXPECTED_ABI), 'missing/malformed ABI fields')
    check(all(type(actual_abi[k]) is int for k in ('pointer_size','pointer_alignment','int32_size','uint32_size','size','alignment')), 'ABI integer types')
    check(type(actual_abi['platform']) is str and type(actual_abi['machine']) is str, 'ABI platform types')
    check(type(actual_abi['offsets']) is list and len(actual_abi['offsets']) == 8 and all(type(x) is int for x in actual_abi['offsets']), 'ABI offset types')
    if category != 'ABI_GUARD_FAILED':
        check(actual_abi == EXPECTED_ABI, 'recorded ABI mismatch')
    else:
        check(not names and actual_abi != EXPECTED_ABI, 'ABI guard category mismatch')
    if names or category == 'LOADER_BINDING_FAILED':
        loader = report.get('loader', {})
        check(loader.get('requested') == LOADER and loader.get('resolved') == '/usr/lib/x86_64-linux-gnu/libvulkan.so.1.4.309' and loader.get('sha256') == LOADER_SHA, 'recorded loader mismatch')
    early = {'ABI_GUARD_FAILED', 'SOURCE_PIN_MISMATCH', 'LOADER_UNAVAILABLE', 'LOADER_BINDING_FAILED'}
    if category in early:
        check(not names or category == 'SOURCE_PIN_MISMATCH', 'early failure has API calls')
        if category in ('LOADER_UNAVAILABLE','LOADER_BINDING_FAILED'): check(bool(report.get('error')), 'missing error')
        if category == 'SOURCE_PIN_MISMATCH':
            check(report.get('loader',{}).get('sha256') != LOADER_SHA or report.get('loader_after_sha256') != LOADER_SHA, 'not a loader pin mismatch')
            raise ValueError('source drift cannot certify observation')
    elif category in ('ENUMERATION_FAILED','UNEXPECTED_RESULT'):
        if names == ['create']:
            check(category == 'UNEXPECTED_RESULT' and results['create'] > 0, 'unexpected create category')
        else:
            check(names in (['create','enumerate_count','destroy'], ['create','enumerate_count','enumerate_fill','destroy']), 'missing enum failure trace')
            check(results['create'] == 0 and report.get('instance_nonnull') is True, 'invalid instance')
            phase = 'enumerate_fill' if 'enumerate_fill' in names else 'enumerate_count'
            if phase == 'enumerate_fill': check(results['enumerate_count'] == 0 and type(report.get('count_query')) is int and 1 <= report['count_query'] <= 64, 'invalid fill capacity')
            value = results[phase]
            check(value < 0 if category == 'ENUMERATION_FAILED' else value > 0 and (phase != 'enumerate_fill' or value != 5), 'wrong error category')
    elif category == 'PYTHON_EXCEPTION':
        raise ValueError('exception evidence is retained but not certified as completed native observation')
    elif category == 'PROTOCOL_ANOMALY':
        # Preserve anomalous raw evidence but never certify it as a consistent native observation.
        raise ValueError('native protocol anomaly')
    else:
        check(category.startswith('ENUMERATED_') or category in ('INSTANCE_CREATION_FAILED','COUNT_EXCEEDS_PROBE_BOUND'), 'invalid child terminal category')
    if names:
        check(report.get('loader_after_sha256') == LOADER_SHA, 'missing/changed loader after hash')
        if results.get('create') == 0 and report.get('instance_nonnull') is True:
            check(names[-1] == 'destroy' and results.get('destroy') is None, 'missing cleanup')
    if category.startswith('ENUMERATED_') or category == 'COUNT_EXCEEDS_PROBE_BOUND':
        check(results.get('create') == 0 and report.get('instance_nonnull') is True and names[-1] == 'destroy', 'missing valid creation/cleanup')
        check(results.get('enumerate_count') == 0 and type(report['count_query']) is int and 0 <= report['count_query'] < 2**32, 'count failed')
        count = report['count_query']
        if category == 'COUNT_EXCEEDS_PROBE_BOUND':
            check(count > 64 and 'enumerate_fill' not in names, 'bound mismatch')
        elif 'enumerate_fill' not in names:
            check(count == 0 and category == 'ENUMERATED_ZERO', 'zero mismatch')
        else:
            cap = report['capacity']; returned = report['returned_count']; flags = report['returned_nonnull']
            check(type(cap) is int and type(returned) is int and 1 <= cap <= 64 and count == cap and 0 <= returned < 2**32, 'bad counts')
            check(all(type(x) is bool for x in flags), 'bad flags')
            check(classify_fill(results['enumerate_fill'], cap, returned, flags) == category, 'fill classification mismatch')
    if category == 'INSTANCE_CREATION_FAILED':
        check(names == ['create'] and results['create'] < 0 and report.get('instance_nonnull') is not True, 'creation failure mismatch')
    return category

def consume(root, source, expected_uuid):
    root = Path(root); source = Path(source)
    for p in (root, *root.parents, source, *source.parents):
        check(not p.is_symlink(), 'symlink root component')
    def local(name):
        p = root / name
        check(not p.is_symlink() and p.is_file() and p.resolve().parent == root.resolve(), 'unsafe artifact')
        return p
    receipt = strict(local('receipt.json').read_text())
    check(receipt['uuid'] == expected_uuid and receipt['state'] == 'COMPLETE', 'not terminal invocation')
    check(receipt['returncode'] == 0 and receipt['timeout'] is False, 'child did not complete normally')
    check(type(receipt['returncode']) is int, 'noninteger return code')
    check(receipt.get('group_remaining') is False and not receipt.get('unexpected_descendants'), 'process group not clean')
    protocol = strict((source / 'protocol.json').read_text())
    check(digest(source / 'protocol.json') == '8ec8c5746b1b8280ea0a9acfc1cedc2fb73e2572970675d90db90bfa858a0057', 'untrusted protocol')
    check(digest(source / 'isolation.py') == protocol['environment']['helper_sha256'], 'untrusted helper')
    check(receipt['base_environment'] == protocol['environment']['base_environment_exact'], 'environment mismatch')
    mapping = receipt['isolation']; keys = protocol['environment']['added_by_helper']
    check(set(mapping) == set(keys), 'isolation keys differ')
    owned = Path(receipt['owned_runtime_root'])
    check(owned.is_absolute() and '..' not in owned.parts and owned != Path(owned.anchor), 'invalid archived owned root')
    check(all(mapping[k] == str(owned/k) for k in keys), 'isolation path mismatch')
    check(receipt['argv'] == [receipt['python'], str(Path(receipt['source_root'])/'child.py'), expected_uuid], 'argv mismatch')
    check(Path(receipt['python']).is_absolute() and Path(receipt['source_root']).is_absolute(), 'nonabsolute executable/source')
    manifest = strict((source / 'source-manifest.json').read_text())
    check(receipt['source_sha256'] == manifest, 'untrusted source manifest')
    check(receipt['source_after_sha256'] == manifest, 'source drift/missing after hashes')
    for name, sha in manifest.items():
        check(Path(name).name == name and digest(source / name) == sha, 'source mismatch')
    for name in ('stdout.txt','stderr.txt'):
        check(digest(local(name)) == receipt['output_sha256'][name], 'output mismatch')
    events = [strict(line) for line in local('stdout.txt').read_text().splitlines()]
    check(all(e['kind'] in ('trace','terminal') for e in events), 'unknown output')
    terminals = [e['value'] for e in events if e['kind'] == 'terminal']
    check(len(terminals) == 1 and events[-1]['kind'] == 'terminal', 'missing/followed terminal')
    report = terminals[0]
    check(report['uuid'] == expected_uuid and report['pid'] == receipt['child_pid'], 'identity mismatch')
    check(report['category'] == receipt['category'], 'category mismatch')
    protocol = strict((source / 'protocol.json').read_text())
    check(report['category'] in protocol['terminal_categories'], 'unknown category')
    return validate_report(report, [e['value'] for e in events if e['kind'] == 'trace'])

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(); p.add_argument('output'); p.add_argument('uuid'); p.add_argument('--source', default=str(Path(__file__).parent))
    args = p.parse_args()
    print(json.dumps({'category': consume(args.output, args.source, args.uuid), 'meaning': 'pinned archive consistency only; not authenticated execution or GPU success'}))
