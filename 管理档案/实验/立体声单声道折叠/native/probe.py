"""Deterministic synthesized PCM through actual FFmpeg pan. No engine/human test.
Run python probe.py; output JSON on stdout, generated WAVs beside script.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess, wave, struct, math, json, hashlib
ROOT=Path(__file__).resolve().parent
FS=48000; N=FS; A=4096
# Quantize one period, derive the opposite half by integer negation: exact symmetry.
def sine(period):
 half=[2*round((A/2)*math.sin(2*math.pi*k/period)) for k in range(period//2)]
 return half+[-x for x in half]
t750=sine(64);t1500=sine(32)
def signal(table):return [table[k%len(table)] for k in range(N)]
a=signal(t750);b=signal(t1500)
def delayed(x):return [0]*32+x[:-32]
zero=[0]*N
cases={'identical_750':(a,a),'opposite_750':(a,[-x for x in a]),
       'delay32_750':(a,delayed(a)),'delay32_1500':(b,delayed(b)),
       'right_only_cue_1500':(zero,b)}
def write(path,channels):
 values=[v for frame in zip(*channels) for v in frame]
 with wave.open(str(path),'wb') as w:
  w.setparams((len(channels),2,FS,0,'NONE','not compressed'))
  w.writeframes(struct.pack('<'+'h'*len(values),*values))
def read(path):
 with wave.open(str(path),'rb') as w:
  assert w.getframerate()==FS and w.getsampwidth()==2 and w.getnframes()==N
  nc=w.getnchannels();v=struct.unpack('<'+'h'*(N*nc),w.readframes(N))
 return [list(v[k::nc]) for k in range(nc)]
def metric(x):
 # Excludes startup/end: covers an integer count of both tone periods.
 y=x[1024:47104]
 return {'peak_pcm':max(map(abs,y)),'sum_squares_pcm':sum(v*v for v in y),
         'rms_pcm':math.sqrt(sum(v*v for v in y)/len(y)),
         'nonzero_samples':sum(v!=0 for v in y)}
def command(args):
 r=subprocess.run(args,check=True,capture_output=True);return r.stdout
version=command(['ffmpeg','-version']).decode().splitlines()[0]
filters={'fold':'pan=mono|c0=0.5*c0+0.5*c1',
         'left_replicate':'pan=stereo|c0=c0|c1=c0',
         'fold_replicate':'pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1'}
rows={}
with TemporaryDirectory(prefix='mono-downmix-') as tmp:
 for name,(left,right) in cases.items():
  src=Path(tmp)/(name+'.wav');write(src,[left,right])
  row={'input_left':metric(left),'input_right':metric(right),'outputs':{}}
  modes=['fold'] if name!='right_only_cue_1500' else list(filters)
  for mode in modes:
   output=ROOT/(name+'_'+mode+'.wav')
   command(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-af',filters[mode],'-c:a','pcm_s16le','-fflags','+bitexact','-flags:a','+bitexact',str(output)])
   channels=read(output)
   expected=[round((x+y)*0.5) for x,y in zip(left,right)]
   if mode=='left_replicate':expected=left
   assert all(x==expected for x in channels),(name,mode)
   row['outputs'][mode]={'channels':len(channels),'metrics':[metric(x) for x in channels],
                        'all_samples_match_explicit_matrix':True,
                        'sha256_wav':hashlib.sha256(output.read_bytes()).hexdigest()}
  rows[name]=row
assert rows['identical_750']['outputs']['fold']['metrics'][0]==metric(a)
for name in ['opposite_750','delay32_750']:
 assert rows[name]['input_left']['rms_pcm']>0 and rows[name]['input_right']['rms_pcm']>0
 assert rows[name]['outputs']['fold']['metrics'][0]['peak_pcm']==0
assert rows['delay32_1500']['outputs']['fold']['metrics'][0]==metric(b)
assert rows['right_only_cue_1500']['outputs']['left_replicate']['metrics'][0]['peak_pcm']==0
assert rows['right_only_cue_1500']['outputs']['fold_replicate']['metrics'][0]['peak_pcm']==A//2
print(json.dumps({'scope':'actual FFmpeg pan on synthesized integer PCM, no perceptual or game-runtime claims',
 'ffmpeg':version,'sample_rate':FS,'frames':N,'amplitude_pcm':A,'delay_samples':32,
 'metrics_interval_half_open':[1024,47104],'filters':filters,'cases':rows},indent=2))
