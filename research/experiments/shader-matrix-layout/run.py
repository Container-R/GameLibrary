"""Finite compiler-decoration and host-interpretation oracle."""
import hashlib,json,os,platform,re,struct,subprocess,sys,uuid
from pathlib import Path
R=Path(__file__).resolve().parent
O=R/'results';O.mkdir(exist_ok=True)
(O/'summary.json').unlink(missing_ok=True)
inv=str(uuid.uuid4())
(O/'invocation.json').write_text(json.dumps({'id':inv,'state':'RUNNING'})+'\n')
def need(c,m):
 if not c: raise RuntimeError(m)
def raw(v):return v.decode(errors='replace') if isinstance(v,bytes) else (v or '')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decorations(text,case):
 lines=[x.strip().split() for x in text.splitlines() if x.strip() and not x.strip().startswith(';')]
 # Resolve the named block and member, not the first arbitrary decoration.
 ids=[x[1] for x in lines if len(x)==3 and x[0]=='OpName' and x[2]=='"Params"']
 need(len(ids)==1,'unique Params')
 bid=ids[0]
 need(['OpMemberName',bid,'0','"transform"'] in lines,'member identity')
 ds=[x[3:] for x in lines if len(x)>=4 and x[:3]==['OpMemberDecorate',bid,'0']]
 expected='RowMajor' if case=='row' else 'ColMajor'
 need(sorted(ds)==sorted([[expected],['Offset','0'],['MatrixStride','16']]),'exact member decorations')
 types={x[0]:x[2:] for x in lines if len(x)>3 and x[1]=='='}
 need(types[bid][0]=='OpTypeStruct' and len(types[bid])==2,'single matrix member')
 mt=types[types[bid][1]];need(mt[0]=='OpTypeMatrix' and mt[2]=='3','matrix columns')
 vt=types[mt[1]];need(vt[0]=='OpTypeVector' and vt[2]=='3','matrix rows')
 need(types[vt[1]]==['OpTypeFloat','32'],'float32')
 need(any('OpMatrixTimesVector' in x for x in lines),'matrix operation exists')
 return {'major':expected,'offset':0,'matrix_stride':16,'columns':3,'rows':3,'scalar_bits':32}
def decode(data,major):
 f=struct.unpack('<12f',data)
 return [[f[r*4+c] if major=='RowMajor' else f[c*4+r] for c in range(3)] for r in range(3)]
def product(m):return [sum(row[i]*[1,2,3][i] for i in range(3)) for row in m]
try:
 need(not sys.flags.optimize,'Run without -O')
 contract=json.loads((R/'contract.json').read_text())
 summary={'invocation_id':inv,'python':sys.version,'platform':platform.platform(),
 'source_sha256':{n:sha(R/n) for n in ['run.py','compile_case.py','row.comp','column.comp','contract.json']},'cases':[]}
 for case in ['row','column']:
  command=[sys.executable,str(R/'compile_case.py'),case]
  receipt={'command':command,'timeout_seconds':20}
  try:
   p=subprocess.run(command,capture_output=True,text=True,timeout=20)
  except subprocess.TimeoutExpired as e:
   (O/(case+'.stdout')).write_text(raw(e.stdout));(O/(case+'.stderr')).write_text(raw(e.stderr));receipt['timeout']=True
   (O/(case+'.status.json')).write_text(json.dumps(receipt,indent=2)+'\n');raise
  except OSError as e:
   receipt['spawn_error']=repr(e);(O/(case+'.status.json')).write_text(json.dumps(receipt,indent=2)+'\n');raise
  (O/(case+'.stdout')).write_text(p.stdout);(O/(case+'.stderr')).write_text(p.stderr)
  receipt['returncode']=p.returncode;(O/(case+'.status.json')).write_text(json.dumps(receipt,indent=2)+'\n')
  need(p.returncode==0 and not p.stderr,'child failure')
  records=[json.loads(x[12:]) for x in p.stdout.splitlines() if x.startswith('RESULT_JSON=')]
  need(len(records)==1,'exactly one result');r=records[0]
  (O/(case+'.json')).write_text(json.dumps(r,indent=2)+'\n');(O/(case+'.spvasm')).write_text(r['assembly'])
  need(r['case']==case and r['status']==r['errors']==r['warnings']==0 and not r['diagnostics'],'compiler diagnostics')
  need(r['assembly_length']==len(r['assembly'].encode()) and r['source_sha256']==sha(R/(case+'.comp')),'length/source')
  need(r['library_sha256']==sha(Path(r['library'])),'library identity')
  d=decorations(r['assembly'],case)
  vals=contract[case+'_storage_floats'];data=struct.pack('<12f',*vals)
  (O/(case+'.host.hex')).write_text(data.hex()+'\n')
  need(len(data)==48,'finite matrix bytes')
  matrix=decode(data,d['major']);math=product(matrix)
  need(matrix==contract['matrix_rows'] and math==[14,32,53],'correct host contract')
  summary['cases'].append({'case':case,'decorations':d,'matrix':matrix,'cpu_product':math,'library_sha256':r['library_sha256'],'assembly_sha256':sha(O/(case+'.spvasm'))})
 wrong=product(decode(struct.pack('<12f',*contract['row_storage_floats']),'ColMajor'))
 need(wrong==[30,36,45] and wrong!=[14,32,53],'intentional wrong host interpretation')
 summary.update(status='PASS',wrong_cpu_product=wrong,actual_compiler_processes=2)
 (O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 (O/'invocation.json').write_text(json.dumps({'id':inv,'state':'PASS'})+'\n')
 print('PASS: two actual compiler assembly cases; host products are CPU model only')
except BaseException as e:
 (O/'summary.json').unlink(missing_ok=True)
 (O/'invocation.json').write_text(json.dumps({'id':inv,'state':'FAILED','exception':repr(e)})+'\n')
 raise
