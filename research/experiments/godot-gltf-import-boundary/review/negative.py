import pathlib,sys,shutil,subprocess,os,json
if sys.flags.optimize:raise SystemExit('negative harness requires normal mode')
r=pathlib.Path(__file__).resolve().parent; records=[]
for case in ['optimized','missing-binary','malformed-result']:
 d=r/'negative'/case;d.mkdir(parents=True,exist_ok=True)
 for name in ['run.py','main.gd','project.godot','contract.json','mesh.gltf']:shutil.copyfile(r/'fixture'/name,d/name)
 (d/'results').mkdir(exist_ok=True);(d/'results/summary.json').write_text('{"status":"PASS","seeded_old":true}')
 marker=d/'fake-called';marker.unlink(missing_ok=True)
 fake=d/'fake-engine';fake.write_text('#!/bin/sh\ntouch "'+str(marker)+'"\nprintf "RESULT_JSON={broken}\\n"\n');fake.chmod(0o700)
 env=dict(os.environ,GODOT_BINARY=str(d/'absent') if case=='missing-binary' else str(fake))
 cmd=[sys.executable]+(['-O'] if case=='optimized' else [])+[str(d/'run.py')]
 p=subprocess.run(cmd,capture_output=True,env=env,timeout=10)
 (d/'stdout').write_bytes(p.stdout);(d/'stderr').write_bytes(p.stderr)
 result={'case':case,'command':cmd,'exit':p.returncode,'old_summary_absent':not (d/'results/summary.json').exists(),'fake_called':marker.exists(),'actual_Godot_imports':0}
 if not (p.returncode!=0 and result['old_summary_absent'] and result['fake_called']==(case=='malformed-result')):raise RuntimeError(result)
 records.append(result)
(r/'negative-results.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records,indent=2))
