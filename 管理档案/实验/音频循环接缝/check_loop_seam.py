from math import sin, pi
from pathlib import Path
import argparse
import struct
import json
import wave

FS = 48000
P = 128
A = 12000

def sample(n, phase):
    return round(A*sin(2*pi*((n+phase)%P)/P))

def join_stats(count, phase):
    end_marker,start_marker = sample(count,phase),sample(0,phase)
    end_last,start_next = sample(count-1,phase),sample(1,phase)
    delta_original = end_marker-end_last
    delta_at_join = start_marker-end_last
    after = start_next-start_marker
    return {
        "last_kept":end_last,"first_kept":start_marker,
        "unused_end_sample":end_marker,"next_kept":start_next,
        "jump_vs_natural_step":delta_at_join-delta_original,
        "actual_join_step":delta_at_join,"first_step_after_join":after,
        "first_difference_change_at_first_kept":after-delta_at_join,
    }

lengths = {"phase_matched_full_cycles":6144,
           "left_zero_opposite_slopes":6208}
out = {case:{ch:join_stats(length,phase) for ch,phase in (("left",0),("right",P//4))}
       for case,length in lengths.items()}
assert out["phase_matched_full_cycles"]["left"]["first_difference_change_at_first_kept"]==0
bad=out["left_zero_opposite_slopes"]
assert bad["left"]["first_kept"]==bad["left"]["unused_end_sample"]==0
assert bad["left"]["jump_vs_natural_step"]==0 and bad["left"]["first_difference_change_at_first_kept"]==1178
assert bad["right"]["jump_vs_natural_step"]==24000

p=argparse.ArgumentParser()
p.add_argument("--wav-directory",type=Path)
a=p.parse_args()
if a.wav_directory is not None:
    a.wav_directory.mkdir(exist_ok=True,parents=True)
    for case,length in lengths.items():
        n=length*8
        stereo=[]
        # Equal peak scale, with 10 ms ramp only at ends of the complete demonstration.
        for i in range(n):
            f=min(1,i/480,(n-i-1)/480)
            stereo.extend(round(sample(i%length,k)*f) for k in (0,P//4))
        with wave.open(str(a.wav_directory/(case+".wav")),"wb") as w:
            w.setparams((2,2,FS,0,"NONE","not compressed"))
            w.writeframes(struct.pack("<"+"h"*len(stereo),*stereo))
print(json.dumps(out,indent=2))
