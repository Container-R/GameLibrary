"""Portable static consistency check, not execution/provenance authentication."""
import base64, gzip, hashlib, json, struct
from pathlib import Path

def require(ok, why):
    if not ok: raise ValueError(why)
def digest(b): return hashlib.sha256(b).hexdigest()
def integers(value):
    # No Boolean values are part of this archive schema.
    require(type(value) not in (bool,float),'non-integer numeric substitution')
    if isinstance(value,dict):
        for item in value.values(): integers(item)
    elif isinstance(value,list):
        for item in value: integers(item)

def verify(source, out):
    source,out = Path(source),Path(out)
    r=json.loads((out/'receipt.json').read_text()); integers(r)
    require(r['status']=='PASS','not PASS')
    require(set(r['source_sha256'])=={'protocol.md','run.py','reader.py','common.py','consumer.py','test_pure.py','isolation.py'},'source set')
    for name,h in r['source_sha256'].items(): require(digest((source/name).read_bytes())==h,'source hash')
    require(r['identity_before']==r['identity_after'],'identity delta')
    require(r['identity_before']['/usr/bin/ffmpeg']=='e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a','recorded binary')
    require(r['native_media_processes']==2 and r['version_processes']==1,'counts')
    old = Path(r['original_process_directory'])
    prefix=['/usr/bin/ffmpeg','-hide_banner','-loglevel','error','-nostdin','-y']
    expected=[['/usr/bin/ffmpeg','-version'],
      prefix+['-f','s16le','-ar','48000','-ac','2','-i',str(old/'input.pcm'),'-map','0:a:0','-c:a','libopus','-application','audio','-frame_duration','20','-b:a','96000','-vbr','off','-mapping_family','0','-f','opus',str(old/'encoded.opus')],
      prefix+['-i',str(old/'encoded.opus'),'-map','0:a:0','-c:a','pcm_s16le','-ar','48000','-ac','2','-f','s16le',str(old/'decoded.pcm')]]
    require(len(r['processes'])==3,'process count')
    for p,name,argv in zip(r['processes'],('version','encode','decode'),expected):
        require(p['name']==name and p['argv']==argv and p['status']=='RETURNED' and p['returncode']==0 and p['timeout_seconds']==20,'process association')
        for stream in ('stdout','stderr'):
            b=(out/f'{name}.{stream}').read_bytes()
            require(digest(b)==p[stream+'_sha256'],'raw stream hash')
            if stream=='stderr' or name!='version': require(b==b'','unexpected diagnostic')
            else: require(b.startswith(b'ffmpeg version 7.1.5-0+deb13u1 '),'version text')
    require(set(r['artifacts'])=={'input.pcm','encoded.opus','decoded.pcm','parsed.json'},'artifact set')
    require(set(r['archives'])=={'input.pcm','encoded.opus','decoded.pcm'},'archive set')
    data={}
    for name,meta in r['artifacts'].items():
        if name in r['archives']:
            chunks=[]
            for i,c in enumerate(r['archives'][name]):
                require(c['path']==f'{name}.gz.b64.{i:03d}','chunk path/order')
                b=(out/c['path']).read_bytes()
                require(0<len(b)<=65536 and len(b)==c['bytes'] and digest(b)==c['sha256'],'chunk hash/length')
                chunks.append(b)
            b=gzip.decompress(base64.b64decode(b''.join(chunks),validate=True))
            if (out/name).exists(): require((out/name).read_bytes()==b,'binary/archive disagreement')
        else: b=(out/name).read_bytes()
        require(len(b)==meta['bytes'] and digest(b)==meta['sha256'],'artifact hash/length')
        data[name]=b
    require(len(data['input.pcm'])==374636 and len(data['decoded.pcm'])==374636,'literal PCM lengths')
    for i,(left,right) in enumerate(struct.iter_unpack('<hh',data['input.pcm'])):
        require(left==128*(i%96-48) and right==96*(i%80-40),'original formula')
    parsed=json.loads(data['parsed.json']); integers(parsed)
    # Independently associate the declared page/packet durations with archive bytes.
    raw=data['encoded.opus']; off=0; pending=b''; packets=[]; gps=[]
    require(0<len(raw)<=1048576 and 0<len(parsed['pages'])<=1024,'encoded size/page count')
    serial=None; previous_audio=None; cumulative=0
    for index,page in enumerate(parsed['pages']):
        require(off+27<=len(raw) and raw[off:off+5]==b'OggS\0','page capture')
        n=raw[off+26]; require(off+27+n<=len(raw),'table bound')
        lace=raw[off+27:off+27+n]; end=off+27+n+sum(lace)
        require(end<=len(raw),'body bound')
        gp=struct.unpack_from('<q',raw,off+6)[0]; gps.append(gp)
        flags=raw[off+5]; sid=struct.unpack_from('<I',raw,off+14)[0]
        if serial is None: serial=sid
        require(sid==serial==parsed['serial'] and gp>=-1,'serial/granule domain')
        require(flags&~7==0 and bool(flags&1)==bool(pending) and bool(flags&2)==(index==0) and bool(flags&4)==(end==len(raw)),'flag semantics')
        require(page['index']==index and page['offset']==off and page['size']==end-off and page['granule']==gp and page['laces']==list(lace),'parsed page binding')
        require(page['flags']==raw[off+5] and struct.unpack_from('<I',raw,off+18)[0]==index,'page sequence/flag')
        crc=0; segment=bytearray(raw[off:end]); segment[22:26]=bytes(4)
        for byte in segment:
            crc ^= byte<<24
            for _ in range(8): crc=((crc<<1)^(0x04c11db7 if crc&0x80000000 else 0))&0xffffffff
        require(crc==page['crc']==page['computed_crc']==struct.unpack_from('<I',raw,off+22)[0],'CRC association')
        pos=off+27+n; complete=[]
        for size in lace:
            pending+=raw[pos:pos+size]; pos+=size
            if size<255:
                complete.append(len(packets)); packets.append(pending); pending=b''
        require(complete==page['completed_packets'] and len(pending)==page['pending_bytes'] and len(packets)<=1024,'packet binding')
        if not complete: require(gp==-1,'no-completion granule')
        elif complete[-1]<=1: require(gp==0,'header granule')
        else:
            require(complete[0]>=2,'header/audio mixing')
            cumulative+=960*len(complete)
            require(0<=gp<=cumulative,'granule cumulative bound')
            if previous_audio is None: require(not(flags&4) and gp==cumulative,'initial origin')
            if not(flags&4): require(gp==cumulative,'non-EOS granule')
            else: require(previous_audio is not None and gp>=previous_audio,'EOS order')
            previous_audio=gp
        off=end
    require(off==len(raw) and not pending and len(packets)>=3,'exact packet extraction')
    require(packets[0][:8]==b'OpusHead' and len(packets[0])==19,'header')
    require(struct.unpack_from('<BB',packets[0],8)==(1,2) and struct.unpack_from('<IhB',packets[0],12)==(48000,0,0),'header config')
    require(parsed['pages'][0]['completed_packets']==[0] and parsed['pages'][0]['pending_bytes']==0,'header alone')
    require(packets[1][:8]==b'OpusTags','tags identity')
    p=struct.unpack_from('<H',packets[0],10)[0]
    require(p>0 and p==parsed['header']['preskip'],'actual pre-skip')
    require(len(parsed['audio_packets'])==len(packets)-2,'audio count')
    for number,(packet,meta) in enumerate(zip(packets[2:],parsed['audio_packets']),2):
        require(2<=len(packet)<=1276 and packet[0]&3==0 and packet[0]>>3 in (1,5,9,13,15,19,23,27,31),'actual TOC')
        require(meta['packet']==number and meta['toc']==packet[0] and meta['config']==packet[0]>>3 and meta['frames']==960 and meta['bytes']==len(packet),'packet metadata')
    d=960*(len(packets)-2); g=gps[-1]; t=d-g
    require(0<t<=960 and g-p==93659 and d-p-93659==t and g-93659==p,'three count identities')
    require(parsed['coded_frames']==d and parsed['final_granule']==g and parsed['tail_trim']==t and parsed['presented_frames']==93659,'reported counts')
    return {'status':'PASS','scope':'static archive consistency only','presented_frames':93659,'final_granule':g,'coded_frames':d}

if __name__=='__main__':
    import sys
    require(len(sys.argv)==3,'usage: consumer.py SOURCE_ROOT EVIDENCE_UUID_DIR')
    print(json.dumps(verify(sys.argv[1],sys.argv[2]),sort_keys=True))
