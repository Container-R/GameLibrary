"""Synthetic records only. No Godot imports, launches or resource parsing."""
import copy,json,tempfile,shutil,subprocess,sys,unittest,uuid
from pathlib import Path
from oracle import check,load
from consumer import *
ROOT=Path(__file__).resolve().parent
U='12345678-1234-4234-8234-123456789abc'

def sample(mode):
    a,b,c,s,d='11','12','13','14','15'
    db=b if mode=='shallow' else '16';dc=c if mode!='all' else '17'
    def gradient(id_,color):return {'id':id_,'class':'Gradient','count':2,'colors':[color,[1,1,1,1]],'offsets':[0,1]}
    def graph(root,bi,ci,length,bcolor,ccolor):return {'root_id':root,'script_id':s,'length':length,'first3_ids':[bi,bi,ci],'slot3':137 if length==4 else None,'values':[gradient(bi,bcolor),gradient(bi,bcolor),gradient(ci,ccolor)]}
    def meta(id_,cls,path,builtin):return {'id':id_,'class':cls,'path':path,'built_in':builtin,'local_to_scene':False}
    red=[1,0,0,1];green=[0,1,0,1];blue=[0,0,1,1];magenta=[1,0,1,1]
    result={'schema':1,'invocation_uuid':U,'mode':mode,'process_id':123,'engine_version':{'major':4,'minor':6,'patch':3,'status':'stable','build':'official','hash':'7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3'},'constants':{'type_array':28,'storage':2,'always':1<<19,'never':1<<20,'none':0,'internal':1,'all':2},'setup':{'property':{'name':'entries','type':28,'usage':4102},'typed_array':False,'a':meta(a,'Resource','res://config.tres',False),'b':meta(b,'Gradient','res://config.tres::Gradient_B',True),'c':meta(c,'Gradient','res://external.tres',False),'script_path':'res://config.gd','a_graph':graph(a,b,c,3,red,green),'a2_graph':graph(a,b,c,3,red,green),'held_b':gradient(b,red),'held_c':gradient(c,green),'cached_c':gradient(c,green),'cached_root_id':a},'stages':[]}
    for i,label in enumerate(('copied','append','internal_edit','external_edit')):
        bc=blue if i>=2 and mode=='shallow' else red;cc=magenta if i>=3 and mode!='all' else green
        result['stages'].append({'stage':label,'a':graph(a,b,c,4 if i>=1 and mode=='shallow' else 3,bc,cc),'a2':graph(a,b,c,4 if i>=1 and mode=='shallow' else 3,bc,cc),'d':graph(d,db,dc,4 if i>=1 else 3,blue if i>=2 else red,magenta if i>=3 else green),'cached_root_id':a,'held_b':gradient(b,bc),'held_c':gradient(c,cc),'cached_c':gradient(c,cc),'same_array':mode=='shallow'})
    return copy.deepcopy(result)

