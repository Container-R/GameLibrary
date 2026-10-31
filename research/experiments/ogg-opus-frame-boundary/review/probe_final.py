"""Pure artificial framing/receipt probes, never codec input."""
import base64,copy,gzip,hashlib,json,struct,sys,tempfile,uuid
from pathlib import Path
src=Path(sys.argv[1]).resolve();sys.path.insert(0,str(src))
from test_pure import page,HEAD,TAGS,AUDIO
from reader import read
from consumer import verify
from common import commands,IDENTITY,SOURCES
sha=lambda b:hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as temp:
 out=Path(temp)/str(uuid.uuid4());out.mkdir();raw=page(0,2,0,[HEAD])+page(1,0,0,[TAGS])+page(2,0,93120,[AUDIO]*97)+page(3,4,93759,[AUDIO])
 parsed=read(raw)
 data={'input.pcm':b''.join(struct.pack('<hh',128*(i%96-48),96*(i%80-40)) for i in range(93659)), 'encoded.opus':raw,'decoded.pcm':bytes(374636),'parsed.json':json.dumps(parsed).encode()}
 r={'status':'PASS','uuid':out.name,'source_sha256':{n:sha((src/n).read_bytes()) for n in SOURCES},'identity_before':IDENTITY.copy(),'identity_after':IDENTITY.copy(),'native_media_processes':2,'version_processes':1,'original_process_directory':str(out),'processes':[],'artifacts':{},'archives':{}}
 r['source_after']=r['source_sha256'].copy();r['base_environment']={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'};r['selected_environment']={k:str(out/'environment'/k) for k in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')};r['encoded_subset_gate']='PASS';r['encoded_before_parse']={'bytes':len(raw),'sha256':sha(raw)}
 for name,argv in commands(out).items():
  p={'name':name,'argv':argv,'status':'RETURNED','returncode':0,'timeout_seconds':20,'pid':123,'attempted_utc':'2026-10-31T23:00:00+00:00','returned_utc':'2026-10-31T23:00:00+00:00'}
  for stream in ('stdout','stderr'):
   b=b'ffmpeg version 7.1.5-0+deb13u1 synthetic\n' if name=='version' and stream=='stdout' else b''
   (out/f'{name}.{stream}').write_bytes(b);p[stream+'_sha256']=sha(b)
  r['processes'].append(p)
 for name,b in data.items():
  r['artifacts'][name]={'bytes':len(b),'sha256':sha(b)}
  if name.endswith('.json'):(out/name).write_bytes(b)
  else:
   chunks=[];enc=base64.b64encode(gzip.compress(b,mtime=0))
   for i,start in enumerate(range(0,len(enc),65536)):
    chunk=enc[start:start+65536];path=f'{name}.gz.b64.{i:03d}';(out/path).write_bytes(chunk);chunks.append({'path':path,'bytes':len(chunk),'sha256':sha(chunk)})
   r['archives'][name]=chunks
 def check(name,receipt):
  (out/'receipt.json').write_text(json.dumps(receipt))
  try:verify(src,out);v='ACCEPTED'
  except Exception as e:v='REJECTED '+type(e).__name__+': '+str(e)
  print(json.dumps({'case':name,'result':v}))
 check('synthetic internally consistent control, NOT executed',r)
 bad=copy.deepcopy(r);bad['identity_before']['/usr/lib/x86_64-linux-gnu/libopus.so.0.10.1']='0'*64;bad['identity_after']=bad['identity_before'].copy();check('jointly altered libopus pin',bad)
 bad=copy.deepcopy(r);bad['selected_environment']={'HOME':'/unrelated'};check('unrelated environment map',bad)
 bad=copy.deepcopy(r);bad['uuid']='different-unbound-id';check('unbound UUID',bad)
 for label,edit in [('header channels',lambda x:x['header'].update(channels=1)),('packet stereo',lambda x:x['audio_packets'][0].update(stereo_bit=42)),('packet start',lambda x:x['audio_packets'][0].update(start_page=99)),('continuation count',lambda x:x.update(continuation_pages=500)),('granule origin',lambda x:x['pages'][2].update(granule=93121)),('Tags padding',lambda x:x['header'].update(tags_padding_bytes=0))]:
  changed=copy.deepcopy(parsed);edit(changed);b=json.dumps(changed).encode();(out/'parsed.json').write_bytes(b);bad=copy.deepcopy(r);bad['artifacts']['parsed.json']={'bytes':len(b),'sha256':sha(b)};check('rehashed '+label,bad)

