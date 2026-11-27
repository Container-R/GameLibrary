import ctypes as c
import json

icu = c.CDLL("libicuuc.so.76")
u16 = c.POINTER(c.c_uint16)
i32p = c.POINTER(c.c_int32)

def api(name, ret, *argtypes):
    f = getattr(icu, name + "_76")
    f.restype = ret
    f.argtypes = argtypes
    return f

unicode_version = api("u_getUnicodeVersion", None, c.POINTER(c.c_uint8))
open_break = api("ubrk_open", c.c_void_p, c.c_int32, c.c_char_p, u16, c.c_int32, i32p)
first = api("ubrk_first", c.c_int32, c.c_void_p)
next_break = api("ubrk_next", c.c_int32, c.c_void_p)
rule_status = api("ubrk_getRuleStatus", c.c_int32, c.c_void_p)
close = api("ubrk_close", None, c.c_void_p)

def boundaries(text, kind, locale, with_status=False):
    units = text.encode("utf-16-le")
    buf = (c.c_uint16 * (len(units)//2))(*(int.from_bytes(units[i:i+2], "little") for i in range(0, len(units), 2)))
    status = c.c_int32(0)
    it = open_break(kind, locale.encode(), buf, len(buf), c.byref(status))
    if not it or status.value > 0:
        raise RuntimeError((kind, locale, status.value))
    try:
        result = []
        off = first(it)
        while off != -1:
            result.append((off, rule_status(it)) if with_status else off)
            off = next_break(it)
        return result
    finally:
        close(it)

version = (c.c_uint8 * 4)()
unicode_version(version)
print("unicode_version="+".".join(map(str, version)))
for name, text, locale in [
    ("cjk", "拿取道具，继续", "zh"),
    ("emoji_zwj", "a👩🏽‍🔧b", "en"),
    ("combining", "e\u0301clair", "en"),
    ("hard", "A\r\nB", "en"),
    ("nbsp", "A\u00a0B C", "en"),
]:
    chars = boundaries(text, 0, locale)
    lines = boundaries(text, 2, locale, with_status=True)
    positions = [offset for offset, _ in lines]
    hard = [offset for offset, status in lines if 100 <= status < 200]
    expected = {
        "cjk": ([0, 1, 2, 3, 4, 5, 6, 7], [0, 1, 2, 3, 5, 6, 7], []),
        "emoji_zwj": ([0, 1, 8, 9], [0, 1, 8, 9], []),
        "combining": ([0, 2, 3, 4, 5, 6, 7], [0, 7], []),
        "hard": ([0, 1, 3, 4], [0, 3, 4], [3]),
        "nbsp": ([0, 1, 2, 3, 4, 5], [0, 4, 5], []),
    }
    assert (chars, positions, hard) == expected[name]
    print(json.dumps({"name": name, "text": text, "locale": locale,
                      "grapheme_u16": chars, "line_u16": positions,
                      "hard_line_u16": hard}, ensure_ascii=False))
