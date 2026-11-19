from fractions import Fraction
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
import json
import wave

source = Path(__file__).with_name("generated")/"phase_matched_full_cycles.wav"
def cmd(*args):
    return run(args,check=True,capture_output=True).stdout

with TemporaryDirectory() as temp:
    d=Path(temp)
    enc=d/"asset.opus"
    raw=d/"readback.wav"
    cmd("ffmpeg","-hide_banner","-loglevel","error","-i",str(source),
        "-c:a","libopus","-frame_duration","20",str(enc))
    cmd("ffmpeg","-hide_banner","-loglevel","error","-i",str(enc),
        "-c:a","pcm_s16le",str(raw))
    packets=json.loads(cmd("ffprobe","-v","error","-select_streams","a:0",
                          "-show_packets","-of","json",str(enc)))["packets"]
    with wave.open(str(source)) as orig, wave.open(str(raw)) as decoded:
        assert (orig.getframerate(),decoded.getframerate()) == (48000,48000)
        assert (orig.getnchannels(),decoded.getnchannels()) == (2,2)
        assert orig.getnframes() == decoded.getnframes()
        opus={"original_pcm_frames":orig.getnframes(),
              "decoded_pcm_frames":decoded.getnframes(),
              "first_packet_skip_samples":packets[0]["side_data_list"][0]["skip_samples"],
              "final_packet_discard_padding":packets[-1]["side_data_list"][0]["discard_padding"]}
assert opus["first_packet_skip_samples"] > 0 and opus["final_packet_discard_padding"] > 0
period_a,period_b,repeat=48000,48032,150
offset=repeat*(period_b-period_a)
assert Fraction(offset,48000)==Fraction(1,10)
print(json.dumps({"local_ffmpeg_ogg_opus_length_only":opus,
                  "hypothetical_different_periods":{"period_a_frames":period_a,"period_b_frames":period_b,
                    "interval_count":repeat,"offset_frames":offset,
                    "offset_milliseconds":str(Fraction(1000*offset,48000))}},indent=2))
