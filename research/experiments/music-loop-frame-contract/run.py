"""Original numerical PCM fixture; actual finite offline FFmpeg filtering."""
import base64,gzip,hashlib,json,struct,subprocess,sys,wave
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
if not __debug__:raise SystemExit('optimized invocation rejected')

def need(ok,why):
    if not ok:raise RuntimeError(why)

def sha(b):return hashlib.sha256(b).hexdigest()
def command(name,cmd):
    (OUT/f'{name}-command.json').write_text(json.dumps(cmd)+'\n')
    try:p=subprocess.run(cmd,capture_output=True,timeout=10)
    except subprocess.TimeoutExpired as e:
        (OUT/f'{name}-stdout.txt').write_bytes(e.stdout or b'')
        (OUT/f'{name}-stderr.txt').write_bytes(e.stderr or b'')
        (OUT/f'{name}-status.json').write_text(json.dumps({'timeout_seconds':10})+'\n')
        raise
    (OUT/f'{name}-stdout.txt').write_bytes(p.stdout);(OUT/f'{name}-stderr.txt').write_bytes(p.stderr)
    (OUT/f'{name}-status.json').write_text(json.dumps({'exit_code':p.returncode})+'\n')
    need(p.returncode==0,f'{name} process failed {p.returncode}')
    return p.stdout.decode()

def read_wav(path):
    with wave.open(str(path),'rb') as w:
        meta={'rate':w.getframerate(),'channels':w.getnchannels(),'sample_width':w.getsampwidth(),'frames':w.getnframes(),'compression':w.getcomptype()}
        pcm=w.readframes(w.getnframes())
    need(meta['rate']==48000 and meta['channels']==2 and meta['sample_width']==2 and meta['compression']=='NONE','PCM format')
    need(len(pcm)==meta['frames']*4,'PCM byte count')
    return meta,pcm

ffmpeg=Path('/usr/bin/ffmpeg');ffprobe=Path('/usr/bin/ffprobe')
versions={str(p):command(p.name+'-version',[str(p),'-version']) for p in (ffmpeg,ffprobe)}
ideal=Fraction(48000*60*4,123);rounded=(2*ideal.numerator+ideal.denominator)//(2*ideal.denominator)
need(ideal==Fraction(3840000,41) and rounded==93659,'tempo arithmetic')
# Generator: explicit ranges and endpoint overrides, no audio assets.
raw=bytearray()
for frame in range(96539):
    value=(-111,111) if frame<480 else ((222,-222) if frame>=94139 else (100,-100))
    if frame==480:value=(1234,-2345)
    if frame==94138:value=(3456,-4567)
    raw.extend(struct.pack('<hh',*value))
source=OUT/'source.wav'
with wave.open(str(source),'wb') as w:
    w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes(raw)
meta,pcm=read_wav(source);need(meta['frames']==96539 and pcm==raw,'source roundtrip')
# Independent literal oracle differs from generator loop.
body=struct.pack('<hh',1234,-2345)+struct.pack('<hh',100,-100)*93657+struct.pack('<hh',3456,-4567)
need(len(body)==374636 and pcm[1920:376556]==body,'literal source body')
cases=[]
for name,end,expected_frames,expected in [('correct',94139,93659,body),('offbyone',94138,93658,body[:-4])]:
    path=OUT/f'{name}.wav';path.unlink(missing_ok=True)
    cmd=[str(ffmpeg),'-hide_banner','-nostdin','-y','-i',str(source),'-af',f'atrim=start_sample=480:end_sample={end},asetpts=PTS-STARTPTS','-c:a','pcm_s16le',str(path)]
    command(name,cmd);m,data=read_wav(path)
    need(m['frames']==expected_frames and data==expected,f'{name} exact PCM')
    probe=json.loads(command(name+'-probe',[str(ffprobe),'-v','error','-select_streams','a:0','-show_entries','stream=sample_rate,channels,bits_per_sample,duration_ts,time_base','-of','json',str(path)]))
    stream=probe['streams'][0]
    need(stream['sample_rate']=='48000' and stream['channels']==2 and stream['bits_per_sample']==16 and stream['time_base']=='1/48000' and stream['duration_ts']==expected_frames,'probe metadata')
    cases.append(dict(name=name,filter_end_exclusive=end,metadata=m,pcm_sha256=sha(data),first_frame=struct.unpack('<hh',data[:4]),last_frame=struct.unpack('<hh',data[-4:])))
artifacts={}
for path in [source,OUT/'correct.wav',OUT/'offbyone.wav']:
    b=path.read_bytes();packed=gzip.compress(b,mtime=0);encoded=base64.b64encode(packed)
    (OUT/(path.name+'.gz.base64')).write_bytes(encoded+b'\n')
    need(gzip.decompress(base64.b64decode(encoded,validate=True))==b,'lossless archive')
    need(len(encoded)<100000,'archive text size budget')
    artifacts[path.name]=dict(bytes=len(b),sha256=sha(b),archive_bytes=len(encoded)+1,archive_sha256=sha(encoded+b'\n'))
summary=dict(status='PASS',python=sys.version,scope='two actual offline FFmpeg PCM extractions; no FMOD/device/perception',
 source_sha256={f:sha((ROOT/f).read_bytes()) for f in ('run.py','contract.md')},
 tools={str(p):{'sha256':sha(p.read_bytes()),'version_output':versions[str(p)]} for p in (ffmpeg,ffprobe)},
 ideal_body_frames=[ideal.numerator,ideal.denominator],rounded_body_frames=rounded,source_metadata=meta,cases=cases,artifacts=artifacts)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('RESULT_JSON '+json.dumps(summary,sort_keys=True))
