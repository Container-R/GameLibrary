"""Synthetic receipt tests only: no FFmpeg, loader, or media process invocation."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import consumer as c
import signals

ROOT=Path(__file__).resolve().parent
UID='12345678-1234-4234-8234-123456789abc'

def write_json(path,obj): path.write_text(json.dumps(obj,indent=2)+'\n')

def synthetic(root):
    for name in c.SOURCES: shutil.copyfile(ROOT/name,root/name)
    manifest=c.hashes(root);write_json(root/'SOURCE-SHA256.json',manifest)
    out=root/'evidence'/UID;out.mkdir(parents=True)
    original=Path('/synthetic/not-an-execution/evidence')/UID
    ih={k:c.sha(v) for k,v in c.inputs().items()}
    r={'status':'PASS','uuid':UID,'original_directory':str(original),
       'manifest_sha256':c.sha((root/'SOURCE-SHA256.json').read_bytes()),
       'source_before':manifest,'source_after':dict(manifest),'tools_before':dict(c.PINS),'tools_after':dict(c.PINS),
       'inputs':{},'processes':[],'outputs':{}}
    for name,data in c.inputs().items(): r['inputs'][name]=c.archive(out,name,data)
    for i,mode in enumerate(('version',)+c.MODES):
        env=dict(c.BASE);env.update({k:str(original/'environment'/mode/k) for k in c.ENVKEYS})
        p={'name':mode,'argv':c.argv_for(mode,original),'cwd':str(original),'environment':env,'timeout_seconds':20,
           'status':'RETURNED','pid':100+i,'attempted_utc':f'2026-11-01T00:00:0{i}+00:00',
           'returned_utc':f'2026-11-01T00:00:0{i}+00:00','returncode':0,'inputs_before':dict(ih),'inputs_after':dict(ih)}
        for stream in ('stdout','stderr'):
            data=c.BANNER+b' synthetic fixture, not native evidence\n' if mode=='version' and stream=='stdout' else b''
            (out/(mode+'.'+stream)).write_bytes(data);p[stream+'_sha256']=c.sha(data)
        r['processes'].append(p)
        if mode!='version':
            r['outputs'][mode]={'archive':c.archive(out,mode,c.expected(mode)),
                              'check':{'frames':4096,'bytes':16384,'all_samples_equal':True}}
    bind(root,r)
    return r,out

def bind(root,r):
    path=root/'evidence'/UID/'receipt.json';write_json(path,r)
    write_json(root/'summary.json',{'status':'PASS','uuid':UID,'receipt_sha256':c.sha(path.read_bytes()),'processes':4,'mixing_conditions':3})

class Pure(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.r,self.out=synthetic(self.root)
    def tearDown(self): self.tmp.cleanup()
    def test_literal_sequences(self):
        self.assertTrue(c.exact(signals.inputs(),c.inputs()))
        for mode in c.MODES:
            self.assertEqual(signals.check(mode,c.expected(mode))['frames'],4096)
            bad=bytearray(c.expected(mode));bad[8192]^=1
            with self.assertRaises(ValueError): signals.check(mode,bytes(bad))
        with self.assertRaises(ValueError): signals.check(c.MODES[0],bytes.fromhex('0000807f')*4096)
    def test_valid_portable_synthetic(self):
        self.assertEqual(c.verify(self.root)['mixing_conditions'],3)
        # No .f32le binary is needed; canonical hex is complete.
        self.assertFalse(list(self.out.glob('*.f32le')))
    def test_strict_types_and_json(self):
        for raw in ('{"x":0,"x":1}','{"x":NaN}','{"x":Infinity}','{"x":1e999}'):
            with self.assertRaises(ValueError): c.load(raw)
        for path,value in ((('processes',0,'returncode'),False), (('outputs','short-normalized','check','all_samples_equal'),1),
                           (('inputs','A','bytes'),16384.0), (('processes',0,'pid'),True)):
            r=copy.deepcopy(self.r);node=r
            for key in path[:-1]:node=node[key]
            node[path[-1]]=value;bind(self.root,r)
            with self.subTest(path=path),self.assertRaises(ValueError):c.verify(self.root)
    def test_hash_log_and_output_tampering(self):
        r=copy.deepcopy(self.r);r['tools_after'][c.LIB]='0'*64;bind(self.root,r)
        with self.assertRaises(ValueError):c.verify(self.root)
        bind(self.root,self.r)
        log=self.out/'short-normalized.stderr';log.write_bytes(b'error')
        with self.assertRaises(ValueError):c.verify(self.root)
        log.write_bytes(b'')
        # Rebinding corrupted output archive hash cannot change literal expectation.
        bad=bytearray(c.expected('short-normalized'));bad[8192]^=1
        r=copy.deepcopy(self.r);r['outputs']['short-normalized']['archive']=c.archive(self.out,'short-normalized',bytes(bad));bind(self.root,r)
        with self.assertRaises(ValueError):c.verify(self.root)
    def test_command_environment_and_counts(self):
        for kind in ('argv','environment','count','timeout'):
            r=copy.deepcopy(self.r)
            if kind=='argv':r['processes'][1]['argv'][0]='/bin/other'
            if kind=='environment':r['processes'][0]['environment']['SECRET']='unexpected'
            if kind=='count':r['processes'].pop()
            if kind=='timeout':r['processes'][0]['status']='TIMEOUT'
            bind(self.root,r)
            with self.subTest(kind=kind),self.assertRaises(ValueError):c.verify(self.root)
    def test_stale_pass_cleared_before_guards(self):
        # Only Python children; both fail before the native-launching code.
        for kind in ('optimized','missing-helper'):
            with tempfile.TemporaryDirectory() as td:
                root=Path(td)
                for name in c.SOURCES:shutil.copyfile(ROOT/name,root/name)
                (root/'summary.json').write_text('{"status":"PASS"}')
                if kind=='missing-helper':(root/'isolation.py').unlink()
                argv=[sys.executable,'-B']+(['-O'] if kind=='optimized' else [])+[str(root/'run.py')]
                p=subprocess.run(argv,cwd=root,capture_output=True,timeout=10)
                self.assertEqual(p.returncode,1)
                self.assertFalse((root/'summary.json').exists())
                receipts=list((root/'evidence').glob('*/receipt.json'));self.assertEqual(len(receipts),1)
                r=c.load(receipts[0].read_bytes());self.assertEqual(r['status'],'FAIL');self.assertEqual(r['processes'],[])

if __name__=='__main__':unittest.main(verbosity=2)
