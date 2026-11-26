"""Compare complete decoded packet lengths with FFmpeg's presented PCM."""
import json
import math
from pathlib import Path
import struct
import subprocess
import wave

RATE = 48000
def run(*args):
    return subprocess.check_output(args)

print(run('ffmpeg', '-version').decode().splitlines()[0])
for N in (93659, 94001):
    with wave.open('input.wav', 'wb') as w:
        w.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        w.writeframes(b''.join(struct.pack('<h', round(8000 * math.sin(2 * math.pi * 440 * i / RATE)))
                               for i in range(N)))
    print(f'input frames={N}')
    for ms in ('10', '20'):
        ogg = f'framing-{ms}ms.opus'
        run('ffmpeg', '-y', '-v', 'error', '-i', 'input.wav', '-c:a', 'libopus',
            '-b:a', '64k', '-frame_duration', ms, ogg)
        p = json.loads(run('ffprobe', '-v', 'error', '-select_streams', 'a:0',
                           '-show_packets', '-show_streams', '-of', 'json', ogg))
        packets = p['packets']
        assert p['streams'][0]['time_base'] == '1/48000'
        pcm = run('ffmpeg', '-v', 'error', '-i', ogg, '-f', 's16le', '-acodec',
                  'pcm_s16le', '-')
        skip = packets[0]['side_data_list'][0]['skip_samples']
        discard = packets[-1]['side_data_list'][0]['discard_padding']
        frame_samples = RATE * int(ms) // 1000
        assert all(int(x['duration']) == frame_samples for x in packets[:-1])
        assert int(packets[-1]['duration']) + discard == frame_samples
        decoded_packet_slots = frame_samples * len(packets)
        print(f'{ms} ms: n={len(packets)}, slots={decoded_packet_slots}, '
              f'pre-skip={skip}, EOS discard={discard}, presented={len(pcm)//2}')
        assert decoded_packet_slots - skip - discard == len(pcm)//2 == N
