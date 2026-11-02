"""Synthetic data only, deliberately unrelated allocation values; no native."""
import copy,json,unittest
from pathlib import Path
from checker import check
ORACLE=Path(__file__).with_name('independent-oracle.json')
def h(n):return dict(full=n,index=n&0xfffff,version=n>>20)
def synthetic():
    R,H,S,B,L=map(h,[7,8,7,9,10])
    rows=[dict(kind='declaration',schema=1,cplusplus=201703,gcc=None,clang=None,entt=[3,13,2],entity_mask=1048575,version_mask=4095)]
    for stream,i,t,v in [('entities',0,'uint32',2),('entities',1,'uint32',2),('entities',2,'entity',R),('entities',3,'entity',H),('links',0,'uint32',1),('links',1,'entity',H),('links',2,'Link',{'target':R})]:rows.append(dict(kind='token',stream=stream,index=i,type=t,value=v))
    for j,name in enumerate(['prepared','entities_loaded','component_loaded']):
        rows.append(dict(kind='stage',stage=name,remote_box=R,remote_holder=H,local_seed=S,mapped_box=h(0xffffffff) if j==0 else B,mapped_holder=h(0xffffffff) if j==0 else L,source_target=R,archive_target=R,input_target=R if j==2 else None,loaded_target=R if j==2 else None,source_box_valid=True,source_holder_valid=True,seed_valid=True,box_contains=j>0,holder_contains=j>0,mapped_box_valid=j>0,mapped_holder_valid=j>0,holder_has_link=j==2,target_active_count=1 if j==0 else 3,target_link_count=1 if j==2 else 0,entity_written=4,link_written=3,entity_read=4 if j>0 else 0,link_read=3 if j==2 else 0,loaded_target_in_local_valid=True if j==2 else None,loaded_target_equals_seed=True if j==2 else None))
    return copy.deepcopy(rows)
def raw(rows):return ('\n'.join(json.dumps(r,separators=(',',':')) for r in rows)+'\n').encode()
class Content(unittest.TestCase):
    def test_valid_synthetic_and_descriptive_false(self):
        rows=synthetic();self.assertEqual(len(check(raw(rows),ORACLE)),11)
        for row in rows[8:]:row['local_seed']=h(6)
        rows[-1]['loaded_target_in_local_valid']=False;rows[-1]['loaded_target_equals_seed']=False
        self.assertEqual(len(check(raw(rows),ORACLE)),11)
    def test_meaningful_counterexamples(self):
        changes=[(6,'value',h(7)),(1,'value',3),(7,'value',{'target':h(9)}),(10,'loaded_target',h(9)),(10,'input_target',h(9)),(10,'loaded_target_in_local_valid',False),(10,'loaded_target_equals_seed',False),(8,'input_target',h(0xffffffff)),(8,'mapped_box',None),(9,'stage','prepared'),(9,'link_read',3),(10,'link_read',2),(8,'entity_written',7),(10,'holder_has_link',False),(9,'mapped_box',h(7)),(10,'mapped_holder',h(11)),(0,'schema',True),(0,'gcc',[True,1,2]),(0,'entt',[3,13,3]),(1,'index',False),(10,'target_active_count',True),(9,'box_contains',1),(8,'remote_box',h(-1)),(8,'remote_holder',h(2**32)),(8,'local_seed',{'full':7,'index':8,'version':0}),(4,'value',h(7)),(10,'extra',1)]
        for row,key,value in changes:
            with self.subTest(row=row,key=key):
                r=synthetic();r[row][key]=value
                with self.assertRaises((ValueError,KeyError,TypeError)):check(raw(r),ORACLE)
    def test_all_ten_consistent_reserved_live_handles(self):
        # Start with five distinct live values, so each role is challenged alone.
        for role,old in [('R',7),('H',8),('S',6),('B',9),('L',10)]:
            for reserved in [0x000fffff,0xfff00000]:
                with self.subTest(role=role,reserved_kind='index' if reserved==0x000fffff else 'version'):
                    rows=synthetic()
                    for row in rows[8:]:row['local_seed']=h(6)
                    def replace(value):
                        if isinstance(value,dict):
                            if list(value)==['full','index','version'] and value['full']==old:return h(reserved)
                            return {k:replace(v) for k,v in value.items()}
                        if isinstance(value,list):return [replace(v) for v in value]
                        return value
                    rows=replace(rows)
                    final=rows[-1];r=final['loaded_target']['full']
                    final['loaded_target_equals_seed']=r==final['local_seed']['full']
                    final['loaded_target_in_local_valid']=r in {final[k]['full'] for k in ['local_seed','mapped_box','mapped_holder']}
                    with self.assertRaisesRegex(ValueError,'live_reserved_handle'):check(raw(rows),ORACLE)
    def test_nonzero_nonreserved_versions_not_forbidden(self):
        rows=synthetic()
        def bump(value):
            if isinstance(value,dict):
                if list(value)==['full','index','version'] and value['full']!=0xffffffff:return h(value['full']+(1<<20))
                return {k:bump(v) for k,v in value.items()}
            if isinstance(value,list):return [bump(v) for v in value]
            return value
        self.assertEqual(len(check(raw(bump(rows)),ORACLE)),11)
    def test_encoding_and_shape_rejections(self):
        good=raw(synthetic());r=synthetic();del r[8]['seed_valid']
        cases=[raw(r),raw(synthetic()[:-1]),raw(synthetic()+[synthetic()[-1]]),good[:-1],good.replace(b'\n',b'\r\n'),b'\xff'+good,good.replace(b'"schema":1',b'"schema":1,"schema":1',1),good.replace(b'"cplusplus":201703',b'"cplusplus":NaN',1)]
        for item in cases:
            with self.subTest(length=len(item)):
                with self.assertRaises((ValueError,KeyError,TypeError)):check(item,ORACLE)
if __name__=='__main__':unittest.main()
