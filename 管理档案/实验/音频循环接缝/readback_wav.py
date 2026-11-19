from pathlib import Path
import json
import struct
import sys
import wave

d=Path(sys.argv[1]) if len(sys.argv)>1 else Path('generated')
control = json.loads(Path(__file__).with_name('observed.json').read_text())
checks={}
for case,k in (("phase_matched_full_cycles",6144),("left_zero_opposite_slopes",6208)):
    with wave.open(str(d/(case+".wav"))) as f:
        assert (f.getnchannels(),f.getsampwidth(),f.getframerate()) == (2,2,48000)
        frames=f.getnframes()
        assert frames==8*k
        f.setpos(k-1)
        samples=struct.unpack("<hhhhhh",f.readframes(3))
        marks={}
        for i,channel in enumerate(("left","right")):
            old,new,nxt=samples[i::2]
            m=control[case][channel]
            assert [old,new,nxt]==[m["last_kept"],m["first_kept"],m["next_kept"]]
            marks[channel]=[old,new,nxt]
        checks[case]={"frames":frames,"first_internal_seam_triplets":marks}
print(json.dumps(checks,indent=2))
