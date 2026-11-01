"""Finite author-side archive checker; not an independent implementation oracle."""
import hashlib
import json
import re
from pathlib import Path

# length, flag, initial U, channel, command, final R, final U, final group
CASES = [
 (1364,0,65534,0,7,42,65535,7),(1364,0,65535,0,134,43,0,7),
 (1364,8,65534,0,7,42,65535,7),(1364,8,65535,0,134,43,0,7),
 (1364,1,65534,0,134,43,0,7),(1364,1,65535,0,134,43,0,7),
 (1364,2,65534,0,73,42,65534,8),(1364,2,65535,0,73,42,65535,8),
 (1365,0,65534,0,136,44,0,7),(1365,0,65535,0,136,44,0,7),
 (1365,8,65534,0,12,42,65535,7),(1365,8,65535,0,136,44,0,7),
 (1365,1,65534,0,136,44,0,7),(1365,1,65535,0,136,44,0,7),
 (1365,2,65534,0,136,44,0,7),(1365,2,65535,0,136,44,0,7),
 (1365,1,65535,1,-1,42,65535,7),
]
UNITS = ['callbacks','compress','host','list','packet','peer','protocol','unix']
BUILD = ['cc','-std=gnu99','-O0','-Wall','-Wextra','-Iupstream/include','fixture.c'] + [f'upstream/{p}.c' for p in UNITS] + ['-o','queue_fixture']
SOURCE_FILES = {'fixture.c','consumer.py','run.py','test_queue.py','PROTOCOL.md','UPSTREAM-SOURCE-MANIFEST.json','independent/oracle.json','reviewed-build.stderr','WARNING-POLICY.md'}
UPSTREAM_FILES = {p+'.c' for p in UNITS} | {'include/enet/'+p+'.h' for p in ('enet','protocol','unix','types','list','callbacks','time','utility')} | {'Makefile.am'}
UUID = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}')

def need(condition, message):
    if not condition:
        raise ValueError(message)

def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b

def pairs(items):
    out = {}
    for k, v in items:
        need(k not in out, 'duplicate JSON key')
        out[k] = v
    return out

def decode(s):
    def invalid(_):
        raise ValueError('non-finite JSON')
    return json.loads(s, object_pairs_hook=pairs, parse_constant=invalid)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def expected_row(i):
    length, flag, u, ch, cmd, r_end, u_end, g_end = CASES[i]
    n = 0 if ch else (1 if length == 1364 else 2)
    commands = []
    for j in range(n):
        r = 43+j if cmd in (134,136) else (0 if cmd == 73 else 42)
        us = 65535 if cmd in (7,12) else 0
        off, size = (0,1364) if j == 0 else (1364,1)
        extras = {7:[65535,1364], 73:[8,1364], 134:[1364],
                  136:[43,size,2,j,1365,off],12:[65535,size,2,j,1365,off]}[cmd]
        commands.append([cmd,0,r,r,us,off,size,True,0,0,0,j+1,extras])
    total = 0 if n == 0 else (1413 if n == 2 else (1370 if cmd == 134 else 1372))
    return {'kind':'row','id':i,'input':[length,flag,u,ch], 'before':[42,u,7,0,0,0],
            'result':-1 if ch else 0,'packet':[n,flag,length,True],
            'state':[r_end,u_end,g_end,n,total,1],
            'ordinary':commands if cmd in (7,73,12) else [],
            'reliable':commands if cmd in (134,136) else [],
            'other_empty':True,'freed_before':0,
            'cleanup':[1,0,flag,length,True,0,True,0,True,n,0]}

def expected_records(run):
    need(type(run) is str and UUID.fullmatch(run), 'invalid run identity')
    return [{'kind':'start','run':run,'version':66322,'sizes':[2,4,4,24,6,8,8],'F':1364}] + [expected_row(i) for i in range(17)] + [{'kind':'end','run':run,'rows':17}]

def check_raw(raw, run):
    need(type(raw) is bytes and len(raw) <= 1024*1024, 'raw size/type')
    lines = raw.decode('utf-8').splitlines()
    need(len(lines) == 19 and all(lines), 'exactly 19 nonempty JSONL records required')
    records = [decode(line) for line in lines]
    need(same(records, expected_records(run)), 'raw records differ from frozen cases')
    return records

def check_build_diagnostic(raw, reviewed):
    need(type(raw) is bytes and type(reviewed) is bytes, 'build diagnostic types')
    need(hashlib.sha256(reviewed).hexdigest() == 'ffdcc382ac87a1dbda0da90930ac00c5672950b9b4cb4a6ab4617af094ca0a51', 'reviewed diagnostic identity')
    need(raw == b'' or raw == reviewed, 'unreviewed build diagnostic: stop')


def check_trace(raw):
    need(type(raw) is bytes and 0 < len(raw) <= 65536, 'trace absent/oversized')
    lines = raw.decode('ascii').splitlines()
    # strace -f -o normally prefixes decimal process labels. Never export raw trace.
    need(len(lines) == 1 and re.fullmatch(r'(?:[0-9]+\s+)?\+\+\+ exited with 0 \+\+\+', lines[0]),
         'network trace must contain exactly normal exit and no syscall/signal/unknown record')

