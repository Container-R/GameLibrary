"""Controlled Arabic cmap fallback; no font files are written to the output."""
import argparse
from ctypes import CDLL, POINTER, Structure, byref, c_char_p, c_int, c_uint, c_void_p
import hashlib
from pathlib import Path
import tempfile

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, features, __version__ as pillow_version

TEXT = "\u0628\u062a"
MISSING = ord(TEXT[1])
KW = dict(direction="rtl", language="ar")

class Glyph(Structure):
    _fields_ = [(k, c_uint) for k in ("codepoint", "mask", "cluster", "var1", "var2")]

hb = CDLL("libharfbuzz.so.0")
def bind(name, argtypes, restype=None):
    func = getattr(hb, name)
    func.argtypes, func.restype = argtypes, restype
    return func

version = bind("hb_version_string", [], c_char_p)
blob = bind("hb_blob_create_from_file", [c_char_p], c_void_p)
face = bind("hb_face_create", [c_void_p, c_uint], c_void_p)
font = bind("hb_font_create", [c_void_p], c_void_p)
ot_funcs = bind("hb_ot_font_set_funcs", [c_void_p])
buffer = bind("hb_buffer_create", [], c_void_p)
add = bind("hb_buffer_add_utf32", [c_void_p, POINTER(c_uint), c_int, c_uint, c_int])
lang = bind("hb_language_from_string", [c_char_p, c_int], c_void_p)
setlang = bind("hb_buffer_set_language", [c_void_p, c_void_p])
guess = bind("hb_buffer_guess_segment_properties", [c_void_p])
shape = bind("hb_shape", [c_void_p, c_void_p, c_void_p, c_uint])
infos = bind("hb_buffer_get_glyph_infos", [c_void_p, POINTER(c_uint)], POINTER(Glyph))
free = [bind(f"hb_{part}_destroy", [c_void_p]) for part in ("buffer","font","face","blob")]

def glyphs(path, text):
    b = blob(str(path).encode())
    fa = face(b, 0)
    fo = font(fa)
    ot_funcs(fo)
    buf = buffer()
    raw = (c_uint*len(text))(*map(ord,text))
    add(buf,raw,len(text),0,len(text))
    setlang(buf,lang(b"ar",-1))
    guess(buf)
    shape(fo,buf,None,0)
    n = c_uint()
    data = infos(buf,byref(n))
    ret = [(data[i].codepoint, data[i].cluster) for i in range(n.value)]
    for destroy, obj in zip(free, (buf,fo,fa,b)):
        destroy(obj)
    return ret

def render(main_path, fallback_path, png):
    assert features.check_feature("raqm")
    main, fallback = [ImageFont.truetype(str(p), 96, layout_engine=ImageFont.Layout.RAQM)
                      for p in (main_path, fallback_path)]
    rows = [
        ("Primary only (missing slot)", [(TEXT,main)]),
        ("Per-character fallback: two independent shaping runs",
         [(TEXT[0],main),(TEXT[1],fallback)]),
        ("Whole-word fallback: one shaping run", [(TEXT,fallback)]),
    ]
    art = Image.new("RGB", (830, 540), "#f5f7fa")
    d = ImageDraw.Draw(art)
    d.text((28,15), "U+0628 U+062A | RTL, Noto Sans Arabic | temporary primary omits U+062A", fill="#132840", font=ImageFont.load_default(size=17))
    d.text((28,40), "Blue = primary; orange = fallback; grey guide = common right edge and baseline", fill="#364e63", font=ImageFont.load_default(size=16))
    for i,(label,runs) in enumerate(rows):
        y = 68+i*151
        d.rounded_rectangle((22,y,807,y+140),radius=8,fill="#ffffff",outline="#b6c2ce")
        d.text((43,y+13),label,fill="#132840",font=ImageFont.load_default(size=19))
        cursor = 729
        d.line((465,y+91,cursor,y+91),fill="#d8e0e8")
        d.line((cursor,y+46,cursor,y+117),fill="#d8e0e8")
        for chunk,f in runs:
            advance = f.getlength(chunk,**KW)
            cursor -= advance
            d.text((cursor,y+91),chunk, fill="#174c7d" if f is main else "#a64424", font=f, anchor="ls",**KW)
        print(f"{label}: advance={729-cursor:.6f}px")
    art.save(png)

def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--font",type=Path,default=Path("/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"))
    arg.add_argument("--png",type=Path,default=Path("comparison.png"))
    ns = arg.parse_args()
    orig = ns.font.resolve()
    print(f"Pillow {pillow_version}; RAQM {features.version_feature('raqm')}; Pillow HarfBuzz {features.version_feature('harfbuzz')}; system HarfBuzz {version().decode()}")
    print("Input font SHA-256:",hashlib.sha256(orig.read_bytes()).hexdigest())
    with tempfile.TemporaryDirectory() as td:
        cut = Path(td)/"local-cmap-test.ttf"
        with TTFont(orig) as f:
            keep = ord(TEXT[0])
            assert keep in f.getBestCmap() and MISSING in f.getBestCmap()
            for table in f["cmap"].tables:
                if table.isUnicode() and hasattr(table,"cmap"):
                    table.cmap.pop(MISSING,None)
            assert keep in f.getBestCmap() and MISSING not in f.getBestCmap()
            f.save(cut)
        missing = glyphs(cut,TEXT)
        split = glyphs(cut,TEXT[0]),glyphs(orig,TEXT[1])
        whole = glyphs(orig,TEXT)
        assert len(missing)==2 and any(gid==0 for gid,_ in missing)
        assert len(whole)==2 and all(gid!=0 for gid,_ in whole)
        assert all(len(gs)==1 and gs[0][0]!=0 for gs in split)
        assert [gs[0][0] for gs in reversed(split)] != [gid for gid,_ in whole]
        for label, data in [("primary only",missing),("independent chunks (logical order; each cluster index starts at zero)",split),("whole fallback word",whole)]:
            print(f"{label} glyphs (gid, codepoint index within shaping input): {data}")
        render(cut, orig, ns.png)

if __name__ == "__main__":
    main()
