"""Read-only consistency checks; not authenticated execution evidence."""
import hashlib
import json
from pathlib import Path
from child import classify_fill

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

def validate_report(report, streamed):
    trace = report['trace']
    check(trace == streamed, 'trace differs from streamed events')
    check(len(trace) % 2 == 0, 'unfinished native call')
    names = []
    for i in range(0, len(trace), 2):
        a, b = trace[i:i+2]
        check(a == {'call': i//2+1, 'name': a['name'], 'phase': 'attempt'}, 'bad attempt')
        check(b['call'] == a['call'] and b['name'] == a['name'] and b['phase'] == 'returned', 'bad return')
        check(type(b['result']) is int or (a['name'] == 'destroy' and b['result'] is None), 'bad result type')
        names.append(a['name'])
    check(names in ([], ['create'], ['create','destroy'], ['create','enumerate_count','destroy'],
                    ['create','enumerate_count','enumerate_fill','destroy']), 'invalid call order')
    results = {trace[i]['name']: trace[i+1]['result'] for i in range(0,len(trace),2)}
    for name, field in [('create','create_result'), ('enumerate_count','count_result'), ('enumerate_fill','fill_result')]:
        if name in results: check(report.get(field) == results[name], 'result mismatch')
    category = report['category']
    if category.startswith('ENUMERATED_') or category == 'COUNT_EXCEEDS_PROBE_BOUND':
        check(results.get('create') == 0 and report.get('instance_nonnull') is True and names[-1] == 'destroy', 'missing valid creation/cleanup')
        check(results.get('enumerate_count') == 0 and type(report['count_query']) is int, 'count failed')
        count = report['count_query']
        if category == 'COUNT_EXCEEDS_PROBE_BOUND':
            check(count > 64 and 'enumerate_fill' not in names, 'bound mismatch')
        elif 'enumerate_fill' not in names:
            check(count == 0 and category == 'ENUMERATED_ZERO', 'zero mismatch')
        else:
            cap = report['capacity']; returned = report['returned_count']; flags = report['returned_nonnull']
            check(type(cap) is int and type(returned) is int and 1 <= cap <= 64 and count == cap and returned >= 0, 'bad counts')
            check(all(type(x) is bool for x in flags), 'bad flags')
            check(classify_fill(results['enumerate_fill'], cap, returned, flags) == category, 'fill classification mismatch')
    if category == 'INSTANCE_CREATION_FAILED':
        check(names == ['create'] and results['create'] < 0, 'creation failure mismatch')
    return category

def consume(root, source, expected_uuid):
    root = Path(root); source = Path(source)
    def local(name):
        p = root / name
        check(not p.is_symlink() and p.is_file() and p.resolve().parent == root.resolve(), 'unsafe artifact')
        return p
    receipt = strict(local('receipt.json').read_text())
    check(receipt['uuid'] == expected_uuid and receipt['state'] == 'COMPLETE', 'not terminal invocation')
    check(receipt['returncode'] == 0 and receipt['timeout'] is False, 'child did not complete normally')
    manifest = strict((source / 'source-manifest.json').read_text())
    check(receipt['source_sha256'] == manifest, 'untrusted source manifest')
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
