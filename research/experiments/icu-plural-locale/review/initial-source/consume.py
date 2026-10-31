"""Portable static archive consistency checks. Never imports a native probe."""
import hashlib,json,math
from pathlib import Path
PROTOCOL_SHA='e44d2d3a7463eeb2669ad1a3ad37d894611d792ee3221642b1d459dda32d377c'
NAMES={'protocol.json','isolation.py','child.py','run.py','consume.py','test_pure.py'}
def require(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strict(s):
    def pairs(xs):
        d={}
        for k,v in xs:require(k not in d,'duplicate key');d[k]=v
        return d
    def bad(x):raise ValueError('nonfinite JSON')
    def floating(x):
        v=float(x);require(math.isfinite(v),'nonfinite JSON');return v
    return json.loads(s,object_pairs_hook=pairs,parse_constant=bad,parse_float=floating)
def i32(x):return type(x) is int and -(2**31)<=x<2**31
def no_symlink(p):
    for x in (p,*p.parents):require(not x.is_symlink(),'symlink path')
def local(root,name):
    name=Path(name);require(not name.is_absolute() and '..' not in name.parts,'unsafe relative path')
    p=root/name;no_symlink(p);require(p.is_file() and p.resolve().is_relative_to(root.resolve()),'missing/escaped file');return p

def validate_report(r,trace,loads,protocol,config_id,invocation):
    config=next(x for x in protocol['configurations'] if x['id']==config_id)
    require(r['category']=='COMPLETE_EXPECTED_OUTPUTS','not a completed expected observation')
    require(r['uuid']==invocation and r['config']==config_id and r['locale']==config['locale'] and r['pattern']==config['pattern'] and r['inputs']==protocol['inputs'],'config identity')
    expectedabi={k:protocol['abi'][k] for k in ('platform','machine','byteorder','pointer_size','int32_size','uint16_size','double_size','UParseError')}
    require(json.dumps(r['abi'],sort_keys=True)==json.dumps(expectedabi,sort_keys=True),'typed ABI mismatch')
    expectedlibs={n:{k:v[k] for k in ('requested','resolved','sha256')} for n,v in protocol['libraries'].items()}
    require(r['libraries_before']==r['libraries_after']==expectedlibs,'library identity')
    require(loads==r['loads']==[{'name':n,'phase':p} for n in ('icuuc','icui18n') for p in ('attempt','returned')],'load trace')
    require(trace==r['trace'] and len(trace)==18,'native trace count')
    names=['version','open']+['format']*6+['close'];outputs=[]
    for index,name in enumerate(names):
        a,b=trace[index*2:index*2+2]
        expected={'call':index+1,'name':name,'phase':'attempt'}
        if name=='format':expected['input']=protocol['inputs'][index-2]
        require(a==expected and type(a['call']) is int,'attempt identity')
        require(b['call']==index+1 and type(b['call']) is int and b['name']==name and b['phase']=='returned','returned identity')
        if name=='version':require(b['result'] is None and b['version']==[76,1,0,0] and all(type(x) is int for x in b['version']),'version return')
        elif name=='open':
            require(b['handle_nonnull'] is True and i32(b['status']) and b['status']<=0,'open failed/null')
            require(type(b['pattern_utf16_units']) is int and b['pattern_utf16_units']==len(config['pattern'].encode('utf-16-le'))//2,'input units')
            require(i32(b['parse_line']) and i32(b['parse_offset']),'parse diagnostics')
            for key in ('pre_context_units','post_context_units'):require(type(b[key]) is list and len(b[key])==16 and all(type(x) is int and 0<=x<65536 for x in b[key]),'parse context units')
        elif name=='format':
            require(type(b['input']) is int and b['input']==expected['input'] and b['argument_type']=='c_double','format input')
            require(i32(b['status']) and b['status']<=0 and type(b['result']) is int and 0<=b['result']<64 and type(b['capacity_utf16']) is int and b['capacity_utf16']==64,'format status/capacity')
            units=b['units'];require(type(units) is list and len(units)==b['result'] and all(type(x) is int and 0<=x<65536 for x in units),'bounded output units')
            text=b''.join(x.to_bytes(2,'little') for x in units).decode('utf-16-le','strict')
            require(text==config['expected'][index-2],'literal marker mismatch');outputs.append(text)
        else:require(b['result'] is None,'void close')
    require(r['outputs']==outputs==config['expected'],'report output mismatch')
    if config_id=='ar_omit_few':require(r['intent_acceptance']=={'number':3,'intended':'FEW','actual':'OTHER','accepted':False},'intent/fallback conflation')
    else:require('intent_acceptance' not in r,'unexpected intent case')
    return {'category':r['category'],'outputs':outputs,'native_calls':9,'warnings':[x['status'] for x in trace if x.get('phase')=='returned' and 'status' in x and x['status']<0]}

def consume(output,source,invocation,config_id):
    root=Path(output);source=Path(source);no_symlink(root);no_symlink(source)
    protocol=strict(local(source,'protocol.json').read_text());require(digest(source/'protocol.json')==PROTOCOL_SHA,'protocol pin')
    require(digest(local(source,'isolation.py'))==protocol['environment']['helper_sha256'],'helper pin')
    manifest=strict(local(source,'source-manifest.json').read_text());require(set(manifest)==NAMES,'source manifest keys')
    for n,h in manifest.items():require(digest(local(source,n))==h,'source hash '+n)
    receipt=strict(local(root,'receipt.json').read_text())
    require(receipt['uuid']==invocation and receipt['config']==config_id and receipt['state']=='COMPLETE','receipt identity')
    require(type(receipt['returncode']) is int and receipt['returncode']==0 and receipt['timeout'] is False and receipt['group_remaining'] is False and not receipt.get('unexpected_descendants'),'process incomplete')
    require(receipt['source_sha256']==receipt['source_after_sha256']==manifest,'source drift')
    require(receipt['base_environment']==protocol['environment']['base_exact'],'base environment')
    owned=Path(receipt['owned_runtime_root']);require(owned.is_absolute() and '..' not in owned.parts and owned!=Path(owned.anchor),'owned root record')
    require(receipt['isolation']=={k:str(owned/k) for k in protocol['environment']['helper_keys']},'five locations')
    require(Path(receipt['python']).is_absolute() and Path(receipt['source_root']).is_absolute(),'absolute recorded paths')
    require(receipt['argv']==[receipt['python'],str(Path(receipt['source_root'])/'child.py'),config_id,invocation],'argv')
    for n in ('stdout.txt','stderr.txt'):require(digest(local(root,n))==receipt['output_sha256'][n],'raw hash')
    require(local(root,'stderr.txt').read_bytes()==b'','unexpected stderr; retain for review')
    events=[strict(x) for x in local(root,'stdout.txt').read_text().splitlines()]
    require(events and all(x['kind'] in ('trace','load','terminal') for x in events),'event kinds')
    terminal=[x['value'] for x in events if x['kind']=='terminal'];require(len(terminal)==1 and events[-1]['kind']=='terminal','terminal cardinality')
    r=terminal[0];require(type(r['pid']) is int and r['pid']==receipt['child_pid'],'child identity')
    require(receipt['category']==r['category'],'receipt category')
    return validate_report(r,[x['value'] for x in events if x['kind']=='trace'],[x['value'] for x in events if x['kind']=='load'],protocol,config_id,invocation)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('output');p.add_argument('uuid');p.add_argument('config');p.add_argument('--source',default=str(Path(__file__).parent));a=p.parse_args()
    print(json.dumps({'archive':consume(a.output,a.source,a.uuid,a.config),'meaning':'static archive consistency, not authenticated execution or translation approval'}))
