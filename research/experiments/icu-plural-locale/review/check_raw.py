"""Independent literal raw oracle; standard library only, no native/author imports."""
import hashlib,json,sys
from pathlib import Path

def need(value,msg):
    if not value:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
root=Path(sys.argv[1]);source=Path(sys.argv[2]);batch=read(root/'batch.json')
expected={
'en_full':['OTHER','ONE','OTHER','OTHER','OTHER','OTHER'],
'ar_full':['ZERO','ONE','TWO','FEW','MANY','OTHER'],
'ar_omit_few':['ZERO','ONE','TWO','OTHER','MANY','OTHER']}
full='{0, plural, zero {ZERO} one {ONE} two {TWO} few {FEW} many {MANY} other {OTHER}}'
omit='{0, plural, zero {ZERO} one {ONE} two {TWO} many {MANY} other {OTHER}}'
nums=[0,1,2,3,11,100];names=['version','open']+['format']*6+['close']
need(batch['state']=='COMPLETE_EXPECTED_OUTPUTS' and batch['native_child_spawn_count']==3 and batch['not_started']==[],'batch')
need([c['config'] for c in batch['configs']]==list(expected),'config order')
pins=read(source/'source-manifest.json')
for name,digest in pins.items():need(sha(source/name)==digest,'source pin')
rows=[]
for config in batch['configs']:
    cid=config['config'];out=root/config['uuid'];r=read(out/'receipt.json')
    need(sha(out/'receipt.json')==config['receipt_sha256'],'receipt hash')
    need(r['returncode']==0 and r['timeout'] is False and r['group_remaining'] is False,'process')
    need(r['source_sha256']==r['source_after_sha256']==pins,'source before/after')
    for filename in ('stdout.txt','stderr.txt'):need(sha(out/filename)==r['output_sha256'][filename],'rawhash')
    need((out/'stderr.txt').read_bytes()==b'','stderr')
    events=[json.loads(line) for line in (out/'stdout.txt').read_text().splitlines()]
    need([e['kind'] for e in events]==['load']*4+['trace']*18+['terminal'],'event order')
    t=events[-1]['value'];trace=[e['value'] for e in events[4:-1]]
    need(t['trace']==trace and t['uuid']==config['uuid'] and t['config']==cid,'raw identity')
    need(t['locale']==('en' if cid=='en_full' else 'ar') and t['pattern']==(omit if cid=='ar_omit_few' else full),'literal config')
    need(t['inputs']==nums and t['libraries_before']==t['libraries_after'],'inputs/libs')
    outputs=[];statuses=[]
    for i,name in enumerate(names):
        a,b=trace[2*i:2*i+2]
        need(a['name']==b['name']==name and a['phase']=='attempt' and b['phase']=='returned' and a['call']==b['call']==i+1,'lifecycle')
        if name=='version':need(b['version']==[76,1,0,0] and b['result'] is None,'version')
        elif name=='open':need(b['handle_nonnull'] is True and type(b['status']) is int and b['status']<=0,'open');statuses.append(b['status'])
        elif name=='format':
            need(type(a['input']) is int and a['input']==b['input']==nums[i-2] and b['argument_type']=='c_double','number')
            need(type(b['status']) is int and b['status']<=0 and 0<=b['result']<64 and b['capacity_utf16']==64,'status/length')
            units=b['units'];need(len(units)==b['result'] and all(type(x) is int and 0<=x<65536 for x in units),'UTF16')
            text=b''.join(x.to_bytes(2,'little') for x in units).decode('utf-16-le','strict')
            need(text==expected[cid][i-2],'independent literal oracle');outputs.append(text);statuses.append(b['status'])
        else:need(b['result'] is None,'close')
    need(t['outputs']==outputs,'summary outputs')
    if cid=='ar_omit_few':need(t['intent_acceptance']=={'number':3,'intended':'FEW','actual':'OTHER','accepted':False},'fallback intent')
    rows.append({'config':cid,'uuid':config['uuid'],'outputs':outputs,'statuses':statuses,'attempts':9,'returns':9})
print(json.dumps({'batch':batch['uuid'],'accepted':True,'children':3,'total_attempts':27,'total_returns':27,'configurations':rows},indent=2))
