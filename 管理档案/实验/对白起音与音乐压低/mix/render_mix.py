#!/usr/bin/env python3
"""Render a fixed synthetic voice over an original competing music stem."""
import array
import json
import math
import pathlib
import subprocess
import sys
import tempfile
import wave

RATE = 48000
N = RATE * 3
STEP = RATE // 200
DETECTOR_RMS = .002
FIRST_START = RATE // 2

def ffmpeg(args, pcm=None):
    return subprocess.run(["ffmpeg", "-v", "error", *args], input=pcm,
                          capture_output=True, check=True).stdout

def read_float(buf):
    samples = array.array("f")
    samples.frombytes(buf)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples

def to_float(data):
    samples = array.array("f", data)
    if sys.byteorder != "little":
        samples.byteswap()
    return samples.tobytes()

def rms(seq):
    return math.sqrt(math.fsum(x*x for x in seq)/len(seq))

def speech(text, target_peak):
    raw = read_float(ffmpeg(["-f", "lavfi", "-i",
                             f"flite=voice=slt:text='{text}'",
                             "-ar", str(RATE), "-ac", "1", "-f", "f32le", "-"]))
    scale = target_peak / max(abs(x) for x in raw)
    pcm = [x * scale for x in raw]
    hits = [i for i in range(0, len(pcm), STEP)
            if rms(pcm[i:i+STEP]) >= DETECTOR_RMS]
    assert hits
    return pcm[hits[0]:min(len(pcm),hits[-1]+STEP)]

def save_wav(path, data):
    assert max(abs(v) for v in data) < 1
    pcm = array.array("h", (round(v*32767) for v in data))
    if sys.byteorder != "little":
        pcm.byteswap()
    with wave.open(str(path), "wb") as w:
        w.setparams((1, 2, RATE, len(data), "NONE", "not compressed"))
        w.writeframes(pcm.tobytes())

def music(i):
    t = i / RATE
    # Original A-minor harmony with deliberately overlapping midrange partials.
    notes = (220., 261.6256, 329.6276, 440.)
    x = sum((.060*math.sin(2*math.pi*f*t + j*.31)
             +.026*math.sin(4*math.pi*f*t + j*.17)
             +.012*math.sin(6*math.pi*f*t + j*.23)) for j,f in enumerate(notes))
    env = min(1., t/.08, (3.-t)/.10) * (.88 + .12*math.cos(2*math.pi*2*t))
    return x * env

def main():
    OUT = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "rendered")
    OUT.mkdir(parents=True, exist_ok=True)
    first = speech("Wait", .145)
    body = speech("The gate is open.", .4)
    first_end = FIRST_START + len(first)
    body_start = first_end + round(.14 * RATE)
    body_end = body_start + len(body)
    assert body_end < N - 4800
    voice = [0.] * N
    voice[FIRST_START:first_end] = first
    voice[body_start:body_end] = body
    bed = [music(i) for i in range(N)]
    with tempfile.TemporaryDirectory() as td:
        pair = pathlib.Path(td, "pair.f32")
        # Both stems share one clocked input. A little extra silence supplies full frames.
        padded = zip(bed+[0.]*RATE, voice+[0.]*RATE)
        pair.write_bytes(to_float(v for frame in padded for v in frame))
        reactive = read_float(ffmpeg(
            ["-f","f32le","-ar",str(RATE),"-ac","2","-i",str(pair),
             "-filter_complex_threads","1","-filter_complex",
             "[0:a]channelsplit=channel_layout=stereo[music][key];"
             "[music][key]sidechaincompress=threshold=0.125:ratio=4:knee=1:attack=12:release=180:detection=peak",
             "-f","f32le","-"]))
    assert len(reactive)>=N, len(reactive)
    reactive = reactive[:N]
    ramp = round(.06*RATE)
    release = round(.16*RATE)
    ctrl = [min(max(0,(i-(FIRST_START-ramp))/ramp),1,max(0,(body_end+release-i)/release))
            for i in range(N)]
    pre = [x * 10**(-7.5*c/20) for x,c in zip(bed,ctrl)]
    windows = {"first_35ms":(FIRST_START,FIRST_START+round(.035*RATE)),
               "full_first":(FIRST_START,first_end),
               "between_words":(first_end,body_start),
               "body":(body_start,body_end)}
    report = {
        "ffmpeg": subprocess.check_output(["ffmpeg","-version"],text=True).splitlines()[0].split(" Copyright")[0],
        "rate_hz": RATE, "voice_activity_rms_threshold": DETECTOR_RMS,
        "windows_ms": {name:[round(a*1000/RATE,3),round(b*1000/RATE,3)] for name,(a,b) in windows.items()},
        "voice_peak_amplitude_by_window": {name:round(max(abs(x) for x in voice[a:b]),6)
                                           for name,(a,b) in windows.items()},
        "variants": {}
    }
    for name,bg in [("no-duck",bed),("fast-reactive",reactive),("pre-duck",pre)]:
        combined = [x+y for x,y in zip(bg,voice)]
        save_wav(OUT/f"{name}.wav",combined)
        report["variants"][name] = {
            "background_rms_change_db":{
                name:round(20*math.log10(rms(bg[a:b])/rms(bed[a:b])),3)
                for name,(a,b) in windows.items()},
            "render_peak_dbfs":round(20*math.log10(max(abs(x) for x in combined)),3),
        }
    save_wav(OUT/"voice.wav",voice)
    save_wav(OUT/"music.wav",bed)
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
