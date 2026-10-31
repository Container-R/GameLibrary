import base64,gzip,hashlib,io,json,struct,sys,wave
from pathlib import Path
if sys.flags.optimize:raise SystemExit('Refusing optimized oracle')
r=Path(sys.argv[1]);s=json.loads((r/'summary.json').read_text());outputs={}
body=struct.pack('<hh',1234,-2345)+struct.pack('<hh',100,-100)*93657+struct.pack('<hh',3456,-4567)
expected={'source.wav':struct.pack('<hh',-111,111)*480+body+struct.pack('<hh',222,-222)*2400,'correct.wav':body,'offbyone.wav':body[:-4]}
for name,want in expected.items():
 archive=(r/(name+'.gz.base64')).read_bytes();b=gzip.decompress(base64.b64decode(archive.strip(),validate=True));a=s['artifacts'][name]
 assert len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256']
 assert len(archive)==a['archive_bytes'] and hashlib.sha256(archive).hexdigest()==a['archive_sha256']
 if (r/name).exists():assert b==(r/name).read_bytes()
 with wave.open(io.BytesIO(b),'rb') as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getcomptype())==(2,2,48000,'NONE')
  pcm=w.readframes(w.getnframes());assert pcm==want and w.getnframes()*4==len(want)
 outputs[name]=dict(frames=len(want)//4,pcm_bytes=len(want),first=struct.unpack('<hh',pcm[:4]),last=struct.unpack('<hh',pcm[-4:]),archive_verified=True)
for c in s['cases']:
 want=expected[c['name']+'.wav'];assert c['pcm_sha256']==hashlib.sha256(want).hexdigest()
 assert c['metadata']['frames']==len(want)//4
for name in ('ffmpeg-version','ffprobe-version','correct','offbyone','correct-probe','offbyone-probe'):
 assert json.loads((r/(name+'-status.json')).read_text())=={'exit_code':0}
assert s['ideal_body_frames']==[3840000,41] and s['rounded_body_frames']==93659
print(json.dumps(dict(status='PASS',artifacts=outputs),indent=2))
