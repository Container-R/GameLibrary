"""Generate float samples through FFmpeg aevalsrc; simple control hysteresis model."""
import array
import math
import subprocess
import sys

RATE, START, TURN = 48000, 1200, 1440
DOWN = "(0.2+0.8*exp(-(n-1200)/240))"
AT_TURN = 0.2 + 0.8 / math.e
modes = {
    "steady": "1",
    "step": "if(lt(n,1200),1,0.2)",
    "smooth": f"if(lt(n,1200),1,{DOWN})",
    "retarget": f"if(lt(n,1200),1,if(lt(n,1440),{DOWN},1+({AT_TURN}-1)*exp(-(n-1440)/240)))",
    "restart-old-target": f"if(lt(n,1200),1,if(lt(n,1440),{DOWN},1-0.8*exp(-(n-1440)/240)))",
}


def render(gain):
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
           "-f", "lavfi", "-i", f"aevalsrc='0.5*cos(2*PI*1000*n/{RATE})*({gain})':s={RATE}:d=0.1",
           "-c:a", "pcm_f32le", "-f", "f32le", "-"]
    f32 = array.array("f")
    f32.frombytes(subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout)
    if sys.byteorder != "little":
        f32.byteswap()
    assert len(f32) == 4800
    return f32


def jump(x, n):
    return abs(x[n] - x[n - 1])


if __name__ == "__main__":
    version = subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0]
    print(version.split(" Copyright", 1)[0])
    print("48 kHz; carrier 1 kHz; transitions at 25 and 30 ms; tau 5 ms")
    print("mode jump@25ms gain@30ms jump@30ms gain@45ms")
    outputs = {m: render(g) for m, g in modes.items()}
    for m, x in outputs.items():
        print(f"{m} {jump(x, START):.6f} {2*x[TURN]:.6f} {jump(x, TURN):.6f} {2*x[2160]:.6f}")
    assert jump(outputs["step"], START) > 0.39
    assert outputs["steady"][START] == outputs["smooth"][START]
    assert abs(2*outputs["smooth"][TURN] - AT_TURN) < 1e-6
    assert outputs["retarget"][TURN] == outputs["smooth"][TURN]
    assert jump(outputs["retarget"], TURN) < 0.01
    assert jump(outputs["restart-old-target"], TURN) > 0.14

    scores = [0.20, 0.49, 0.51, 0.48, 0.52, 0.49, 0.70, 0.55, 0.45, 0.30]
    binary = [int(s >= 0.50) for s in scores]
    hist, blocked = [], 0
    for s in scores:
        if not blocked and s >= 0.60:
            blocked = 1
        elif blocked and s <= 0.40:
            blocked = 0
        hist.append(blocked)
    changes = lambda seq: sum(a != b for a, b in zip(seq, seq[1:]))
    assert (changes(binary), changes(hist)) == (6, 2)
    print("control scores", ",".join(f"{v:.2f}" for v in scores))
    print("single threshold", "".join(map(str, binary)), "changes", changes(binary))
    print("hysteresis", "".join(map(str, hist)), "changes", changes(hist))
