import hashlib, struct
from pathlib import Path
N = 93659
BINARY = '/usr/bin/ffmpeg'
IDENTITY = {
BINARY:'e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a',
'/usr/lib/x86_64-linux-gnu/libopus.so.0.10.1':'621e97f23655dbf2727873b7717e3b65ae8c734f84a0848f88c21edb95202357',
'/usr/lib/x86_64-linux-gnu/libavcodec.so.61.19.101':'c01e80460c07b27883a61c53e549755b9ff052071a83f4912ff285168719219d',
'/usr/lib/x86_64-linux-gnu/libavformat.so.61.7.103':'8cde31eb30ee1ccc7d3758f60fe46dc9f342c4c9fef98cef81ecf7b681b78eeb',
'/usr/lib/x86_64-linux-gnu/libswresample.so.5.3.100':'de57f190891cf107b9c2fb51fc7d45c02c6c652f6fc7992a3c26d1f16f371674',
'/usr/lib/x86_64-linux-gnu/libavutil.so.59.39.100':'6c463f7e033438989533aea3c35e4c9a98fd6b0a637ddb8529733c0f3db1850a'}
SOURCES = ('protocol.md','run.py','reader.py','common.py','consumer.py','test_pure.py','isolation.py')
def sha(data): return hashlib.sha256(data).hexdigest()
def files(root): return {s:sha((root/s).read_bytes()) for s in SOURCES}
def identities(): return {p:sha(Path(p).read_bytes()) for p in IDENTITY}
def input_bytes():
    return b''.join(struct.pack('<hh',((i%96)-48)*128,((i%80)-40)*96) for i in range(N))
def commands(root):
    prefix = [BINARY,'-hide_banner','-loglevel','error','-nostdin','-y']
    return {'version':[BINARY,'-version'],
    'encode':prefix+['-f','s16le','-ar','48000','-ac','2','-i',str(root/'input.pcm'),'-map','0:a:0','-c:a','libopus','-application','audio','-frame_duration','20','-b:a','96000','-vbr','off','-mapping_family','0','-f','opus',str(root/'encoded.opus')],
    'decode':prefix+['-i',str(root/'encoded.opus'),'-map','0:a:0','-c:a','pcm_s16le','-ar','48000','-ac','2','-f','s16le',str(root/'decoded.pcm')]}
