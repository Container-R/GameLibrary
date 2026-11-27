import ctypes as c
import json

pango = c.CDLL("libpango-1.0.so.0")
cairo = c.CDLL("libpangocairo-1.0.so.0")
gobj = c.CDLL("libgobject-2.0.so.0")
ptr, ip = c.c_void_p, c.POINTER(c.c_int)
SCALE = 1024

def bind(lib, name, result, *args):
    fun = getattr(lib, name)
    fun.restype, fun.argtypes = result, args
    return fun

unref = bind(gobj, "g_object_unref", None, ptr)
get_map = bind(cairo, "pango_cairo_font_map_get_default", ptr)
context = bind(pango, "pango_font_map_create_context", ptr, ptr)
layout_new = bind(pango, "pango_layout_new", ptr, ptr)
font_from = bind(pango, "pango_font_description_from_string", ptr, c.c_char_p)
font_free = bind(pango, "pango_font_description_free", None, ptr)
font_set = bind(pango, "pango_layout_set_font_description", None, ptr, ptr)
set_width = bind(pango, "pango_layout_set_width", None, ptr, c.c_int)
set_wrap = bind(pango, "pango_layout_set_wrap", None, ptr, c.c_int)
set_text = bind(pango, "pango_layout_set_text", None, ptr, c.c_char_p, c.c_int)
get_size = bind(pango, "pango_layout_get_size", None, ptr, ip, ip)
get_count = bind(pango, "pango_layout_get_line_count", c.c_int, ptr)
get_line = bind(pango, "pango_layout_get_line_readonly", ptr, ptr, c.c_int)
get_start = bind(pango, "pango_layout_line_get_start_index", c.c_int, ptr)
get_length = bind(pango, "pango_layout_line_get_length", c.c_int, ptr)
version = bind(pango, "pango_version_string", c.c_char_p)

def measure(text, width, mode):
    ctx = context(get_map())
    layout = layout_new(ctx)
    font = font_from(b"DejaVu Sans 16px")
    data = text.encode("utf-8")
    try:
        font_set(layout, font)
        set_width(layout, -1 if width is None else width * SCALE)
        set_wrap(layout, mode)
        set_text(layout, data, len(data))
        logical_w, logical_h = c.c_int(), c.c_int()
        get_size(layout, c.byref(logical_w), c.byref(logical_h))
        lines = []
        for i in range(get_count(layout)):
            line = get_line(layout, i)
            start = get_start(line)
            lines.append(data[start:start+get_length(line)].decode("utf-8"))
        return (logical_w.value / SCALE, lines)
    finally:
        font_free(font)
        unref(layout)
        unref(ctx)

print("pango="+version().decode())
for text in ["iiiiii", "WWWWWW"]:
    unbounded = measure(text, None, 0)
    word = measure(text, 54, 0)
    word_char = measure(text, 54, 2)
    print(json.dumps({"text": text, "unbounded": unbounded, "word_54px": word, "word_char_54px": word_char}))
    assert len(unbounded[1]) == len(word[1]) == 1
    assert (word[0] <= 54 if text[0] == "i" else word[0] > 54)
    assert len(word_char[1]) == (1 if text[0] == "i" else 2)
