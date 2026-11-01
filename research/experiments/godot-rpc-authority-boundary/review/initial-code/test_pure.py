"""Synthetic traces only. No subprocess, engine, sockets or media."""
import copy
import itertools
import json
import unittest
from oracle import BANNER, expected_server, expected_client, payload, check_payloads, parse_stream, loads

class FiniteOracle(unittest.TestCase):
    def pair(self): return payload('server',17,expected_server(17)),payload('client',17,expected_client(17))
    def test_literal_sequence_and_connection_permutations(self):
        for order in itertools.permutations(('PEER_CONNECTED','CONNECTED','WELCOME')):
            server=payload('server',17,expected_server(17));client=payload('client',17,expected_client(17,order))
            self.assertEqual(check_payloads(server,client)['command_rpc_deliveries'],3)
    def test_policy_and_identity_mutations(self):
        for index,key,value in ((4,'sender',1),(7,'fresh_sender',17),(8,'reason','ownership'),(10,'sender',False),(14,'captured_sender',1),(22,'last_index',2)):
            server,client=self.pair();server['trace'][index][key]=value
            with self.assertRaises(ValueError):check_payloads(server,client)
        server,client=self.pair();client['version']['patch']=9
        with self.assertRaises(ValueError):check_payloads(server,client)
    def test_raw_envelope(self):
        server,_=self.pair()
        raw=(BANNER+'\n'+''.join('EVENT_JSON='+json.dumps(r)+'\n' for r in server['trace'])+'RESULT_JSON='+json.dumps(server)+'\n').encode()
        self.assertEqual(parse_stream(raw,b'')[1][0],server)
        for bad,err in ((raw+b'ERROR: injected\n',b''),(raw,b'ERROR\n'),(raw+b'RESULT_JSON={}\n',b''),(raw.replace(b'"sender": 17',b'"sender": 18',1),b'')):
            with self.assertRaises(ValueError):parse_stream(bad,err)
    def test_json_nonfinite_duplicates(self):
        for text in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}','{"x":1e999}'):
            with self.assertRaises(ValueError):loads(text)
    def test_synthetic_receipt_and_mutations(self):
        import tempfile
        import uuid
        from pathlib import Path
        from consumer import consume,sha
        from oracle import SOURCES,BASE_ENV,BINARY,VERSION
        root=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory() as temp:
            rid=str(uuid.uuid4()); out=Path(temp)/rid;out.mkdir()
            original='/synthetic/fixture'; invocation=original+'/evidence/'+rid
            server,client=self.pair()
            for role,data in (('server',server),('client',client)):
                (out/(role+'.json')).write_text(json.dumps(data))
                (out/(role+'.stdout')).write_text(BANNER+'\n'+''.join('EVENT_JSON='+json.dumps(r)+'\n' for r in data['trace'])+'RESULT_JSON='+json.dumps(data)+'\n')
                (out/(role+'.stderr')).write_bytes(b'')
            (out/'version.stdout').write_text(VERSION+'\n');(out/'version.stderr').write_bytes(b'')
            sources={name:sha(root/name) for name in SOURCES};processes=[]
            for i,name in enumerate(('version','server','client')):
                argv=['/usr/local/bin/godot','--version'] if name=='version' else ['/usr/local/bin/godot','--headless','--path',original,'--single-threaded-scene','--script',original+'/main.gd','--',name,invocation+'/STOP']
                processes.append(dict(name=name,argv=argv,cwd=original,selected_environment={key:invocation+'/environment/'+name+'/'+key for key in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')},attempted_utc='2026-11-01T00:00:00+00:00',returned_utc='2026-11-01T00:00:00+00:00',status='RETURNED',pid=100+i,exit_code=0))
            receipt=dict(uuid=rid,original_source_root=original,original_invocation=invocation,status='PASS',processes=processes,orchestration=[{'kind':'ATTEMPT','name':'version'},{'kind':'VERSION_ACCEPTED'},{'kind':'ATTEMPT','name':'server'},{'kind':'SERVER_READY_ACCEPTED'},{'kind':'ATTEMPT','name':'client'},{'kind':'BOTH_TERMINALS_ACCEPTED'},{'kind':'STOP_CREATED'}],source_before=sources,source_after=sources,binary_before=BINARY,binary_after=BINARY,base_environment=BASE_ENV,stop_initially_absent=True,version_processes=1,behavior_processes=2,output_sha256={p.name:sha(p) for p in out.iterdir()})
            def put(value):(out/'receipt.json').write_text(json.dumps(value))
            put(receipt);self.assertEqual(consume(root,out)['status'],'PASS')
            for field,value in (('behavior_processes',True),('binary_after','0'*64),('uuid',str(uuid.uuid4())),('source_after',{}),('base_environment',dict(BASE_ENV,LD_PRELOAD='untrusted')),('stop_initially_absent',False)):
                mutant=copy.deepcopy(receipt);mutant[field]=value;put(mutant)
                with self.assertRaises(ValueError):consume(root,out)

    def test_client_stop_and_wait(self):
        server,client=self.pair();client['trace'][6],client['trace'][7]=client['trace'][7],client['trace'][6]
        with self.assertRaises(ValueError):check_payloads(server,client)

if __name__=='__main__':unittest.main()
