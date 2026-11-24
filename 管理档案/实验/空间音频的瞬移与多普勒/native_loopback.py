"""OpenAL Soft loopback: isolated steady explicit velocities, not a teleport trace."""
import array
import ctypes as ct
import ctypes.util
import math
from pathlib import Path
import wave

HZ = 48000
TONE = 440.0
C = 343.0
N = 28800
lib = ct.CDLL(ctypes.util.find_library("openal") or "libopenal.so.1")
ptr, integer, uint, flt = ct.c_void_p, ct.c_int, ct.c_uint, ct.c_float

def bind(name, result, *args):
    fn = getattr(lib, name)
    fn.restype = result
    fn.argtypes = args
    return fn

open_loop = bind("alcLoopbackOpenDeviceSOFT", ptr, ct.c_char_p)
supports = bind("alcIsRenderFormatSupportedSOFT", ct.c_byte, ptr, integer, integer, integer)
create_context = bind("alcCreateContext", ptr, ptr, ct.POINTER(integer))
activate_context = bind("alcMakeContextCurrent", ct.c_byte, ptr)
destroy_context = bind("alcDestroyContext", None, ptr)
close_device = bind("alcCloseDevice", ct.c_byte, ptr)
render = bind("alcRenderSamplesSOFT", None, ptr, ptr, integer)
al_string = bind("alGetString", ct.c_char_p, integer)
al_error = bind("alGetError", integer)
doppler = bind("alDopplerFactor", None, flt)
sound_speed = bind("alSpeedOfSound", None, flt)
distance_model = bind("alDistanceModel", None, integer)
listener_vec = bind("alListener3f", None, integer, flt, flt, flt)
gen_buffers = bind("alGenBuffers", None, integer, ct.POINTER(uint))
gen_sources = bind("alGenSources", None, integer, ct.POINTER(uint))
set_buf = bind("alBufferData", None, uint, integer, ptr, integer, integer)
source_vec = bind("alSource3f", None, uint, integer, flt, flt, flt)
source_set = bind("alSourcei", None, uint, integer, integer)
source_play = bind("alSourcePlay", None, uint)
source_stop = bind("alSourceStop", None, uint)
del_buf = bind("alDeleteBuffers", None, integer, ct.POINTER(uint))
del_src = bind("alDeleteSources", None, integer, ct.POINTER(uint))

POS, VEL = 0x1004, 0x1006
AL_FORMAT_MONO16 = 0x1101
ALC_MONO_SOFT, ALC_SHORT_SOFT = 0x1500, 0x1402

def measured_pitch(samples):
    # Ignore first 0.1 s (start transient), last 0.1 s; use interpolated
    # positive crossings over the entire interior rather than FFT bin centers.
    phase = []
    for i in range(HZ//10, N-HZ//10):
        if samples[i] <= 0 < samples[i+1]:
            phase.append(i - samples[i]/(samples[i+1]-samples[i]))
    assert len(phase) > 50
    return (len(phase)-1)*HZ/(phase[-1]-phase[0])

def main():
    dev = open_loop(None)
    assert dev and supports(dev, HZ, ALC_MONO_SOFT, ALC_SHORT_SOFT)
    attrs = (integer*7)(0x1007, HZ, 0x1990, ALC_MONO_SOFT, 0x1991, ALC_SHORT_SOFT, 0)
    ctx = create_context(dev, attrs)
    assert ctx and activate_context(ctx)
    print("OpenAL", al_string(0xB002).decode(), "|", al_string(0xB003).decode())
    print("48000 Hz mono signed PCM16, positions held: source (0,0,-10), listener (0,0,0)")
    print("Doppler factor 1, speed of sound 343, distance attenuation disabled")
    doppler(1)
    sound_speed(C)
    distance_model(0)
    listener_vec(POS, 0, 0, 0)
    listener_vec(VEL, 0, 0, 0)
    tone = (ct.c_short*HZ)(*(round(6000*math.sin(math.tau*TONE*i/HZ)) for i in range(HZ)))
    buf, src = uint(), uint()
    gen_buffers(1, ct.byref(buf))
    set_buf(buf, AL_FORMAT_MONO16, tone, ct.sizeof(tone), HZ)
    panels = array.array("h")
    for name, velocity in (("approach",5),("recede",-5),("jump interpreted as approach",120),("reset velocity",0)):
        gen_sources(1, ct.byref(src))
        source_set(src, 0x1009, buf.value)  # AL_BUFFER
        source_set(src, 0x1007, 1)         # AL_LOOPING
        source_vec(src, POS, 0, 0, -10)
        source_vec(src, VEL, 0, 0, velocity)
        source_play(src)
        pcm=(ct.c_short*N)()
        render(dev, pcm, N)
        assert al_error()==0
        observed=measured_pitch(pcm)
        ideal=TONE*C/(C-velocity)
        print(f"{name}: vz={velocity:+g} m/s; measured {observed:.3f} Hz; ideal {ideal:.3f} Hz")
        assert abs(observed-ideal)<1
        source_stop(src)
        del_src(1, ct.byref(src))
        # Listening copy only: 0.35 s of steady audio, 5 ms fades, 0.15 s gap.
        clip = list(pcm[HZ//10:HZ//10+16800])
        for i,x in enumerate(clip):
            clip[i] = round(x*min(1,i/240,(len(clip)-1-i)/240))
        panels.extend(clip); panels.extend([0]*7200)
    if __import__("sys").byteorder != "little":
        panels.byteswap()
    with wave.open(str(Path("comparison.wav")), "wb") as out:
        out.setparams((1,2,HZ,0,"NONE","not compressed"))
        out.writeframes(panels.tobytes())
    del_buf(1, ct.byref(buf))
    activate_context(None)
    destroy_context(ctx)
    close_device(dev)

if __name__=="__main__":
    main()
