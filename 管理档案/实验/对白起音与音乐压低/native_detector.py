import math, struct, subprocess
from pathlib import Path
R = 48000
windows=[(200,235),(260,340),(410,450),(450,470)]
def level(i):
    return .145 if 9600<=i<11280 or 21600<=i<22560 else .4 if 11280<=i<18240 or 22560<=i<28800 else 0.
def polarity(i):
    return -1 if i%2 else 1
def encode(x): return struct.pack('<48000f',*x)
def save(name,x): Path(name+'.f32').write_bytes(encode(x))
def samples(path):
    b=Path(path).read_bytes()
    return struct.unpack('<'+'f'*(len(b)//4),b)
# Square alternating signs at a constant magnitude so output/input energy
# gives exactly the unweighted gain-power mean. Analyzer only, not audition.
save('carrier-constant-energy',(.2*polarity(i) for i in range(R)))
save('detector',(level(i)*polarity(i) for i in range(R)))
m=samples('carrier-constant-energy.f32')
for mode,attack,threshold in [('peak',120,.125),('peak',12,.125),('rms',120,.125),('peak',12,.09)]:
    command=['ffmpeg','-y','-v','error','-f','f32le','-ar','48000','-ac','1','-i','carrier-constant-energy.f32','-f','f32le','-ar','48000','-ac','1','-i','detector.f32','-filter_complex',f'[0:a][1:a]sidechaincompress=threshold={threshold}:ratio=4:knee=1:attack={attack}:release=180:detection={mode}','-c:a','pcm_f32le','-f','f32le','processed.f32']
    subprocess.run(command,check=True)
    y=samples('processed.f32')
    z=[]
    for a,b in windows:
        s,e=a*48,b*48
        z.append(10*math.log10(sum(v*v for v in y[s:e])/sum(v*v for v in m[s:e])))
    print(mode,attack,threshold,[round(x,2) for x in z])
