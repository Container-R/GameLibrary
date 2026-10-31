"""Independent observed-stream count oracle; no codec or author imports."""
import hashlib,json,struct,sys,base64,zlib
from pathlib import Path
root=Path(sys.argv[1]);r=json.loads((root/'receipt.json').read_text())
def need(v,msg):
 if not v:raise ValueError(msg)
sha=lambda b:hashlib.sha256(b).hexdigest()
def media(name):
 if (root/name).is_file():return (root/name).read_bytes()
 chunks=[]
 for i,c in enumerate(r['archives'][name]):
  need(c['path']==f'{name}.gz.b64.{i:03d}','chunk path');b=(root/c['path']).read_bytes();need(sha(b)==c['sha256'] and len(b)==c['bytes'],'chunk hash');chunks.append(b)
 dec=zlib.decompressobj(31);b=dec.decompress(base64.b64decode(b''.join(chunks),validate=True),1048577)
 need(len(b)<=1048576 and dec.eof and not dec.unused_data and not dec.unconsumed_tail,'bounded archive')
 return b
need(r['status']=='PASS' and r['uuid']==root.name,'receipt')
need([p['name'] for p in r['processes']]==['version','encode','decode'],'process order')
for p in r['processes']:
 need(type(p['returncode']) is int and p['returncode']==0 and p['status']=='RETURNED','process result')
 for stream in ('stdout','stderr'):
  b=(root/(p['name']+'.'+stream)).read_bytes();need(sha(b)==p[stream+'_sha256'],'log hash')
  if stream=='stderr' or p['name']!='version':need(b==b'','diagnostic')
need(r['source_after']==r['source_sha256'] and r['identity_after']==r['identity_before'],'identity drift')
for name in ('input.pcm','encoded.opus','decoded.pcm'):
 b=media(name);need(len(b)==r['artifacts'][name]['bytes'] and sha(b)==r['artifacts'][name]['sha256'],'media hash')
input_pcm=media('input.pcm');need(len(input_pcm)==93659*4,'input frames')
for i,(l,rr) in enumerate(struct.iter_unpack('<hh',input_pcm)):
 need((l,rr)==((i%96-48)*128,(i%80-40)*96),'input formula')
raw=media('encoded.opus');offset=0;packets=[];pending=b'';pages=[]
while offset<len(raw):
 need(raw[offset:offset+5]==b'OggS\0','capture')
 flags=raw[offset+5];gp,serial,seq=struct.unpack_from('<qII',raw,offset+6)
 n=raw[offset+26];laces=raw[offset+27:offset+27+n];start=offset+27+n;end=start+sum(laces)
 need(end<=len(raw) and seq==len(pages),'bounds/sequence')
 completed=[];pos=start
 for size in laces:
  pending+=raw[pos:pos+size];pos+=size
  if size<255:completed.append(len(packets));packets.append(pending);pending=b''
 pages.append({'seq':seq,'granule':gp,'flags':flags,'completed':completed});offset=end
need(offset==len(raw) and not pending,'exact packets')
need(len(pages)==4 and pages[0]['completed']==[0] and pages[1]['completed']==[1],'observed layout')
need(all(not(p['flags']&1) for p in pages),'observed no continuation')
head=packets[0];need(len(head)==19 and head[:8]==b'OpusHead','head')
version,channels,preskip,rate,gain,family=struct.unpack_from('<BBHIhB',head,8)
need((version,channels,rate,gain,family)==(1,2,48000,0,0),'header values')
need(packets[1].startswith(b'OpusTags'),'tags')
frames=0
for pkt in packets[2:]:
 need(2<=len(pkt)<=1276 and pkt[0]&3==0,'single frame')
 cfg=pkt[0]>>3
 # Independently derive milliseconds from the RFC table groups, not an author duration helper.
 duration=([10,20,40,60][cfg%4] if cfg<12 else [10,20][cfg%2] if cfg<16 else [2.5,5,10,20][cfg%4])
 need(duration==20,'actual duration');frames+=int(duration*48)
need(pages[2]['granule']==960*len(pages[2]['completed']) and not(pages[2]['flags']&4),'initial zero origin')
g=pages[-1]['granule'];trim=frames-g;decoded=len(media('decoded.pcm'))
need(pages[-1]['flags']&4 and g>=pages[2]['granule'],'EOS')
need(preskip>0 and 0<trim<=960 and g-preskip==93659 and decoded==93659*4,'frame oracle')
need(g-93659==preskip and (frames-preskip)-93659==trim,'two wrong counts')
print(json.dumps({'uuid':r['uuid'],'accepted':True,'processes':3,'media_processes':2,'pages':len(pages),'audio_packets':len(packets)-2,'pre_skip':preskip,'granule':g,'coded_frames':frames,'tail_trim':trim,'presented_frames':decoded//4,'source_sha256':r['source_sha256'],'artifacts':r['artifacts']},indent=2))