def write_archive(root):
    for name in SOURCES:shutil.copyfile(ROOT/name,root/name)
    frozen=hashes(root,SOURCES);(root/'SOURCE-SHA256.json').write_text(json.dumps(frozen))
    out=root/'evidence'/U;out.mkdir(parents=True)
    base={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
    r={'status':'PASS','uuid':U,'original_source_directory':str(root),'original_process_directory':str(out),'source_sha256':frozen,'source_after':frozen.copy(),'manifest_sha256':sha((root/'SOURCE-SHA256.json').read_bytes()),'binary_before':BINARY_HASH,'binary_after':BINARY_HASH,'base_environment':base,'selected_environment':{k:str(out/'environment'/k) for k in KEYS},'behavior_processes':3,'version_processes':1,'processes':[],'inputs_before':{},'inputs_after':{},'parsed_sha256':{},'oracle':{}}
    for i,name in enumerate(('version',)+MODES):
        work=out if name=='version' else out/'projects'/name
        if name!='version':
            work.mkdir(parents=True)
            for n in INPUTS:shutil.copyfile(root/n,work/n)
            r['inputs_before'][name]=hashes(work,INPUTS);r['inputs_after'][name]=hashes(work,INPUTS)
            obj=sample(name);parsed=json.dumps(obj).encode();(out/f'{name}.json').write_bytes(parsed)
            raw=(BANNER+'\n\nRESULT_JSON:'+json.dumps(obj)+'\n').encode()
            r['parsed_sha256'][name]=sha(parsed);r['oracle'][name]=check(obj)
        else:raw=b'4.6.3.stable.official.7d41c59c4\n'
        (out/f'{name}.stdout').write_bytes(raw);(out/f'{name}.stderr').write_bytes(b'')
        r['processes'].append({'name':name,'argv':[BINARY,'--version'] if name=='version' else [BINARY,'--headless','--path',str(work),'--script',str(work/'main.gd'),'--',name,U],'cwd':str(work),'timeout_seconds':10 if name=='version' else 20,'status':'RETURNED','pid':123,'returncode':0,'attempted_utc':f'2026-11-01T03:00:0{i*2}+00:00','returned_utc':f'2026-11-01T03:00:0{i*2+1}+00:00','stdout_sha256':sha(raw),'stderr_sha256':sha(b'')})
    (out/'receipt.json').write_text(json.dumps(r));(root/'summary.json').write_text(json.dumps({'status':'PASS','uuid':U,'receipt_sha256':sha((out/'receipt.json').read_bytes())}))
    return out,r

class PureTests(unittest.TestCase):
    def test_synthetic_good_modes(self):
        for mode in MODES:self.assertEqual(check(sample(mode))['mode'],mode)
    def test_synthetic_bad_graphs(self):
        changes=[lambda x:x['stages'][2]['d']['first3_ids'].__setitem__(1,'99'),
                 lambda x:x['stages'][3]['held_c']['colors'].__setitem__(0,[1,0,1,1]),
                 lambda x:x['stages'][1]['a'].__setitem__('length',4),
                 lambda x:x['stages'][0]['d'].__setitem__('script_id','99'),
                 lambda x:x['setup']['property'].__setitem__('usage',2|(1<<20)),
                 lambda x:x['stages'].__setitem__(1,copy.deepcopy(x['stages'][0])),
                 lambda x:x.__setitem__('schema',True),
                 lambda x:x['setup']['held_b']['colors'][0].__setitem__(0,float('nan')),
                 lambda x:x['stages'][1]['d'].__setitem__('slot3',True),
                 lambda x:x['setup']['a'].__setitem__('id','0011')]
        for mutation in changes:
            x=sample('all');mutation(x)
            with self.assertRaises((ValueError,KeyError)):check(x)
    def test_json_envelope_rejection(self):
        for raw in ('{"a":1,"a":2}','{"a":NaN}'):
            with self.assertRaises(ValueError):load(raw)
        good=(BANNER+'\nRESULT_JSON:'+json.dumps(sample('all'))+'\n').encode()
        self.assertEqual(parse_stdout(good)['mode'],'all')
        for raw in (good+good,b'WARNING\n'+good,good[:-5],b'RESULT_JSON:{}\n'):
            with self.assertRaises(ValueError):parse_stdout(raw)
    def test_synthetic_archive_and_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);out,r=write_archive(root);self.assertEqual(len(verify_summary(root)),3)
            mutations=[lambda x:x.__setitem__('status','FAIL'),lambda x:x.__setitem__('uuid',str(uuid.uuid4())),lambda x:x['processes'][1].__setitem__('pid',124),lambda x:x['processes'][1].__setitem__('returncode',True),lambda x:x['processes'].pop(),lambda x:x['source_after'].__setitem__('main.gd','0'*64),lambda x:x['processes'][1].__setitem__('stdout_sha256','0'*64),lambda x:x['inputs_after']['all'].__setitem__('config.tres','0'*64)]
            for mutation in mutations:
                changed=copy.deepcopy(r);mutation(changed);(out/'receipt.json').write_text(json.dumps(changed))
                with self.assertRaises((ValueError,KeyError)):verify(root,out)
            (out/'receipt.json').write_text(json.dumps(r))
            (root/'summary.json').write_text(json.dumps({'status':'PASS','uuid':str(uuid.uuid4()),'receipt_sha256':'0'*64}))
            with self.assertRaises((ValueError,FileNotFoundError)):verify_summary(root)
    def test_exact_type_raw_parsed_and_derived_binding(self):
        self.assertFalse(exact_json_equal({'value':0},{'value':False}))
        self.assertFalse(exact_json_equal([1],[True]))
        self.assertFalse(exact_json_equal([1],[1.0]))
        self.assertTrue(exact_json_equal({'a':[1,True,None]},{'a':[1,True,None]}))
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);out,r=write_archive(root)
            parsed_path=out/'all.json';original=parsed_path.read_bytes()
            parsed=load(original)
            parsed['stages'][0]['d']['values'][0]['colors'][0][1]=False
            altered=json.dumps(parsed).encode();parsed_path.write_bytes(altered)
            r['parsed_sha256']['all']=sha(altered)
            (out/'receipt.json').write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'raw/parsed association'):verify(root,out)
            parsed_path.write_bytes(original);r['parsed_sha256']['all']=sha(original)
            r['oracle']['all']['mutable_payload_scope_verified']=1
            (out/'receipt.json').write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'derived oracle'):verify(root,out)

    def test_startup_fails_before_native(self):
        # Two Python-only rejection processes; no path can reach engine launch.
        for optimized in (True,False):
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp)
                for name in SOURCES:shutil.copyfile(ROOT/name,root/name)
                (root/'summary.json').write_text('{"status":"PASS","stale":true}')
                if not optimized:(root/'isolation.py').unlink()
                args=[sys.executable]+(['-O'] if optimized else [])+[str(root/'run.py')]
                child=subprocess.run(args,capture_output=True,timeout=10)
                self.assertNotEqual(child.returncode,0);self.assertFalse((root/'summary.json').exists())
                files=list((root/'evidence').glob('*/receipt.json'));self.assertEqual(len(files),1)
                r=load(files[0].read_bytes());self.assertEqual(r['status'],'FAIL');self.assertEqual(r['processes'],[])
if __name__=='__main__':unittest.main(verbosity=2)
