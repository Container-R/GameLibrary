"""Portable static evidence check: recorded identities, not current binary authentication."""
import datetime
import hashlib
from pathlib import Path, PurePosixPath
import sys
import uuid
from oracle import SOURCES, BASE_ENV, BINARY, VERSION, PROTOCOL, HELPER, require, equal, loads, parse_stream, check_payloads

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def absolute(value):
    require(type(value) is str,'path type')
    path=PurePosixPath(value)
    require(path.is_absolute() and '..' not in path.parts,'absolute clean path')
    return path

def stamp(value):
    require(type(value) is str,'timestamp type')
    result=datetime.datetime.fromisoformat(value)
    require(result.utcoffset()==datetime.timedelta(0),'UTC timestamp')
    return result

def consume(source_root,evidence):
    root=Path(source_root);out=Path(evidence)
    receipt=loads((out/'receipt.json').read_text())
    equal(receipt['status'],'PASS','receipt status')
    rid=receipt['uuid']; require(type(rid) is str and str(uuid.UUID(rid))==rid and out.name==rid,'UUID binding')
    original=absolute(receipt['original_source_root']); invocation=absolute(receipt['original_invocation'])
    require(invocation==original/'evidence'/rid,'invocation binding')
    equal(receipt['stop_initially_absent'],True,'STOP precondition')
    equal(receipt['base_environment'],BASE_ENV,'minimal base environment')
    expected_sources={name:sha(root/name) for name in SOURCES}
    require(expected_sources['protocol.md']==PROTOCOL and expected_sources['isolation.py']==HELPER,'protocol/helper pin')
    equal(receipt['source_before'],expected_sources,'sources before')
    equal(receipt['source_after'],expected_sources,'sources after')
    equal(receipt['binary_before'],BINARY,'binary before');equal(receipt['binary_after'],BINARY,'binary after')
    equal(receipt['version_processes'],1,'version count');equal(receipt['behavior_processes'],2,'behavior count')
    processes=receipt['processes'];require(type(processes) is list and len(processes)==3,'process count')
    pids=[]
    for name,item in zip(('version','server','client'),processes):
        equal(item['name'],name,'process name');equal(item['status'],'RETURNED','process status');equal(item['exit_code'],0,'exit')
        require(type(item['pid']) is int and item['pid']>0 and item['pid'] not in pids,'pid identity');pids.append(item['pid'])
        require(stamp(item['returned_utc'])>=stamp(item['attempted_utc']),'timestamp order')
        equal(item['cwd'],str(original),'cwd')
        command=['/usr/local/bin/godot','--version'] if name=='version' else ['/usr/local/bin/godot','--headless','--path',str(original),'--single-threaded-scene','--script',str(original/'main.gd'),'--',name,str(invocation/'STOP')]
        equal(item['argv'],command,'argv')
        keys=('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')
        equal(item['selected_environment'],{key:str(invocation/'environment'/name/key) for key in keys},'environment')
    require(stamp(processes[0]['returned_utc'])<=stamp(processes[1]['attempted_utc'])<=stamp(processes[2]['attempted_utc']),'launch order')
    require(stamp(processes[1]['returned_utc'])>=stamp(processes[2]['attempted_utc']) and stamp(processes[2]['returned_utc'])>=stamp(processes[1]['attempted_utc']),'recorded behavior lifetimes overlap')
    equal(receipt['orchestration'],[{'kind':'ATTEMPT','name':'version'},{'kind':'VERSION_ACCEPTED'},{'kind':'ATTEMPT','name':'server'}, {'kind':'SERVER_READY_ACCEPTED'},{'kind':'ATTEMPT','name':'client'},{'kind':'BOTH_TERMINALS_ACCEPTED'},{'kind':'STOP_CREATED'}],'orchestration')
    files=('version.stdout','version.stderr','server.stdout','server.stderr','client.stdout','client.stderr','server.json','client.json')
    equal(receipt['output_sha256'],{name:sha(out/name) for name in files},'output hashes')
    require((out/'version.stderr').read_bytes()==b'' and (out/'version.stdout').read_bytes().strip()==VERSION.encode(),'version raw')
    parsed={}
    for name in ('server','client'):
        _,results=parse_stream((out/(name+'.stdout')).read_bytes(),(out/(name+'.stderr')).read_bytes())
        data=loads((out/(name+'.json')).read_text());equal(results[0],data,'raw parsed association');parsed[name]=data
    result=check_payloads(parsed['server'],parsed['client'])
    return dict(status='PASS',uuid=rid,**result,version_processes=1,behavior_processes=2,scope='static archive consistency; no execution authenticity or current binary check')
if __name__=='__main__':
    import json
    require(len(sys.argv)==3,'usage: consumer.py SOURCE_ROOT EVIDENCE_UUID_DIR')
    print(json.dumps(consume(sys.argv[1],sys.argv[2]),sort_keys=True))
