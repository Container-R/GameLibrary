from pathlib import Path
import subprocess,json,hashlib,os,datetime,sys
research=Path(__file__).resolve().parent
sdk=Path(os.environ['DOTNET_ROOT']).resolve(); ink=Path(os.environ['INK_SOURCE']).resolve()
false='--old-score-false' in sys.argv
name='direct-roslyn-20261111T025948Z' if false else 'direct-roslyn-20261111T030108Z'
out=Path(os.environ['NATIVE_RESULTS_DIR']).resolve()/name
out.mkdir(parents=True,exist_ok=False)
import shutil
shutil.copytree(research/'fixtures',out/'inputs')
shutil.copy2(research/'native-results'/name/'Program.cs',out/'Program.cs')
assert subprocess.check_output(['git','-C',str(ink),'rev-parse','HEAD'],text=True).strip()=='35c63e52f1d36060930dc7ed3cfba38ea224b528'
assert not subprocess.check_output(['git','-C',str(ink),'status','--porcelain','--untracked-files=all'],text=True).strip()
refs=sorted((sdk/'packs/Microsoft.NETCore.App.Ref/8.0.34/ref/net8.0').glob('*.dll'))
files=sorted((ink/'compiler').rglob('*.cs'))+sorted((ink/'ink-engine-runtime').rglob('*.cs'))
(out/'source-sha256.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f)+'\n' for f in files))
(out/'reference-sha256.txt').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f)+'\n' for f in refs))
(out/'ink-commit.txt').write_text('35c63e52f1d36060930dc7ed3cfba38ea224b528\n')
(out/'runtime-assembly-attributes.cs').write_text('[assembly: System.Runtime.CompilerServices.InternalsVisibleTo("ink_compiler")]\n[assembly: System.Runtime.CompilerServices.InternalsVisibleTo("inklecate")]\n[assembly: System.Runtime.CompilerServices.InternalsVisibleTo("ink-tests")]\n')
(out/'global-usings.cs').write_text('global using System;\nglobal using System.Collections.Generic;\nglobal using System.IO;\nglobal using System.Linq;\nglobal using System.Net.Http;\nglobal using System.Threading;\nglobal using System.Threading.Tasks;\n')
base=[str(sdk/'dotnet'),str(sdk/'sdk/8.0.428/Roslyn/bincore/csc.dll')]
common=['-nologo','-noconfig','-nostdlib+','-optimize+','-langversion:latest']+['-r:'+str(f) for f in refs]
steps=[('runtime',['-target:library','-out:'+str(out/'ink-engine-runtime.dll'),'-define:NETSTANDARD;NETSTANDARD2_0']+[str(f) for f in sorted((ink/'ink-engine-runtime').rglob('*.cs'))]+[str(out/'runtime-assembly-attributes.cs')]),('compiler',['-target:library','-out:'+str(out/'ink_compiler.dll'),'-define:NETSTANDARD;NETSTANDARD2_0','-r:'+str(out/'ink-engine-runtime.dll')]+[str(f) for f in sorted((ink/'compiler').rglob('*.cs'))]),('harness',['-target:exe','-out:'+str(out/'NativeHarness.dll'),'-r:'+str(out/'ink-engine-runtime.dll'),'-r:'+str(out/'ink_compiler.dll'),str(out/'global-usings.cs'),str(out/'Program.cs')])]
(out/'method.txt').write_text('Independent direct Roslyn build. Original csproj build FAILED at NuGet first use. Fixed upstream C# bytes unchanged; compile runtime/compiler against .NET 8.0.34 reference assemblies instead of original netstandard target reference pack. Define NETSTANDARD and NETSTANDARD2_0 as original selected target. Preserve assembly names and runtime friend attributes. This does not validate original csproj, NuGet restore, or netstandard portability.\n')
for name,args in steps:
    cmd=base+common+args;(out/(name+'-command.json')).write_text(json.dumps(cmd,indent=2))
    with (out/(name+'-build.log')).open('w') as log: p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
    (out/(name+'-exit.txt')).write_text(str(p.returncode)+'\n');print(name,p.returncode,flush=True)
    if p.returncode: print((out/(name+'-build.log')).read_text());raise SystemExit(p.returncode)
(out/'NativeHarness.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':'net8.0','framework':{'name':'Microsoft.NETCore.App','version':'8.0.34'}}},indent=2))
cmd=[str(sdk/'dotnet'),str(out/'NativeHarness.dll'),str(research/'fixtures'),str(out/'artifacts')]+(['--old-score-false'] if '--old-score-false' in sys.argv else []);(out/'run-command.json').write_text(json.dumps(cmd,indent=2))
with (out/'trace.jsonl').open('w') as log,(out/'stderr.txt').open('w') as err:p=subprocess.run(cmd,stdout=log,stderr=err)
(out/'exit-code.txt').write_text(str(p.returncode)+'\n');print('native run',p.returncode,'out',out,flush=True)
raise SystemExit(p.returncode)
