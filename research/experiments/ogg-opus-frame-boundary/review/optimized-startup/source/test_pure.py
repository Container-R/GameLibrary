"""Synthetic framing only. No valid entropy-coded media or external processes."""
import copy, json, struct, tempfile, unittest
from pathlib import Path
from reader import read, crc
from consumer import integers, verify

def checksum(b):
    # Polynomial remainder of message shifted by32, distinct implementation.
    value=int.from_bytes(b,'big')<<32
    polynomial=0x104c11db7
    while value.bit_length()>32:
        value ^= polynomial << (value.bit_length()-33)
    return value

def page(seq,flags,gp,packets):
    laces=[]; payload=b''
    for packet in packets:
        laces += [255]*(len(packet)//255)+[len(packet)%255]
        payload+=packet
    header=b'OggS\0'+bytes([flags])+struct.pack('<qIII',gp,77,seq,0)+bytes([len(laces)])
    b=bytearray(header+bytes(laces)+payload)
    struct.pack_into('<I',b,22,checksum(b))
    return bytes(b)
HEAD=b'OpusHead'+struct.pack('<BBHIhB',1,2,100,48000,0,0)
TAGS=b'OpusTags'+struct.pack('<II',0,0)+b'allowed-padding'
# Artificial bytes test framing only, never submitted to a decoder.
AUDIO=b'\x98\x55'
def fixture(head=HEAD,tags=TAGS,audio=AUDIO,gp=1500):
    return page(0,2,0,[head])+page(1,0,0,[tags])+page(2,0,960,[audio])+page(3,4,gp,[audio])

class Tests(unittest.TestCase):
    def test_positive_subset(self):
        r=read(fixture())
        self.assertEqual((r['coded_frames'],r['final_granule'],r['tail_trim'],r['presented_frames']),(1920,1500,420,1400))
        self.assertEqual(r['header']['tags_padding_bytes'],15)
    def test_crc(self):
        for b in (b'',b'abc',bytes(range(256))): self.assertEqual(crc(b),checksum(b))
        b=bytearray(fixture());b[-1]^=1
        with self.assertRaisesRegex(ValueError,'CRC'): read(bytes(b))
    def test_structure_mutants(self):
        candidates=[fixture()[:-1],fixture()+b'junk',fixture(gp=-2),fixture(gp=1921),fixture(gp=1920),fixture(gp=959),
                    fixture(audio=b'\x98'),fixture(audio=b'\x99\x55'),fixture(audio=b'\x80\x55'),
                    fixture(tags=b'OpusTags'+struct.pack('<II',0,0xffffffff)),
                    fixture(head=b'OpusHead'+struct.pack('<BBHIhB',1,2,0,48000,0,0)),
                    page(0,2,0,[HEAD,TAGS])+page(1,0,960,[AUDIO])+page(2,4,1500,[AUDIO]),
                    page(0,2,0,[HEAD])+page(1,0,960,[TAGS,AUDIO])+page(2,4,1500,[AUDIO]),
                    page(0,2,0,[HEAD])+page(1,0,0,[TAGS])+page(2,4,500,[AUDIO])]
        for i,b in enumerate(candidates):
            with self.subTest(i=i),self.assertRaises(ValueError): read(b)
    def test_continuation_semantics(self):
        tags=b'OpusTags'+struct.pack('<II',0,0)+bytes(300)
        # Construct a continuation explicitly, distinct from helper's complete packets.
        def fragment(seq,flag,gp,lace,body):
            b=bytearray(b'OggS\0'+bytes([flag])+struct.pack('<qIII',gp,77,seq,0)+bytes([len(lace)])+bytes(lace)+body)
            struct.pack_into('<I',b,22,checksum(b));return bytes(b)
        raw=page(0,2,0,[HEAD])+fragment(1,0,-1,[255],tags[:255])+fragment(2,1,0,[61],tags[255:])+page(3,0,960,[AUDIO])+page(4,4,1500,[AUDIO])
        self.assertEqual(read(raw)['continuation_pages'],1)
        bad=page(0,2,0,[HEAD])+fragment(1,0,-1,[255],tags[:255])+fragment(2,0,0,[61],tags[255:])+page(3,0,960,[AUDIO])+page(4,4,1500,[AUDIO])
        with self.assertRaises(ValueError):read(bad)
    def test_consumer_fail_closed_types_status(self):
        for v in (True,1.0,{'x':[False]}):
            with self.assertRaises(ValueError):integers(v)
        integers({'x':[0,1,-1,'PASS']})
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'receipt.json').write_text(json.dumps({'status':'FAIL'}))
            with self.assertRaisesRegex(ValueError,'not PASS'):verify(p,p)

if __name__=='__main__': unittest.main(verbosity=2)