def source_snapshot(root):
    root = Path(root)
    manifest = decode((root/'SOURCE-MANIFEST.json').read_text())
    need(type(manifest) is dict and set(manifest) == {'files'} and type(manifest['files']) is dict and set(manifest['files']) == SOURCE_FILES, 'source manifest exact inputs')
    out = {}
    for name, wanted in manifest['files'].items():
        need(type(name) is str and not Path(name).is_absolute() and '..' not in Path(name).parts, 'source name')
        actual = sha(root/name)
        need(actual == wanted, 'changed source '+name)
        out[name] = actual
    upstream = decode((root/'UPSTREAM-SOURCE-MANIFEST.json').read_text())
    need(type(upstream) is dict and set(upstream) == {'commit','scope','files'}, 'upstream schema')
    need(type(upstream['files']) is list and all(type(x) is dict and set(x)=={'path','git_blob','sha256'} for x in upstream['files']), 'upstream entries')
    need({x['path'] for x in upstream['files']} == UPSTREAM_FILES, 'upstream exact paths')
    need(upstream['commit'] == '2662c0de09e36f2a2030ccc2c528a3e4c9e8138a' and len(upstream['files']) == 17, 'upstream manifest')
    for item in upstream['files']:
        name = item['path']; data = (root/'upstream'/name).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item['sha256'], 'upstream SHA256 '+name)
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == item['git_blob'], 'upstream git blob '+name)
        out['upstream/'+name] = item['sha256']
    out['SOURCE-MANIFEST.json'] = sha(root/'SOURCE-MANIFEST.json')
    return out

def verify(root, evidence):
    root, evidence = Path(root), Path(evidence)
    receipt = decode((evidence/'receipt.json').read_text())
    need(type(receipt) is dict and set(receipt)=={'schema','run','status','commands','source_before','source_after','work_source_after','tools_before','tools_after','trace_sha256','parsed_sha256','binary_sha256'}, 'receipt schema')
    need(same(receipt['schema'],1) and receipt['status'] == 'PASS', 'receipt is not PASS')
    run = receipt['run']
    need(same(receipt['source_before'], receipt['source_after']), 'source changed during run')
    need(same(receipt['source_after'], source_snapshot(root)), 'source binding')
    need(same(receipt['source_before'],receipt['work_source_after']), 'copied source changed')
    need(same(receipt['tools_before'], receipt['tools_after']), 'selected tools changed')
    need(type(receipt['tools_before']) is dict and set(receipt['tools_before'])=={'cc','strace'}, 'tool record keys')
    for item in receipt['tools_before'].values():
        need(type(item) is dict and set(item)=={'resolved','sha256'}, 'tool record shape')
        need(type(item['resolved']) is str and bool(item['resolved']) and type(item['sha256']) is str and re.fullmatch('[0-9a-f]{64}',item['sha256']), 'tool record fields')
    commands = receipt['commands']
    need(len(commands) == 3, 'exact three commands')
    expected = [('version',5,['cc','--version']), ('build',60,BUILD),
                ('fixture',20,['strace','-f','-e','trace=network','-o','network.trace','./queue_fixture',run])]
    for record,(name,timeout,argv) in zip(commands,expected):
        need(type(record) is dict and set(record)=={'name','argv','timeout_seconds','returncode','timed_out','stdout','stderr','process_id','stdout_sha256','stderr_sha256'}, 'command schema')
        need(type(record['process_id']) is int and record['process_id']>0, 'local process identity')
        need(record['name']==name and same(record['timeout_seconds'],timeout), 'command name/timeout')
        need(same(record['argv'],argv), 'command argv')
        need(type(record['returncode']) is int and record['returncode']==0 and record['timed_out'] is False, 'command failure')
        for stream in ('stdout','stderr'):
            need(record[stream] == name+'.'+stream, 'stream path')
            need(sha(evidence/record[stream]) == record[stream+'_sha256'], 'stream hash')
    need((evidence/'version.stdout').stat().st_size > 0, 'missing compiler version')
    need((evidence/'version.stderr').read_bytes() == b'', 'version stderr')
    need((evidence/'build.stdout').read_bytes() == b'', 'unexpected build stdout')
    need((evidence/'fixture.stderr').read_bytes() == b'', 'fixture/strace stderr')
    check_build_diagnostic((evidence/'build.stderr').read_bytes(),(root/'reviewed-build.stderr').read_bytes())
    # Build diagnostics are retained on failure, never silently removed.
    records = check_raw((evidence/'fixture.stdout').read_bytes(),run)
    need(sha(evidence/'network.trace') == receipt['trace_sha256'], 'trace hash')
    check_trace((evidence/'network.trace').read_bytes())
    need(sha(evidence/'parsed.json') == receipt['parsed_sha256'], 'parsed hash')
    need(same(decode((evidence/'parsed.json').read_text()),records), 'parsed/raw binding')
    need(sha(evidence/'queue_fixture') == receipt['binary_sha256'], 'local artifact binding')
    return {'status':'PASS','rows':17,'successful_rows':16,'refused_rows':1,'run':run}

if __name__ == '__main__':
    import sys
    need(len(sys.argv)==2, 'usage: consumer.py evidence-directory')
    print(json.dumps(verify(Path(__file__).resolve().parent,Path(sys.argv[1])),sort_keys=True))
