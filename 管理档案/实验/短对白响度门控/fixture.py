"""Measurement signals only. No speech / no listening claim."""
from array import array
import json, math, re, subprocess, sys

SR = 48000
def tone(ms, amplitude=.1):
    n=ms*48
    # Integer ms and 1 kHz make both zero-crossing boundaries predictable.
    return array('f', (amplitude*math.sin(2*math.pi*i/48) for i in range(n)))
def silence(ms):
    return array('f', [0.])* (ms*48)
def measure(signal):
    if sys.byteorder != 'little': signal.byteswap()
    cmd=['ffmpeg','-hide_banner','-nostats','-f','f32le','-ar',str(SR),'-ac','1',
        '-i','pipe:0','-af','ebur128=peak=sample+true','-f','null','-']
    log=subprocess.run(cmd,input=signal.tobytes(),capture_output=True,check=True).stderr.decode()
    summary=log.rsplit('Summary:',1)[1]
    def field(pat): return float(re.search(pat,summary).group(1))
    frames=re.findall(r"t:\s*([0-9.]+).*?M:\s*(-?[0-9.]+).*?I:\s*(-?[0-9.]+)",log,re.M)
    return {
        'I_lufs_reported':field(r"\bI:\s*(-?[0-9.]+)"),
        'relative_threshold_lufs_reported':field(r"Threshold:\s*(-?[0-9.]+)"),
        'sample_peak_dbfs':field(r"Sample peak:\s*\n\s*Peak:\s*(-?[0-9.]+)"),
        'true_peak_dbtp':field(r"True peak:\s*\n\s*Peak:\s*(-?[0-9.]+)"),
        'first_400ms':([float(v) for v in frames[3]] if len(frames)>=4 else None),
    }
cases={
 '200_tone':tone(200),
 '350_tone':tone(350),
 '200_tone_200_tail':tone(200)+silence(200),
 '350_tone_50_tail':tone(350)+silence(50),
 '400_tone':tone(400),
 '1000_tone':tone(1000),
 '1000_tone_1000_tail':tone(1000)+silence(1000),
 '1000_lead_1000_tone':silence(1000)+tone(1000),
 '200_lead_1000_tone_200_tail':silence(200)+tone(1000)+silence(200),
 '1000_tone_quiet_role':tone(1000,.025),
 '1000_tone_same_role_plus_12dB':tone(1000,.025*10**(.6)),
}
data={k:measure(v) for k,v in cases.items()}
print(json.dumps(data,indent=2))
