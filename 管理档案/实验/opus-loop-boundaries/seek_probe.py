"""Inspect Ogg metadata, then compare libsndfile complete and seeked PCM."""
import ctypes as C
import hashlib
from pathlib import Path
import math
import random
import struct
import subprocess
import wave

N = 94001
rng = random.Random(274)
data = bytearray()
for i in range(N):
    t = i / 48000
    left = 6500*math.sin(2*math.pi*(410*t+120*t*t)) + rng.randrange(-2500,2501)
    right = 6000*math.sin(2*math.pi*(701*t+370*t*t)) + rng.randrange(-2300,2301)
    if 62501 <= i < 62541:
        left += (i % 7 - 3) * 3000
    if 63203 <= i < 63244:
        right += (i % 5 - 2) * 4000
    data += struct.pack('<hh',round(left),round(right))
with wave.open('seek-input.wav','wb') as w:
    w.setparams((2,2,48000,0,'NONE','not compressed'))
    w.writeframes(data)
subprocess.run(['ffmpeg','-y','-v','error','-i','seek-input.wav','-c:a','libopus',
                '-b:a','128k','-frame_duration','20','-page_duration','100000',
                'seek-test.opus'],check=True)

def pages(data):
    cursor = 0
    while cursor < len(data):
        assert data[cursor:cursor+4] == b'OggS'
        payload = cursor + 27 + data[cursor+26]
        end = payload + sum(data[cursor+27:payload])
        yield (cursor, payload, end, struct.unpack_from('<q',data,cursor+6)[0])
        cursor = end
    assert cursor == len(data)

def crc(page):
    acc = 0
    for b in page:
        acc ^= b << 24
        for _ in range(8):
            acc = ((acc << 1) ^ (0x04c11db7 if acc & (1<<31) else 0)) & 0xffffffff
    return acc

raw = bytearray(Path('seek-test.opus').read_bytes())
info = list(pages(raw))
assert len(info)>6 and raw[info[0][1]:info[0][1]+8]==b'OpusHead'
preskip=struct.unpack_from('<H',raw,info[0][1]+10)[0]
assert info[-1][3]==preskip+N and raw[info[-1][0]+5]&4
for start,_,end,gp in info:
    check=struct.unpack_from('<I',raw,start+22)[0]
    page=bytearray(raw[start:end]);page[22:26]=bytes(4)
    assert crc(page)==check
for start,_,end,gp in info[2:]:
    if gp>=0:
        struct.pack_into('<q',raw,start+6,gp+48000)
        raw[start+22:start+26]=bytes(4)
        struct.pack_into('<I',raw,start+22,crc(raw[start:end]))
Path('seek-shifted.opus').write_bytes(raw)
print('audio pages:',len(info)-2,'pre-skip:',preskip,'EOS granule:',info[-1][3],
      'shifted:',info[-1][3]+48000)
ff=[subprocess.check_output(['ffmpeg','-v','error','-i',p,'-f','f32le','-'])
    for p in ('seek-test.opus','seek-shifted.opus')]
