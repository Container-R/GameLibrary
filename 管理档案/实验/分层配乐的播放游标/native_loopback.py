"""Controlled OpenAL Soft stereo loopback, with reference/stem in L/R."""
import ctypes as c
from ctypes.util import find_library

HZ, BEAT, GATE, END, WIDTH = 48000, 24000, 36000, 100000, 32
STEREO16, TYPE_FLOAT, STEREO = 0x1103, 0x1406, 0x1501
BUFFER, SAMPLE_OFFSET, GAIN = 0x1009, 0x1025, 0x100A
lib = c.CDLL(find_library("openal") or "libopenal.so.1")
P, I, U, F, B = c.c_void_p, c.c_int, c.c_uint, c.c_float, c.c_byte

def bind(name, result, *args):
    fn = getattr(lib, name)
    fn.restype, fn.argtypes = result, args
    return fn

open_loop = bind("alcLoopbackOpenDeviceSOFT", P, c.c_char_p)
supports = bind("alcIsRenderFormatSupportedSOFT", B, P, I, I, I)
ctx_create = bind("alcCreateContext", P, P, c.POINTER(I))
ctx_current = bind("alcMakeContextCurrent", B, P)
ctx_destroy = bind("alcDestroyContext", None, P)
close = bind("alcCloseDevice", B, P)
render = bind("alcRenderSamplesSOFT", None, P, P, I)
get_str = bind("alGetString", c.c_char_p, I)
get_error = bind("alGetError", I)
gen_buffers = bind("alGenBuffers", None, I, c.POINTER(U))
gen_sources = bind("alGenSources", None, I, c.POINTER(U))
buffer_data = bind("alBufferData", None, U, I, P, I, I)
set_i = bind("alSourcei", None, U, I, I)
set_f = bind("alSourcef", None, U, I, F)
get_i = bind("alGetSourcei", None, U, I, c.POINTER(I))
play = bind("alSourcePlay", None, U)
play_many = bind("alSourcePlayv", None, I, c.POINTER(U))

def marker_buffer(channel, begin_shift=0):
    data = (c.c_short * (END*2))()
    for at in range(begin_shift, END-WIDTH, BEAT):
        for k in range(at, at+WIDTH):
            data[k*2+channel] = 8192
    return data

def edges(pcm, channel, threshold=0.04):
    loud = [abs(pcm[k*2+channel]) > threshold for k in range(END)]
    return [k for k, active in enumerate(loud) if active and (k == 0 or not loud[k-1])]

def run(mode):
    dev = open_loop(None)
    assert dev and supports(dev, HZ, STEREO, TYPE_FLOAT)
    attrs = (I*7)(0x1007, HZ, 0x1990, STEREO, 0x1991, TYPE_FLOAT, 0)
    ctx = ctx_create(dev, attrs)
    assert ctx and ctx_current(ctx)
    try:
        sources, buffers = (U*2)(), (U*2)()
        gen_sources(2, sources)
        gen_buffers(2, buffers)
        assert get_error() == 0
        for channel, (source, buffer) in enumerate(zip(sources, buffers)):
            data = marker_buffer(channel, 2400 if (mode == "shifted_asset" and channel == 1) else 0)
            buffer_data(buffer, STEREO16, data, c.sizeof(data), HZ)
            set_i(source, BUFFER, buffer)
        reference, stem = sources
        if mode in ("running_muted", "shifted_asset"):
            set_f(stem, GAIN, 0.0)
            play_many(2, sources)
        else:
            play(reference)
        assert get_error() == 0
        pcm = (F*(END*2))()
        render(dev, pcm, GATE)
        cursor = I()
        get_i(stem, SAMPLE_OFFSET, c.byref(cursor))
        if mode in ("running_muted", "shifted_asset"):
            assert cursor.value == GATE
            set_f(stem, GAIN, 1.0)
        else:
            assert cursor.value == 0
            if mode == "late_aligned":
                set_i(stem, SAMPLE_OFFSET, GATE)
            play(stem)
        assert get_error() == 0
        render(dev, c.byref(pcm, GATE*2*c.sizeof(F)), END-GATE)
        assert get_error() == 0
        left = edges(pcm, 0)
        right = edges(pcm, 1)
        assert left == [0, 24000, 48000, 72000, 96000], left
        expect = {"running_muted":[48000,72000,96000], "late_zero":[36000,60000,84000],
                  "late_aligned":[48000,72000,96000], "shifted_asset":[50400,74400,98400]}[mode]
        assert right == expect, (mode, right)
        assert max(abs(pcm[k*2+1]) for k in range(GATE)) < 1e-7
        print(f"{mode}: cursor before change={cursor.value}, left={left}, right={right}")
        return get_str(0xB002).decode(), get_str(0xB003).decode()
    finally:
        assert ctx_current(None)
        ctx_destroy(ctx)
        assert close(dev)

if __name__ == "__main__":
    print(f"{HZ} Hz; stereo float mix; gate={GATE}; {END} frames; width={WIDTH} frames")
    for mode in ("late_zero", "running_muted", "late_aligned", "shifted_asset"):
        version, renderer = run(mode)
    print(f"OpenAL {version} | {renderer}")
