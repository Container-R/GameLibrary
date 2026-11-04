"""Pure synthetic JSON tests. No compiled fixture, subprocess, or Detour call."""
import copy
import json
from pathlib import Path
import unittest
import consumer

EXPECTED=consumer.strict_json((Path(__file__).parent/'expected.json').read_bytes())

def synthetic():
    # Synthetic only: this is not used by the native fixture or runner.
    def substitute(value):
        if type(value) is str:
            return {'$P0':'101','$P1':'102','$P2':'103','$POSITIVE_INT':512}.get(value,value)
        if type(value) is list: return [substitute(x) for x in value]
        if type(value) is dict: return {k:substitute(v) for k,v in value.items()}
        return value
    return substitute(EXPECTED)

class ConsumerTests(unittest.TestCase):
    def reject(self, value):
        with self.assertRaises((ValueError,OverflowError,UnicodeError)):
            consumer.validate(consumer.strict_json(json.dumps(value,allow_nan=True)))
    def test_synthetic_success(self):
        self.assertEqual(consumer.validate(synthetic())['validation'],'consumer_only')
    def test_numeric_coordinates_accept_float(self):
        v=synthetic();v['setup']['vertices'][0][0]=0.0
        self.assertEqual(consumer.validate(v)['status'],'pass')
    def test_wrong_status_bits(self):
        for bits in (16,64,32,1<<31):
            v=synthetic();v['cases'][2]['status']|=bits;self.reject(v)
    def test_status_bool_or_float(self):
        for wrong in (True,1073741824.0):
            v=synthetic();v['cases'][0]['status']=wrong;self.reject(v)
    def test_wrong_t_or_rounded_max(self):
        for wrong in (.5,1.0,3.40282347e38):
            v=synthetic();v['cases'][0]['t']=wrong;self.reject(v)
        v=synthetic();v['cases'][2]['t']=3.4028234663852886e38;self.reject(v)
    def test_nohit_normal_is_null(self):
        v=synthetic();v['cases'][0]['hit_normal']=[0,0,0];self.reject(v)
    def test_wall_normal_or_edge(self):
        for key,wrong in (('hit_normal',[0,0,1]),('hit_edge',2)):
            v=synthetic();v['cases'][2][key]=wrong;self.reject(v)
    def test_zero_sentinels_and_missing_tail(self):
        for index,slot in ((0,2),(1,2),(2,1),(2,2),(3,2)):
            v=synthetic();v['cases'][index]['path'][slot]='102';self.reject(v)
        v=synthetic();v['cases'][3]['path']=v['cases'][3]['path'][:2];self.reject(v)
    def test_unknown_ref(self):
        v=synthetic();v['cases'][0]['path'][0]='999';self.reject(v)
    def test_refs_canonical_unique(self):
        for wrong in ('0','001','+1',' 1','١',101,'102'):
            v=synthetic();v['setup']['refs'][0]=wrong;self.reject(v)
    def test_wrong_mesh_fields(self):
        for action in ('neis','link','vertex','header','filter'):
            v=synthetic()
            if action=='neis':v['setup']['polygons'][0]['neis'][1]=3
            elif action=='link':v['setup']['polygons'][1]['links'].reverse()
            elif action=='vertex':v['setup']['vertices'][7][2]=3
            elif action=='header':v['setup']['header']['detail_tri_count']=7
            else:v['setup']['filter'][2]=2
            self.reject(v)
    def test_counts_order_stage(self):
        for action in ('calls','path_count','order','completed','stage'):
            v=synthetic()
            if action=='calls':v['calls']['raycast']=4
            elif action=='path_count':v['cases'][0]['path_count']=1
            elif action=='order':v['cases'].reverse()
            elif action=='completed':v['completed'].pop()
            else:v['stage']='other'
            self.reject(v)
    def test_wrong_commit_or_protocol(self):
        for key in ('commit','protocol'):
            v=synthetic();v[key]='wrong';self.reject(v)
    def test_extra_missing_keys(self):
        v=synthetic();v['extra']=1;self.reject(v)
        v=synthetic();del v['cases'][0]['t'];self.reject(v)
    def test_positive_data_size(self):
        for wrong in (0,-1,True,1.0):
            v=synthetic();v['setup']['data_size']=wrong;self.reject(v)
    def test_bool_physical_numeric(self):
        v=synthetic();v['setup']['vertices'][0][0]=False;self.reject(v)
        v=synthetic();v['cases'][2]['hit_normal'][0]=False;self.reject(v)
    def test_failure_not_success(self):
        v=synthetic();v['status']='fail';self.reject(v)
        v['setup']=None;self.reject(v)
    def test_raw_duplicate_key(self):
        raw=json.dumps(synthetic());raw=raw.replace('"status": "pass"','"status": "pass", "status": "pass"',1)
        with self.assertRaises(ValueError):consumer.strict_json(raw)
    def test_raw_trailing_or_missing(self):
        raw=json.dumps(synthetic())
        for wrong in (raw+'{}',raw[:-1],''):
            with self.assertRaises(ValueError):consumer.strict_json(wrong)
    def test_raw_nonfinite(self):
        raw=json.dumps(synthetic())
        for token in ('NaN','Infinity','-Infinity','1e999'):
            wrong=raw.replace('"t": 0.5','"t": '+token)
            with self.assertRaises(ValueError):consumer.strict_json(wrong)
    def test_raw_utf8(self):
        with self.assertRaises(UnicodeError):consumer.strict_json(b'\xff')
    def test_negative_zero(self):
        v=synthetic();v['cases'][2]['hit_normal'][0]=-0.0
        self.assertEqual(consumer.validate(v)['status'],'pass')

if __name__=='__main__':unittest.main(verbosity=2)
