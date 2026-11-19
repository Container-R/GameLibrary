"""Contrast full-scale sample checks with oversampled meters, using float PCM."""
from array import array
from math import cos, sin, tau, pi, log10
from struct import pack
from subprocess import run, PIPE
from sys import byteorder

assert byteorder == 'little', 'the raw array view requires little-endian host'
import json, re

fs=48_000

def source(freq, amp, phase):
    out=bytearray()
    n=fs
    fade=fs//20
    for i in range(n):
        envelope = (1-cos(pi*min(1,i/fade,(n-1-i)/fade)))*.5
        out += pack("<f",envelope*amp*sin(tau*freq*i/fs+phase))
    return out

def ff(data, *extra, rate=fs):
    return run(["ffmpeg","-nostats","-f","f32le","-ar",str(rate),"-ac","1","-i","pipe:0",*extra],
               input=data,stdout=PIPE,stderr=PIPE,check=True)

def capture(data, rate, kind):
    raw=ff(data,"-af",f"aresample={rate}:osf={'flt' if kind=='f32' else 's16'}","-f",f"{kind}le","pipe:1").stdout
    return array("f" if kind=="f32" else "h",raw)

def inspect(data,src_rate=fs,pad_silent_tail=False):
    filters=("apad=pad_dur=0.020," if pad_silent_tail else "")+"ebur128=peak=sample+true"
    out=ff(data,"-af",filters,"-f","null","-",rate=src_rate)
    s=out.stderr.decode().rsplit("Summary:",1)[1]
    meter=re.findall(r"Peak:\s+([\d.+-]+)\s+dBFS",s)
    assert len(meter)==2
    raw=array("f",data)
    y={"sample_dbfs":round(20*log10(max(map(abs,raw))),4),
       "ffmpeg_summary_sample_dbfs":float(meter[0]), "ffmpeg_summary_true_dbtp":float(meter[1])}
    return y

single=source(12_000,.8*2**.5,pi/4)
control=source(1_000,.8,0)
layer=source(12_000,.4*2**.5,pi/4)
values=array("f",layer)
sum2=array("f",(a+b for a,b in zip(values,values))).tobytes()
assert sum2 == single
result={"version":run(["ffmpeg","-version"],stdout=PIPE,check=True,text=True).stdout.splitlines()[0],
        "input48_control_1k":inspect(control),
        "input48_12k":inspect(single),
        "isolated_layer":inspect(layer),
        "two_identical_aligned_layers":inspect(sum2)}
for rate in (44_100, 96_000):
    floating=capture(single,rate,"f32")
    fixed=capture(single,rate,"s16")
    assert len(floating)==len(fixed)==rate
    gate=sum(abs(x)>1 for x in floating)
    saturated=sum(x in (-32768,32767) for x in fixed)
    assert all((b == 32767 if a>1 else b ==-32768) for a,b in zip(floating,fixed) if abs(a)>1)
    result[f"same_input_converted_to_{rate}"]={
        "float_output":inspect(floating.tobytes(),rate),
        "float_samples_above_unit":gate,
        "s16_rails":saturated,
        "samples":len(floating)
    }
def clicks(pos):
    x=bytearray(4*fs)
    x[4*pos:4*pos+8]=pack("<ff",.82,.85)
    return x

tail=clicks(fs-4)
result["known_silent_tail"]={
    "short_capture": inspect(tail),
    "same_with_20ms_silence": inspect(tail,pad_silent_tail=True),
    "pair_placed_100_samples_before_eof": inspect(clicks(fs-100)),
}
t=result["known_silent_tail"]
assert t["short_capture"]["ffmpeg_summary_true_dbtp"]<0
assert t["same_with_20ms_silence"]["ffmpeg_summary_true_dbtp"]>0
assert t["same_with_20ms_silence"]==t["pair_placed_100_samples_before_eof"]
assert result["input48_12k"]["sample_dbfs"]<0<result["input48_12k"]["ffmpeg_summary_true_dbtp"]
assert result["input48_control_1k"]["ffmpeg_summary_true_dbtp"]<0
assert result["isolated_layer"]["ffmpeg_summary_true_dbtp"]<0<result["two_identical_aligned_layers"]["ffmpeg_summary_true_dbtp"]
for rate in (44_100,96_000):
    x=result[f"same_input_converted_to_{rate}"]
    assert x["float_samples_above_unit"]>0 and x["s16_rails"]>0
print(json.dumps(result,indent=2))
