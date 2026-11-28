"""Reconstruct Godot 4.7.2 Forward+ indexing and mixing at one sample.

This has no scene, GPU, or engine dependency. The fixture stipulates that
filler decals enter the eligible list without affecting the chosen sample.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Decal:
    name: str
    key: float
    rgb: tuple[float, float, float]
    covers_sample: bool = True


A = Decal("A", 8, (1, 0, 0))
B = Decal("B", 10, (0, 0, 1))


def run(filler_count: int, targets=(A, B), alpha=0.5):
    fillers = [
        Decal(f"F{i}", 2 + i / 64, (0, 1, 0), False)
        for i in range(filler_count)
    ]
    ordered = sorted((*targets, *fillers), key=lambda x: x.key)
    masks = [0] * ((len(ordered) + 31) // 32)
    for index, decal in enumerate(ordered):
        if decal.covers_sample:
            masks[index >> 5] |= 1 << (index & 31)

    visits = []
    out = (0.0, 0.0, 0.0)
    for word_index, mask in enumerate(masks):
        while mask:
            bit = mask.bit_length() - 1
            mask ^= 1 << bit
            decal = ordered[32 * word_index + bit]
            visits.append(decal.name)
            out = tuple((1 - alpha) * dst + alpha * src
                        for dst, src in zip(out, decal.rgb))
    indices = tuple(ordered.index(decal) for decal in targets)
    return indices, masks, "".join(visits), out


if __name__ == "__main__":
    for n, visit, rgb in [(30, "BA", (0.5, 0, 0.25)),
                          (31, "AB", (0.25, 0, 0.5)),
                          (32, "BA", (0.5, 0, 0.25))]:
        ids, masks, seen, rendered = run(n)
        assert ids == (n, n + 1) and (seen, rendered) == (visit, rgb)
        assert run(n, (B, A))[1:] == (masks, visit, rgb)
        words = ",".join(f"0x{m:08x}" for m in masks)
        print(f"fillers={n} indices={ids} masks={words} visit={seen} rgb={rendered}")
    for target in (A, B):
        assert run(31, (target,))[2:] == (
            target.name, tuple(0.5 * c for c in target.rgb))
    assert run(31, alpha=1.0)[-1] == B.rgb
    assert run(30, alpha=1.0)[-1] == A.rgb
    print("Controls: shuffled input, isolated decals, and opaque top layer passed")
