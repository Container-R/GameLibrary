"""Bounded generated-stream framing reader; no entropy decoding/conformance claim."""
import struct

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def crc(data):
    value = 0
    for byte in data:
        value ^= byte << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value

def read(data):
    need(type(data) is bytes and 0 < len(data) <= 1048576, 'input size/type')
    pages, packets, pending = [], [], bytearray()
    offset = 0
    serial = None
    packet_start = 0
    while offset < len(data):
        need(len(pages) < 1024 and offset + 27 <= len(data), 'page bound')
        head = data[offset:offset+27]
        need(head[:5] == b'OggS\0', 'capture/version')
        flags = head[5]
        gp, sid, seq, checksum = struct.unpack_from('<qIII', head, 6)
        need(gp >= -1, 'negative granule')
        need(flags & ~7 == 0 and bool(flags & 1) == bool(pending), 'flags/continuation')
        need(seq == len(pages), 'sequence')
        need(bool(flags & 2) == (seq == 0), 'BOS placement')
        if serial is None:
            serial = sid
        need(sid == serial, 'unsupported multiple serials')
        count = head[26]
        need(offset+27+count <= len(data), 'lacing bound')
        laces = data[offset+27:offset+27+count]
        end = offset+27+count+sum(laces)
        need(end <= len(data), 'body bound')
        need(bool(flags & 4) == (end == len(data)), 'EOS placement')
        raw = bytearray(data[offset:end]); raw[22:26] = bytes(4)
        computed = crc(raw)
        need(computed == checksum, 'CRC')
        pos = offset+27+count
        completed = []
        for size in laces:
            if not pending:
                packet_start = seq
            pending.extend(data[pos:pos+size]); pos += size
            if size < 255:
                need(len(packets) < 1024, 'packet count')
                completed.append(len(packets))
                packets.append({'start_page':packet_start,'end_page':seq,'data':bytes(pending)})
                pending.clear()
        if not completed:
            need(gp == -1, 'no completion granule')
        pages.append({'index':seq,'offset':offset,'size':end-offset,'flags':flags,'granule':gp,
                      'crc':checksum,'computed_crc':computed,'completed_packets':completed,
                      'pending_bytes':len(pending),'laces':list(laces)})
        offset = end
    need(not pending and len(packets) >= 3, 'unfinished/insufficient packets')
    h = packets[0]
    need(h['start_page'] == h['end_page'] == 0 and pages[0]['completed_packets'] == [0]
         and pages[0]['pending_bytes'] == 0, 'OpusHead placement')
    b = h['data']
    need(len(b) == 19 and b[:8] == b'OpusHead', 'unsupported identification')
    version, channels, preskip, rate, gain, family = struct.unpack_from('<BBHIhB',b,8)
    need((version,channels,rate,gain,family) == (1,2,48000,0,0), 'unsupported header configuration')
    need(preskip > 0, 'positive pre-skip not established')
    tag = packets[1]; b = tag['data']
    need(tag['start_page'] == 1 and b[:8] == b'OpusTags', 'Tags placement/magic')
    tp = pages[tag['end_page']]
    need(tp['completed_packets'][-1] == 1 and tp['pending_bytes'] == 0, 'Tags must finish page')
    at = 8
    def length():
        nonlocal at
        need(at+4 <= len(b),'metadata length bound')
        n = struct.unpack_from('<I',b,at)[0]; at += 4
        return n
    n = length(); need(n <= len(b)-at,'vendor bound'); at += n
    n = length(); need(n <= 1024 and n <= (len(b)-at)//4,'comment count bound')
    for _ in range(n):
        size = length(); need(size <= len(b)-at,'comment bound'); at += size
    padding = len(b)-at
    total = 0; previous = None; audio_pages = 0; audio = []
    for page in pages:
        completed = page['completed_packets']
        if not completed:
            continue
        if completed[-1] <= 1:
            need(page['granule'] == 0,'header granule'); continue
        need(completed[0] >= 2 and page['index'] > tag['end_page'],'mixed header/audio page')
        for number in completed:
            payload = packets[number]['data']
            need(len(payload) >= 2 and len(payload)-1 <= 1275,'unsupported empty/oversize frame')
            toc = payload[0]; config = toc >> 3
            need(toc & 3 == 0,'unsupported frame count code')
            need(config in (1,5,9,13,15,19,23,27,31),'unsupported duration')
            total += 960
            audio.append({'packet':number,'start_page':packets[number]['start_page'],
                          'end_page':page['index'],'bytes':len(payload),'toc':toc,
                          'config':config,'stereo_bit':(toc>>2)&1,'frames':960})
        gp = page['granule']; eos = bool(page['flags'] & 4)
        need(0 <= gp <= total,'audio granule domain')
        if audio_pages == 0:
            need(not eos and gp == total,'unsupported initial-position/EOS layout')
        if not eos:
            need(gp == total,'non-EOS cumulative granule')
        else:
            need(previous is not None and gp >= previous and gp >= preskip,'EOS granule order')
        previous = gp; audio_pages += 1
    last = pages[-1]
    need(last['completed_packets'] and last['completed_packets'][-1] >= 2,'EOS audio completion')
    granule = last['granule']; trim = total-granule
    need(0 < trim <= 960,'positive bounded tail trim not established')
    return {'serial':serial,'pages':pages,'audio_packets':audio,'header':{'version':version,'channels':channels,
            'preskip':preskip,'input_rate':rate,'gain':gain,'mapping_family':family,'tags_padding_bytes':padding},
            'coded_frames':total,'final_granule':granule,'tail_trim':trim,'presented_frames':granule-preskip,
            'continuation_pages':sum(bool(p['flags'] & 1) for p in pages)}
