"""Finite frozen-assembly checks and synthetic mutations; no compiler invocation."""
import sys,json,struct
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('no optimized assertions')
R=Path(__file__).resolve().parent

def oracle(text,data,case):
 lines=[' '.join(s.split()) for s in text.splitlines() if s.strip() and not s.lstrip().startswith(';')]
 major='RowMajor' if case=='row' else 'ColMajor'
 exact=['OpName %Params "Params"','OpMemberName %Params 0 "transform"',
 'OpDecorate %Params Block','OpMemberDecorate %Params 0 '+major,
 'OpMemberDecorate %Params 0 MatrixStride 16','OpMemberDecorate %Params 0 Offset 0',
 '%float = OpTypeFloat 32','%v3float = OpTypeVector %float 3',
 '%mat3v3float = OpTypeMatrix %v3float 3','%Params = OpTypeStruct %mat3v3float',
 '%_ptr_Uniform_Params = OpTypePointer Uniform %Params',
 '%params = OpVariable %_ptr_Uniform_Params Uniform',
 '%int_0 = OpConstant %int 0',
 '%18 = OpAccessChain %_ptr_Uniform_mat3v3float %params %int_0',
 '%19 = OpLoad %mat3v3float %18',
 '%float_1 = OpConstant %float 1','%float_2 = OpConstant %float 2','%float_3 = OpConstant %float 3',
 '%23 = OpConstantComposite %v3float %float_1 %float_2 %float_3',
 '%24 = OpMatrixTimesVector %v3float %19 %23',
 'OpName %Output "Output"','OpMemberName %Output 0 "value"',
 '%Output = OpTypeStruct %v3float','%_ptr_Uniform_Output = OpTypePointer Uniform %Output',
 '%output_data = OpVariable %_ptr_Uniform_Output Uniform',
 '%26 = OpAccessChain %_ptr_Uniform_v3float %output_data %int_0',
 'OpStore %26 %24']
 for line in exact:
  if lines.count(line)!=1: raise ValueError('missing/duplicate frozen line: '+line)
 offsets=[[0,4,8],[16,20,24],[32,36,40]] if case=='row' else [[0,16,32],[4,20,36],[8,24,40]]
 if len(data)!=48: raise ValueError('host length')
 rows=[[struct.unpack_from('<f',data,k)[0] for k in row] for row in offsets]
 if rows!=[[1,2,3],[4,5,6],[7,8,10]]: raise ValueError('host logical elements')
 if [a+2*b+3*c for a,b,c in rows]!=[14,32,53]:raise ValueError('CPU product')

def replace_once(text,a,b):
 if text.count(a)!=1: raise ValueError('mutation precondition')
 return text.replace(a,b,1)

results=[]
for case in ['row','column']:
 text=(R/'fixture/results'/(case+'.spvasm')).read_text()
 data=bytes.fromhex((R/'fixture/results'/(case+'.host.hex')).read_text())
 oracle(text,data,case)
 major='RowMajor' if case=='row' else 'ColMajor'
 mutations={
 'wrong-major':(replace_once(text,'OpMemberDecorate %Params 0 '+major,'OpMemberDecorate %Params 0 '+('ColMajor' if case=='row' else 'RowMajor')),data),
 'wrong-stride':(replace_once(text,'OpMemberDecorate %Params 0 MatrixStride 16','OpMemberDecorate %Params 0 MatrixStride 32'),data),
 'wrong-block-name':(replace_once(text,'OpName %Params "Params"','OpName %Params "Other"'),data),
 'wrong-member-name':(replace_once(text,'OpMemberName %Params 0 "transform"','OpMemberName %Params 0 "other"'),data),
 'changed-host-element':(text,struct.pack('<f',2)+data[4:]),
 'disconnected-matrix-load':(replace_once(text,'%19 = OpLoad %mat3v3float %18','%19 = OpLoad %mat3v3float %99'),data),
 'wrong-output-store':(replace_once(text,'OpStore %26 %24','OpStore %26 %23'),data)}
 for name,(mt,md) in mutations.items():
  try: oracle(mt,md,case)
  except ValueError as e:results.append({'case':case,'mutation':name,'rejected':True,'reason':str(e)})
  else: raise RuntimeError('mutation survived: '+case+'/'+name)
report={'native_compiler_runs':0,'baseline_assemblies_checked':2,'synthetic_mutations_rejected':len(results),'results':results}
(R/'semantic-audit-output.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 2 archived assemblies, 14 synthetic rejects, zero native runs')
