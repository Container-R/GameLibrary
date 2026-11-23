"""Project-level cache-key and snapshot policy, not an engine implementation."""
from dataclasses import dataclass, replace
from hashlib import sha256
import json

@dataclass(frozen=True)
class Inputs:
    target: str = "mobile"
    sprite: str = "immutable source bytes"
    audio: str = "immutable PCM bytes"
    base: int = 256
    override: int | None = None
    metadata: str = "ignored note"
    behavior: int = 1

    def effective(self):
        return self.override if self.override is not None else self.base

def key(i, kind, policy):
    source = i.sprite if kind == "sprite" else i.audio
    fields = [kind, source, i.target, i.behavior]
    if kind == "sprite":
        if policy == "base":
            fields.append(i.base)
        elif policy == "effective":
            fields.append(i.effective())
    return sha256(json.dumps(fields).encode()).hexdigest()

def request(cache, i, kind, policy, *, execution=None):
    k = key(i, kind, policy)
    if k in cache:
        return True, cache[k]
    read = i if execution is None else execution
    value = read.effective() if kind == "sprite" else (read.target, read.audio)
    cache[k] = value
    return False, value

def main():
    baseline = Inputs()
    cases = [
        ("unchanged", baseline, "effective", True, 256, 256, True),
        ("edit omitted rule", replace(baseline, base=512), "omit", True, 256, 512, True),
        ("edit effective rule", replace(baseline, base=512), "effective", False, 512, 512, True),
        ("new override base-only", replace(baseline, override=1024), "base", True, 256, 1024, True),
        ("new override effective", replace(baseline, override=1024), "effective", False, 1024, 1024, True),
        ("switch platform", replace(baseline, target="desktop"), "effective", False, 256, 256, False),
        ("unrelated metadata", replace(baseline, metadata="other"), "effective", True, 256, 256, True),
    ]
    print("case | sprite hit | warm size | clean size | audio hit")
    for label, now, policy, expected_hit, expected_warm, expected_fresh, expected_audio in cases:
        cache = {}
        for kind in ("sprite", "audio"):
            request(cache, baseline, kind, policy)
        hit, warm = request(cache, now, "sprite", policy)
        _, fresh = request({}, now, "sprite", policy)
        audio_hit, audio = request(cache, now, "audio", policy)
        assert (hit,warm,fresh,audio_hit)==(expected_hit,expected_warm,expected_fresh,expected_audio)
        assert audio == (now.target, now.audio)
        print(label, hit, warm, fresh, audio_hit, sep=" | ")
    cache = {}
    request(cache, baseline, "sprite", "effective", execution=replace(baseline, base=512))
    assert request(cache, baseline, "sprite", "effective") == (True, 512)
    fixed = {}
    request(fixed, baseline, "sprite", "effective")
    assert request(fixed, baseline, "sprite", "effective") == (True, 256)
    print("Same 256 key: result with live reread=512; result with pinned input=256")

if __name__ == "__main__":
    main()
