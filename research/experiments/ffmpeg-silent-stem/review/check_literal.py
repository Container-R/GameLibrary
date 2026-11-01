"""Independent fixed-protocol archive checker; stdlib only, no author imports/native.
Checks recorded consistency and literal waveform, not execution authenticity.
Usage: python -B check_literal.py SOURCE_ROOT [UUID]
Reviewed source pins are read from accepted-source-manifest.json beside this file.
"""
import hashlib,json,math,re,struct,sys,uuid
from pathlib import Path
from datetime import datetime,timedelta
HERE=Path(__file__).resolve().parent
ORACLE_HASH='a904ecc7a41cbc9338f0b1ee8f48ecc046835a0792d67815e3bff9c039c36f2b'
MODES=['full-normalized','short-normalized','short-unscaled']
TOOLS={'/usr/bin/ffmpeg':'e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a','/lib/x86_64-linux-gnu/libavfilter.so.10':'420fe0833b4a7062a7ed811ce854c8cbdf566979aa32657a23ffe51dbea0d053'}
def require(v,why):
    if not v:raise ValueError(why)
def digest(b):return hashlib.sha256(b).hexdigest()
def typed(a,b):
    if type(a)!=type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(typed(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(typed(x,y) for x,y in zip(a,b))
    return a==b
def parse(b):
    def pairs(xs):
        d={}
        for k,v in xs:
            require(k not in d,'duplicate key');d[k]=v
        return d
    def bad(s):raise ValueError('nonfinite JSON')
    def real(s):
        x=float(s);require(math.isfinite(x),'overflow JSON');return x
    return json.loads(b,object_pairs_hook=pairs,parse_constant=bad,parse_float=real)
def check(root,uid=None):
    root=Path(root)
    ob=(HERE/'INDEPENDENT-LITERAL-ORACLE.json').read_bytes();require(digest(ob)==ORACLE_HASH,'literal pin');oracle=parse(ob)
    pins=parse((HERE/'accepted-source-manifest.json').read_bytes())
    mb=(root/'SOURCE-SHA256.json').read_bytes();require(typed(parse(mb),pins),'reviewed source manifest')
    for name,h in pins.items():require(digest((root/name).read_bytes())==h,'actual source '+name)
    summary=parse((root/'summary.json').read_bytes())
    uid=uid or summary['uuid'];require(type(uid)is str and str(uuid.UUID(uid))==uid,'UUID')
    out=root/'evidence'/uid;rb=(out/'receipt.json').read_bytes();r=parse(rb)
    require(typed(summary,{'status':'PASS','uuid':uid,'receipt_sha256':digest(rb),'processes':4,'mixing_conditions':3}),'summary')
    require(set(r)=={'status','uuid','original_directory','manifest_sha256','source_before','source_after','tools_before','tools_after','inputs','processes','outputs'},'receipt fields')
    require(r['status']=='PASS' and r['uuid']==uid and r['manifest_sha256']==digest(mb),'receipt association')
    for k in ['source_before','source_after']:require(typed(r[k],pins),k)
    for k in ['tools_before','tools_after']:require(typed(r[k],TOOLS),k)
    original=Path(r['original_directory']);require(original.is_absolute() and '..' not in original.parts and original.name==uid and original.parent.name=='evidence','original path')
    def archived(name,meta,expected):
        raw=(out/(name+'.hex')).read_bytes();require(re.fullmatch(rb'(?:[0-9a-f]{2})*\n',raw)is not None,'canonical hex')
        b=bytes.fromhex(raw.decode());require(b==expected,'literal bytes '+name)
        require(typed(meta,{'bytes':len(b),'sha256':digest(b)}),'byte metadata')
        binary=out/(name+'.f32le')
        if binary.exists():require(binary.read_bytes()==b,'optional raw')
        return b
    inputs={'A':bytes.fromhex('0000003f')*4096,'B-full':bytes(16384),'B-short':bytes(8192)}
    require(set(r['inputs'])==set(inputs),'input set')
    ih={}
    for name,b in inputs.items():
        require(digest(b)==oracle['inputs'][name]['sha256'],'input oracle');archived(name,r['inputs'][name],b);ih[name]=digest(b)
    require(set(r['outputs'])==set(MODES),'output set')
    for mode in MODES:
        entry=oracle['outputs'][mode];expected=b''.join(bytes.fromhex(bits)*(end-start) for start,end,bits in entry['segments_start_inclusive_end_exclusive'])
        require(digest(expected)==entry['sha256'],'output oracle')
        rec=r['outputs'][mode];require(set(rec)=={'archive','check'},'output record')
        b=archived(mode,rec['archive'],expected);require(all(math.isfinite(x[0]) for x in struct.iter_unpack('<f',b)),'finite output')
        require(typed(rec['check'],{'frames':4096,'bytes':16384,'all_samples_equal':True}),'derived check')
    ps=r['processes'];require(type(ps)is list and len(ps)==4,'process count');previous=None
    for mode,p in zip(['version']+MODES,ps):
        require(set(p)=={'name','argv','cwd','environment','timeout_seconds','status','pid','attempted_utc','returned_utc','returncode','stdout_sha256','stderr_sha256','inputs_before','inputs_after'},'process schema')
        if mode=='version':argv=['/usr/bin/ffmpeg','-version']
        else:
            bn='B-full' if mode=='full-normalized' else 'B-short';normal='0' if mode=='short-unscaled' else '1'
            graph='[0:a]asetnsamples=n=256:p=0[a];[1:a]asetnsamples=n=256:p=0[b];[a][b]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 1:normalize='+normal+'[out]'
            argv=['/usr/bin/ffmpeg','-hide_banner','-loglevel','error','-nostdin','-n','-f','f32le','-ar','48000','-ac','1','-i',str(original/'A.f32le'),'-f','f32le','-ar','48000','-ac','1','-i',str(original/(bn+'.f32le')),'-filter_complex_threads','1','-filter_complex',graph,'-map','[out]','-c:a','pcm_f32le','-f','f32le',str(original/(mode+'.f32le'))]
        env={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
        env.update({k:str(original/'environment'/mode/k) for k in ['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR']})
        for key,want in {'name':mode,'argv':argv,'cwd':str(original),'environment':env,'timeout_seconds':20,'status':'RETURNED','returncode':0,'inputs_before':ih,'inputs_after':ih}.items():require(typed(p[key],want),'process '+key)
        require(type(p['pid'])is int and p['pid']>0,'pid')
        require(all(type(p[k])is str for k in ['attempted_utc','returned_utc']),'timestamp strings')
        start,end=[datetime.fromisoformat(p[k]) for k in ['attempted_utc','returned_utc']]
        require(start.utcoffset()==timedelta(0) and end.utcoffset()==timedelta(0) and start<=end,'time order')
        require(previous is None or previous<=start,'sequential');previous=end
        for stream in ['stdout','stderr']:
            raw=(out/(mode+'.'+stream)).read_bytes();require(digest(raw)==p[stream+'_sha256'],'raw hash')
            if mode=='version' and stream=='stdout':
                first=raw.splitlines()[0] if raw else b'';banner=b'ffmpeg version 7.1.5-0+deb13u1';require(first==banner or first.startswith(banner+b' '),'version')
            else:require(raw==b'','unexpected diagnostic')
    return {'uuid':uid,'recorded_processes':4,'unique_mixes':3,'literal_output_frames_each':4096,'scope':'archive consistency, not authenticated execution'}
if __name__=='__main__':print(json.dumps(check(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None),sort_keys=True))
