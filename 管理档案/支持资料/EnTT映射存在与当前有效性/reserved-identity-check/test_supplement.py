"""Synthetic records only. No compiler, runner, subprocess or signal calls."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import check_supplement as supplement

def h(n):return dict(full=n,index=n&0xfffff,version=n>>20)
def sample():
    rows=[dict(kind='declaration',schema=1,cplusplus=201703,gcc=None,clang=None,entt=[3,13,2],entity_mask=1048575,version_mask=4095)]
    for i,(typ,v) in enumerate([('uint32',1),('uint32',1),('entity',9)]):
        rows.append(dict(kind='token',index=i,type=typ,value=v))
    for i,name in enumerate(['before_load','loaded','externally_destroyed','reloaded']):
        rows.append(dict(kind='stage',stage=name,source=h(9),seed=h(8),
            mapped_now=h([0xffffffff,2,2,1048578][i]),mapped_initial=None if i==0 else h(2),
            contains=i>0,mapped_nonnull=i>0,mapped_valid=i in [1,3],active_count=[1,2,1,2][i],
            initial_valid=[None,True,False,False][i],source_valid=True,seed_valid=True,
            input_consumed=3 if i in [1,3] else None))
    return rows

def raw(rows):return ('\n'.join(json.dumps(x,separators=(',',':')) for x in rows)+'\n').encode()

def old_check(data):
    path,oracle=supplement.bound_files()
    spec=importlib.util.spec_from_file_location('old_frozen',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m.check(data,oracle)

class Tests(unittest.TestCase):
    def test_valid_and_stale_preserved(self):
        rows=supplement.check(raw(sample()))
        self.assertFalse(rows[6]['mapped_valid'])
        self.assertFalse(rows[7]['initial_valid'])
        self.assertIsNone(rows[4]['mapped_initial'])
        self.assertEqual(rows[4]['mapped_now'],h(0xffffffff))

    def test_eight_consistent_old_false_accepts(self):
        for role in ['source','seed','initial','reloaded']:
            for value in [0xfffff,0xfff00000]:
                with self.subTest(role=role,value=value):
                    x=sample()
                    if role in ['source','seed']:
                        for row in x[4:]:row[role]=h(value)
                        if role=='source':x[3]['value']=value
                    elif role=='initial':
                        for row in x[5:]:row['mapped_initial']=h(value)
                        for row in x[5:7]:row['mapped_now']=h(value)
                    else:x[7]['mapped_now']=h(value)
                    old_check(raw(x)) # Demonstrate the original consumer's actual hole.
                    with self.assertRaises(supplement.SupplementError):supplement.check(raw(x))

    def test_all_fourteen_identity_positions(self):
        for i in range(4):
            for field in ['source','seed']+(['mapped_now','mapped_initial'] if i else []):
                for value in [0xfffff,0xfff00000]:
                    with self.subTest(stage=i,field=field,value=value):
                        x=sample();x[4+i][field]=h(value)
                        with self.assertRaises(ValueError):supplement.check(raw(x))

    def test_original_strict_checks_remain(self):
        x=sample();x[5]['active_count']=True
        y=sample();y[7]['mapped_now']=h(2)
        z=sample();z[4]['mapped_initial']=h(0xffffffff)
        for data in [raw(x),raw(y),raw(z),raw(sample()[:-1]),raw(sample()).replace(b'"schema":1',b'"schema":1,"schema":1')]:
            with self.subTest(data_kind='synthetic_rejection'):
                with self.assertRaises(ValueError):supplement.check(data)

    def test_checker_and_oracle_bytes_bound(self):
        for name in ['frozen_checker.py','frozen_oracle.json']:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                for f in ['frozen_checker.py','frozen_oracle.json']:
                    (root/f).write_bytes((supplement.ROOT/f).read_bytes())
                with (root/name).open('ab') as out:out.write(b'\n')
                with patch.object(supplement,'ROOT',root):
                    with self.assertRaises(supplement.SupplementError):supplement.check(raw(sample()))

if __name__=='__main__':unittest.main()
