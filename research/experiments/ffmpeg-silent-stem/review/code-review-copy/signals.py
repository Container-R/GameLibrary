"""Original literal input generator and author-side whole-waveform checker."""
import math
import struct

MODES = ('full-normalized', 'short-normalized', 'short-unscaled')

def inputs():
    return {'A': bytes.fromhex('0000003f') * 4096,
            'B-full': bytes(4 * 4096), 'B-short': bytes(4 * 2048)}

def check(mode, data):
    if mode not in MODES or len(data) != 16384:
        raise ValueError('unknown mode or wrong output length')
    if not all(math.isfinite(x[0]) for x in struct.iter_unpack('<f', data)):
        raise ValueError('nonfinite output sample')
    quarter, half = bytes.fromhex('0000803e'), bytes.fromhex('0000003f')
    expected = {'full-normalized': quarter * 4096,
                'short-normalized': quarter * 2048 + half * 2048,
                'short-unscaled': half * 4096}[mode]
    if data != expected:
        raise ValueError('full waveform mismatch')
    return {'frames': 4096, 'bytes': 16384, 'all_samples_equal': True}
