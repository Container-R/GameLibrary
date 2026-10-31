import sys,json,hashlib,struct
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('assertions required')
p=Path(__file__).resolve().parent/'fixture';o=p/'results'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=json.loads((o/'summary.json').read_text());i=json.loads((o/'invocation.json').read_text())
assert s['status']==i['state']=='PASS' and s['invocation_id']==i['id']
assert all(h(p/n)==v for n,v in s['source_sha256'].items())
rows=[[1,2,3],[4,5,6],[7,8,10]]
for case,major,floats in [('row','RowMajor',[1,2,3,99,4,5,6,99,7,8,10,99]),('column','ColMajor',[1,4,7,99,2,5,8,99,3,6,10,99])]:
 raw=(o/(case+'.stdout')).read_text().splitlines();rs=[json.loads(x[12:]) for x in raw if x.startswith('RESULT_JSON=')];assert len(rs)==1
 r=rs[0];assert r['status']==r['errors']==r['warnings']==0 and r['diagnostics']==''
 assert r['library_sha256']==h(Path(r['library'])) and r['source_sha256']==h(p/(case+'.comp'))
 asm=r['assembly'];assert asm==(o/(case+'.spvasm')).read_text()
 # Literal exact assembly interface identifiers observed in original source, independent of author's reader.
 for line in ['OpName %Params "Params"','OpMemberName %Params 0 "transform"','OpMemberDecorate %Params 0 '+major,'OpMemberDecorate %Params 0 MatrixStride 16','OpMemberDecorate %Params 0 Offset 0','%Params = OpTypeStruct %mat3v3float','%mat3v3float = OpTypeMatrix %v3float 3','%v3float = OpTypeVector %float 3','%float = OpTypeFloat 32']:
  assert line in asm,line
 assert ('ColMajor' if major=='RowMajor' else 'RowMajor') not in asm
 assert 'OpMatrixTimesVector' in asm and '; Version: 1.0' in asm
 data=bytes.fromhex((o/(case+'.host.hex')).read_text());assert data==struct.pack('<12f',*floats) and len(data)==48
 # Independently select explicit byte offsets rather than invoking author's decode/product.
 offsets=[[0,4,8],[16,20,24],[32,36,40]] if case=='row' else [[0,16,32],[4,20,36],[8,24,40]]
 matrix=[[struct.unpack_from('<f',data,n)[0] for n in row] for row in offsets]
 assert matrix==rows and [a+2*b+3*c for a,b,c in matrix]==[14,32,53]
 assert json.loads((o/(case+'.status.json')).read_text())['returncode']==0 and not (o/(case+'.stderr')).read_text()
 print(case,'raw assembly, native library, literal host bytes/product PASS')
data=bytes.fromhex((o/'row.host.hex').read_text())
wrong=[[struct.unpack_from('<f',data,n)[0] for n in row] for row in [[0,16,32],[4,20,36],[8,24,40]]]
assert [a+2*b+3*c for a,b,c in wrong]==[30,36,45]
print('wrong interpretation CPU-only product PASS')