assert ff[0]==ff[1] and len(ff[0])==N*2*4
print('FFmpeg float PCM: same',len(ff[0])//8,'frames; sha256=',hashlib.sha256(ff[0]).hexdigest())

s=C.CDLL('libsndfile.so.1')
class Info(C.Structure):
    _fields_=[('frames',C.c_longlong),('samplerate',C.c_int),('channels',C.c_int),
              ('format',C.c_int),('sections',C.c_int),('seekable',C.c_int)]
def wrap(name,res,*args):
    f=getattr(s,name); f.restype=res;f.argtypes=args;return f
open_=wrap('sf_open',C.c_void_p,C.c_char_p,C.c_int,C.POINTER(Info))
close=wrap('sf_close',C.c_int,C.c_void_p)
seek=wrap('sf_seek',C.c_longlong,C.c_void_p,C.c_longlong,C.c_int)
read=wrap('sf_readf_float',C.c_longlong,C.c_void_p,C.POINTER(C.c_float),C.c_longlong)
print(wrap('sf_version_string',C.c_char_p)().decode())
def begin(path):
    i=Info(); f=open_(path.encode(),0x10,C.byref(i))
    assert f and i.samplerate==48000 and i.channels==2 and i.seekable
    return f,i.frames

def pull(f,n):
    a=(C.c_float*(2*n))()
    got=read(f,a,n)
    return got,list(a[:2*got])

def rms(actual, reference):
    assert len(actual)==len(reference) and actual
    return math.sqrt(sum((a-b)**2 for a,b in zip(actual,reference))/len(actual))

unshifted_reference = None
control_reads = {}
for fname in ('seek-test.opus','seek-shifted.opus'):
    f,total=begin(fname)
    got,reference=pull(f,N+10);close(f)
    print(fname,'metadata frames=',total,'read=',got)
    assert total==got==N
    if unshifted_reference is None:
        unshifted_reference = reference
    print('  full-decode RMS against zero-origin fixture=',rms(reference,unshifted_reference))
    if fname == 'seek-shifted.opus':
        for offset in (-312,0,312):
            print('  shifted full PCM frames 1000:3000 vs zero-origin start',1000+offset,'RMS=',
                  rms(reference[2000:6000],unshifted_reference[2*(1000+offset):2*(3000+offset)]))
    for label,target in (('fresh early',713),('fresh middle',62513),
                         ('backward re-entry',62513),('off by one control',62514)):
        f,_=begin(fname)
        if label=='backward re-entry':
            assert seek(f,63214,0)==63214 and pull(f,311)[0]==311
        landed=seek(f,target,0)
        count,observed=pull(f,701); after=seek(f,0,1);close(f)
        if fname == 'seek-test.opus':
            control_reads[label]=observed
        else:
            print('  seek PCM RMS vs zero-origin same target=',rms(observed,control_reads[label]))
        expected=62513 if label=='off by one control' else target
        score=[rms(observed,reference[2*(expected+lag):2*(expected+lag+701)]) for lag in range(-2,3)]
        best=min(range(-2,3),key=lambda lag:score[lag+2])
        print(label,'landed=',landed,'read=',count,'after=',after,'best lag=',best,
              'error -1/0/+1=',*[f'{x:.8f}' for x in score[1:4]])
        assert (landed,count,after)==(target,701,target+701)
        if fname == 'seek-test.opus':
            assert best==(1 if label=='off by one control' else 0)
        elif best!=(1 if label=='off by one control' else 0):
            width=24
            head=observed[:2*width]
            approximate=min(range(0,N-width), key=lambda pos: sum((a-b)**2 for a,b in zip(head,reference[2*pos:2*(pos+width)])))
            other=reference[2*approximate:2*(approximate+701)]
            err=rms(observed,other)
            print('  best entire-stream start for first 24 frames=',approximate,'701-frame RMS there=',round(err,8))

# Compare fresh natural open to explicit seek(0) and last frames to a known
# zero-origin decode from the same packets, then explicitly hit EOF.
for fname in ('seek-test.opus','seek-shifted.opus'):
    f,length=begin(fname)
    n,raw_head=pull(f,128);close(f);assert n==128
    f,length=begin(fname)
    head_cursor=seek(f,0,0);hn,head=pull(f,128)
    tail_cursor=seek(f,length-128,0);tn,tail=pull(f,256)
    eof=pull(f,1)[0];close(f)
    assert (head_cursor,hn,tail_cursor,tn,eof)==(0,128,N-128,128,0)
    print(fname,'fresh head RMS=',f'{rms(raw_head,unshifted_reference[:256]):.8f}',
          'seek(0) head RMS=',f'{rms(head,unshifted_reference[:256]):.8f}',
          'tail count=',tn,'seek tail RMS=',f'{rms(tail,unshifted_reference[-256:]):.8f}',
          'EOF frames=',eof)
