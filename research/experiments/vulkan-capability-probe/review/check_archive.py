"""Literal static check of one archived negative; no fixture imports/native calls."""
import hashlib,json,sys
from pathlib import Path
UUID='c8cf0a91-18ed-4b66-afb4-11141bb7ed0d'
def require(c,m):
    if not c: raise ValueError(m)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main(root):
    root=Path(root)
    for p in (root,*root.parents): require(not p.is_symlink(),'symlink root')
    pins=json.loads(Path(__file__).with_name('archive-pins.json').read_text())
    for name,sha in pins.items():
        p=root/name
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'bad pin path')
        for a in (p,*p.parents): require(not a.is_symlink(),'symlink artifact')
        require(p.is_file() and digest(p)==sha,'hash mismatch: '+name)
    source=json.loads((root/'source-manifest.json').read_text())
    d=root/'results'/UUID
    receipt=json.loads((d/'receipt.json').read_text())
    events=[json.loads(x) for x in (d/'stdout.txt').read_text().splitlines()]
    trace=[{'call':1,'name':'create','phase':'attempt'}, {'call':1,'name':'create','phase':'returned','result':-9}]
    require(len(events)==3 and events[:2]==[{'kind':'trace','value':x} for x in trace] and events[2]['kind']=='terminal','literal trace mismatch')
    r=events[2]['value']
    require(r['trace']==trace and r['uuid']==UUID and r['pid']==receipt['child_pid'],'terminal identity')
    require(r['category']==receipt['category']=='INSTANCE_CREATION_FAILED' and type(r['create_result']) is int and r['create_result']==-9 and r['result_name']=='VK_ERROR_INCOMPATIBLE_DRIVER','negative classification')
    require(not any(x in r for x in ('instance_nonnull','count_result','count_query','fill_result','returned_count')),'unexpected later phase')
    expected_abi={'platform':'Linux','machine':'x86_64','pointer_size':8,'pointer_alignment':8,'int32_size':4,'uint32_size':4,'size':64,'alignment':8,'offsets':[0,8,16,24,32,40,48,56]}
    require(r['abi']==expected_abi,'ABI')
    loader='bbd6827e9fe418e9b9740aea57ce6d21fcea03e9876b4b17835c5a9c58f849fc'
    require(r['loader']=={'requested':'/lib/x86_64-linux-gnu/libvulkan.so.1','resolved':'/usr/lib/x86_64-linux-gnu/libvulkan.so.1.4.309','sha256':loader} and r['loader_after_sha256']==loader,'loader identity')
    require(receipt['uuid']==UUID and receipt['state']=='COMPLETE' and type(receipt['returncode']) is int and receipt['returncode']==0 and receipt['timeout'] is False and receipt['group_remaining'] is False and receipt['termination_attempts']==[],'completion')
    require(receipt['source_sha256']==receipt['source_after_sha256']==source,'source receipt')
    require(receipt['base_environment']=={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C','XDG_CONFIG_DIRS':'/etc/xdg','XDG_DATA_DIRS':'/usr/local/share:/usr/share'},'base env')
    keys=['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR']
    require(receipt['isolation']=={k:str(Path(receipt['owned_runtime_root'])/k) for k in keys},'five paths')
    require(receipt['argv']==[receipt['python'],str(Path(receipt['source_root'])/'child.py'),UUID],'argv')
    require((d/'stderr.txt').read_bytes()==b'','stderr')
    for name in ('stdout.txt','stderr.txt'): require(receipt['output_sha256'][name]==digest(d/name),'output receipt')
    return {'archive_consistency':'accepted','uuid':UUID,'observed_api_result':-9,'create_attempts':1,'create_returns':1,'enumeration_calls':0,'destroy_calls':0,'new_native_calls':0,'meaning':'scoped API-negative observation; not GPU success, hardware absence proof, or execution authentication'}
if __name__=='__main__':print(json.dumps(main(sys.argv[1]),indent=2))
