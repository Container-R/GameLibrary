"""Synthetic PCM diagnostic fixture, not an Unreal/cache simulation. Standard library only."""
from pathlib import Path
import array, hashlib, json, platform, sys, wave
ROOT=Path(__file__).resolve().parent
SR=48000

def code(seed,n):
    # Explicit integer PRNG: deterministic bytes, not a perceptual-quality test.
    out=[]
    for _ in range(n):
        seed=(1664525*seed+1013904223)&0xffffffff
        out.append(3000 if seed & 0x80000000 else -3000)
    return out

def pcm(values):
    a=array.array('h',values)
    if sys.byteorder!='little': a.byteswap()
    return a.tobytes()

def read(path):
    with wave.open(str(path),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,SR)
        return w.readframes(w.getnframes())

source=[0]*SR
lead=code(7,960); later=code(19,1920); body=code(29,19200)
source[0:960]=lead
source[9600:11520]=later
source[19200:38400]=body
cases={'reference':source,'whole_delayed':[0]*5760+source,'prefix_removed':source[3840:]}
result={}
for name,samples in cases.items():
    path=ROOT/(name+'.wav')
    with wave.open(str(path),'wb') as w:
        w.setparams((1,2,SR,0,'NONE','not compressed'))
        w.writeframes(pcm(samples))
    data=read(path)
    assert data==pcm(samples)
    def locate(marker):
        offset=data.find(pcm(marker))
        assert offset<0 or offset%2==0
        return None if offset<0 else offset//2
    first=next((i for i,v in enumerate(samples) if v),None)
    result[name]={'frames':len(samples),'first_nonzero_frame':first,'lead_frame':locate(lead),'later_frame':locate(later),'body_frame':locate(body),'sha256_wav':hashlib.sha256(path.read_bytes()).hexdigest()}
assert result['whole_delayed']['first_nonzero_frame']==result['prefix_removed']['first_nonzero_frame']==5760
assert result['whole_delayed']['lead_frame']==5760
assert result['whole_delayed']['later_frame']==15360
assert result['prefix_removed']['lead_frame'] is None
assert result['prefix_removed']['later_frame']==5760
assert read(ROOT/'whole_delayed.wav')[5760*2:]==read(ROOT/'reference.wav')
assert read(ROOT/'prefix_removed.wav')==read(ROOT/'reference.wav')[3840*2:]
out={'scope':'constructed PCM transformations, no engine or device timing measured','sample_rate_hz':SR,'python':platform.python_version(),'results':result}
(ROOT/'observed.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
