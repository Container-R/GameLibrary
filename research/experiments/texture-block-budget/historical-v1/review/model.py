"""Original finite BC tight-payload model, not a GPU allocator."""
import struct
BLOCK_BYTES = {'BC1': 8, 'BC7': 16}

def layout(width, height, fmt):
    if type(width) is not int or type(height) is not int or width < 1 or height < 1:
        raise ValueError('positive integer dimensions required')
    if fmt not in BLOCK_BYTES:
        raise ValueError('unsupported format')
    rows = []
    offset = 128  # legacy DDS header; layout offsets used for BC1 fixture only
    while True:
        bx, by = (width + 3) // 4, (height + 3) // 4
        size = bx * by * BLOCK_BYTES[fmt]
        rows.append(dict(width=width, height=height, blocks_x=bx, blocks_y=by,
                         size=size, payload_offset=offset - 128))
        offset += size
        if width == height == 1:
            return rows
        width, height = max(1, width // 2), max(1, height // 2)

def header(width, height, mips, top_size):
    # DDS_HEADER: required flags + LINEARSIZE; mip count flag only if multiple.
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000
    caps = 0x1000
    if mips > 1:
        flags |= 0x20000
        caps |= 0x8 | 0x400000
    fields = [124, flags, height, width, top_size, 0, mips] + [0] * 11
    fields += [32, 4, int.from_bytes(b'DXT1', 'little'), 0, 0, 0, 0, 0]
    fields += [caps, 0, 0, 0, 0]
    return b'DDS ' + struct.pack('<31I', *fields)

# Distinct RGB565 endpoints, selectors all0 => every pixel endpoint0.
MARKERS = [(0xf800, (255, 0, 0)), (0x07e0, (0, 255, 0)),
           (0x001f, (0, 0, 255)), (0xffe0, (255, 255, 0)),
           (0xf81f, (255, 0, 255)), (0x07ff, (0, 255, 255))]

def build():
    rows = layout(60, 40, 'BC1')
    payload = b''.join(struct.pack('<HHI', marker[0], 0, 0) * (r['size'] // 8)
                       for r, marker in zip(rows, MARKERS, strict=True))
    return header(60, 40, 6, rows[0]['size']) + payload
