import pathlib,importlib.util,json,sys
root=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('frozen_runner',root/'fixture/run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=pathlib.Path(json.loads((root/'run.stdout').read_text())['output']);raw=(out/'direct-shape.stderr').read_text();primary=raw.splitlines()[0]
mutations={'duplicate_primary':raw+primary+'\n','missing_primary':'\n'.join(raw.splitlines()[1:])+'\n','extra_ERROR':raw+'ERROR: unrelated\n','extra_SCRIPT_ERROR':raw+'SCRIPT ERROR: unrelated\n','unknown_context':raw+'   at: unrelated (other.cpp:1)\n'}
results=[]
m.errors(raw,'direct-shape');m.errors('','deferred-shape')
for name,text in mutations.items():
 try:m.errors(text,'direct-shape')
 except ValueError:results.append({'mutation':name,'rejected':True})
 else:raise RuntimeError('accepted '+name)
# Exercise exactly the original runner's stdout extraction and semantic check.
stdout=(out/'direct-shape.stdout').read_text()+'SCRIPT ERROR: synthetic unrelated diagnostic\n'
rows=[l[12:] for l in stdout.splitlines() if l.startswith('RESULT_JSON=')]
if len(rows)!=1:raise RuntimeError('unexpected extraction')
m.errors(raw,'direct-shape');m.check(json.loads(rows[0]),'direct-shape')
report={'real_stderr_baselines_accepted':2,'stderr_mutations':results,'stdout_extra_error_reaches_existing_acceptance':True,'scope':'Pure Python archived-record probes; zero engine/version/process launches; stdout gap found, not a runtime failure'}
(root/'parser-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
