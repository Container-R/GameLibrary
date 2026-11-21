"""Render original synthetic knock/reverb controls to mono PCM16 WAV.
Python 3 stdlib, no engine, no external audio, no psychoacoustic inference.
Run: python3 -B probe.py out > observed.json
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import wave

SR = 16000
N = 19200
STOP = 1760         # 110 ms, A sends no more samples.
FADE = 1280         # 80 ms after STOP, fixed output gain ramp.
REOPEN = 4320       # 270 ms, no new input in reopen examples.
B_START = 5600      # 350 ms, B independent of A's source lifetime.
IR_LEN = 11520      # 720 ms finite synthetic response.


def make_knock():
    out = []
    for i in range(STOP):
        t = i / SR
        attack = min(1, i / 24)
        # Same knock for both sources (B uses lower gain).
        y = (0.53 * math.sin(2 * math.pi * 177 * t)
             + 0.30 * math.sin(2 * math.pi * 441 * t)
             + 0.17 * math.sin(2 * math.pi * 981 * t))
        out.append(attack * y * math.exp(-t / 0.018) * min(1, (STOP-i)/64))
    return out


def make_ir():
    # Fixed LCG for reproducible reflection timing and amplitude. Not a room measurement.
    state = 43798
    def rand():
        nonlocal state
        state = (1664525 * state + 1013904223) % (2**32)
        return state / (2**32)
    early = [(448,.52),(752,-.43),(1088,.38),(1376,-.31),(2080,.31),
             (2816,-.25),(3680,.24),(5032,-.18)]
    taps = [(i, g) for i,g in early]
    for i in range(636, IR_LEN):
        if rand() < 0.19:
            taps.append((i, (2*rand()-1)*0.11*math.exp(-i/SR/.145)))
    return taps


def response(dry, ir):
    wet = [0.0] * N
    for lag, coeff in ir:
        for i,x in enumerate(dry):
            wet[lag+i] += coeff*x
    return wet


def shift(xs, at, gain):
    return [0.0]*at + [gain*x for x in xs[:N-at]]


def add(a,b):
    return [x+y for x,y in zip(a,b,strict=True)]


def metrics(xs, start, end):
    x = xs[start:end]
    return {"peak": round(max(abs(v) for v in x),8),
            "rms": round(math.sqrt(sum(v*v for v in x)/len(x)),8)}


def pcm(xs):
    return struct.pack("<"+str(len(xs))+"h",*(round(x*32767) for x in xs))


knock = make_knock()
dry_a = knock + [0.]*(N-len(knock))
dry_b = shift(dry_a,B_START,.68)
wet_a = response(knock,make_ir())
wet_b = shift(wet_a,B_START,.68)
wet_total = add(wet_a,wet_b)
keep = wet_a
cut = [v if i<STOP else 0. for i,v in enumerate(wet_a)]
fade = [v*max(0.,min(1.,1-(i-STOP)/FADE)) for i,v in enumerate(wet_a)]
mute_reopen = [v if i<STOP or i>=REOPEN else 0. for i,v in enumerate(wet_a)]
clear_reopen = cut  # State cleared at STOP; no fresh excitation exists in this A-only case.
shared_cut = [v if i<STOP else 0. for i,v in enumerate(wet_total)]
shared_dry = add(dry_a,dry_b)

cases = {
    "01_keep_return": (dry_a,keep),
    "02_hard_cut_return": (dry_a,cut),
    "03_fade_return_80ms": (dry_a,fade),
    "04_mute_then_reopen_state_kept": (dry_a,mute_reopen),
    "05_clear_then_reopen": (dry_a,clear_reopen),
    "06_shared_return_keep": (shared_dry,wet_total),
    "07_shared_return_cut": (shared_dry,shared_cut),
}
out_dir = Path(sys.argv[1])
out_dir.mkdir(parents=True,exist_ok=True)
def wave_out(name, data):
    target=out_dir/(name+".wav")
    with wave.open(str(target),"wb") as handle:
        handle.setnchannels(1);handle.setsampwidth(2);handle.setframerate(SR)
        handle.writeframes(data)
    with wave.open(str(target),"rb") as handle:
        assert handle.readframes(len(data)//2)==data
    return hashlib.sha256(target.read_bytes()).hexdigest()

assert all(x==0 for x in dry_a[STOP:]) and any(wet_a[STOP:])
assert all(x==0 for x in cut[STOP:]) and all(x==0 for x in fade[STOP+FADE:])
assert all(x==0 for x in mute_reopen[STOP:REOPEN]) and mute_reopen[REOPEN:]==keep[REOPEN:]
assert all(x==0 for x in clear_reopen[REOPEN:])
assert any(wet_b[B_START:]) and all(x==0 for x in shared_cut[B_START:])
assert all(c[0:STOP]==wet_a[:STOP] for _,c in tuple(cases.values())[:5])
windows={"first_after_stop":[1920,3040],"reopen_no_new_send":[4320,5440],
         "second_after_its_dry":[7520,9920]}
rows={}
audition=[]
for name,(dry,wet) in cases.items():
    rendered=add(dry,wet)
    assert max(abs(v) for v in rendered)<1
    data = pcm(rendered)
    wav_hash=wave_out(name,data)
    audition += rendered+[0.0]*4000
    rows[name]={"wav_sha256":wav_hash,
        "wet_window_stats":{k:metrics(wet,*w) for k,w in windows.items()},
        "dry_window_stats":{k:metrics(dry,*w) for k,w in windows.items()}}
# B's independent linear contribution can be checked separately in the shared window.
report={"sample_rate":SR,"seconds_per_case":N/SR,"stop_sample":STOP,"fade_samples":FADE,
 "reopen_sample":REOPEN,"second_knock_sample":B_START,
 "scope":"synthetic FIR, post-return gain gates, state-clear equivalent with zero subsequent A send; not engine implementation or listening study",
 "windows_half_open":windows,"cases":rows,
 "second_source_wet_in_shared_window":metrics(wet_b,*windows["second_after_its_dry"]),
 "audition_order":list(cases),"audition_gap_samples":4000}
report["audition_sha256"]=wave_out("audition",pcm(audition))
print(json.dumps(report,indent=2))
