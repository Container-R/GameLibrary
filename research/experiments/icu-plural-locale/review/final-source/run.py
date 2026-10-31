"""Serial bounded native batch; execution requires explicit coordinator approval."""
import datetime,json,os,platform,signal,subprocess,sys,tempfile,time,uuid
from pathlib import Path
from consume import PROTOCOL_SHA,NAMES,consume,digest,strict,require,no_symlink,local
from isolation import prepare_environment,validate_environment
ROOT=Path(__file__).resolve().parent

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,obj):p.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def source_hashes():return {n:digest(local(ROOT,n)) for n in sorted(NAMES)}
def group_exists(pid):
    try:os.killpg(pid,0);return True
    except ProcessLookupError:return False
def stop(proc,r):
    for sig in (signal.SIGTERM,signal.SIGKILL):
        if not group_exists(proc.pid):break
        entry={'signal':sig.name}
        try:os.killpg(proc.pid,sig);entry['sent']=True
        except ProcessLookupError:entry['sent']=False
        r['termination_attempts'].append(entry)
        try:proc.wait(timeout=2)
        except subprocess.TimeoutExpired:pass
    r['group_remaining']=group_exists(proc.pid)

def run_one(batch,config,manifest,protocol):
    invocation=str(uuid.uuid4());out=batch/invocation;out.mkdir()
    r={'uuid':invocation,'config':config,'state':'STARTED','started_utc':now(),'parent_pid':os.getpid(),
       'python':sys.executable,'python_version':sys.version,'platform':platform.platform(),'source_root':str(ROOT),
       'source_sha256':manifest,'timeout':False,'termination_attempts':[],'returncode':None}
    save(out/'receipt.json',r)
    for name in ('stdout.txt','stderr.txt'):(out/name).touch(exist_ok=False)
    start=time.monotonic();proc=None;phase='source'
    try:
        require(source_hashes()==manifest,'source drift before config')
        phase='environment'
        with tempfile.TemporaryDirectory(dir=out,prefix='runtime-') as tmp:
            base=protocol['environment']['base_exact'];env,mapping=prepare_environment(base,tmp);validate_environment(env,tmp)
            r.update(base_environment=base,isolation=mapping,owned_runtime_root=tmp)
            cmd=[sys.executable,str(ROOT/'child.py'),config,invocation];r['argv']=cmd
            phase='spawn'
            with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
                proc=subprocess.Popen(cmd,stdout=stdout,stderr=stderr,env=env,cwd=tmp,start_new_session=True)
                r['child_pid']=proc.pid;save(out/'receipt.json',r);phase='wait'
                try:proc.wait(timeout=20)
                except subprocess.TimeoutExpired:r['timeout']=True;stop(proc,r)
                r['returncode']=proc.poll()
                if not r['timeout']:
                    r['group_remaining']=group_exists(proc.pid)
                    if r['group_remaining']:r['unexpected_descendants']=True;stop(proc,r)
            r['category']='TIMEOUT' if r['timeout'] else 'CHILD_CRASH'
            if r.get('unexpected_descendants'):r['category']='MALFORMED_OR_INCOMPLETE_EVIDENCE'
            elif r['returncode']==0 and not r['timeout']:
                try:r['category']=strict((out/'stdout.txt').read_text().splitlines()[-1])['value']['category']
                except (ValueError,KeyError,IndexError):r['category']='MALFORMED_OR_INCOMPLETE_EVIDENCE'
    except Exception as exc:
        import traceback
        r.update(category='SOURCE_OR_LIBRARY_IDENTITY_FAILURE' if phase=='source' else 'ENVIRONMENT_OR_BINDING_FAILURE',exception_phase=phase,error=str(exc),traceback=traceback.format_exc())
        if proc is not None:stop(proc,r);r['returncode']=proc.poll()
    finally:
        r.update(state='COMPLETE',finished_utc=now(),elapsed_seconds=time.monotonic()-start)
        r['output_sha256']={n:digest(out/n) for n in ('stdout.txt','stderr.txt')}
        try:r['source_after_sha256']=source_hashes()
        except Exception as exc:r['source_after_error']=str(exc)
        if r.get('source_after_sha256')!=manifest:r.update(prior_category=r.get('category'),category='SOURCE_OR_LIBRARY_IDENTITY_FAILURE')
        save(out/'receipt.json',r)
    accepted=False
    if r['category']=='COMPLETE_EXPECTED_OUTPUTS' and 'error' not in r:
        try:
            checked=consume(out,ROOT,invocation,config);accepted=True
            save(out/'consistency.json',{'archive_consistent':True,'result':checked,'not_execution_authentication':True})
        except Exception as exc:
            r.update(prior_category=r['category'],category='MALFORMED_OR_INCOMPLETE_EVIDENCE',consumer_error=str(exc));save(out/'receipt.json',r)
    return {'config':config,'uuid':invocation,'category':r['category'],'accepted':accepted,'receipt_sha256':digest(out/'receipt.json')}

def main(output_parent):
    parent=Path(output_parent);no_symlink(parent);parent=parent.resolve(strict=True)
    batch_id=str(uuid.uuid4());batch=parent/batch_id;batch.mkdir()
    b={'uuid':batch_id,'state':'STARTED','started_utc':now(),'configs':[],'not_started':['en_full','ar_full','ar_omit_few'],'native_child_spawn_count':0}
    save(batch/'batch.json',b)
    in_flight=False
    try:
        require(not sys.flags.optimize,'optimized parent rejected before spawn')
        require(platform.system()=='Linux','Linux wrapper only')
        protocol=strict(local(ROOT,'protocol.json').read_text());require(digest(ROOT/'protocol.json')==PROTOCOL_SHA,'protocol pin')
        require(digest(local(ROOT,'isolation.py'))==protocol['environment']['helper_sha256'],'helper pin')
        manifest=strict(local(ROOT,'source-manifest.json').read_text());require(set(manifest)==NAMES and source_hashes()==manifest,'manifest pins')
        b['source_sha256']=manifest
        for config in protocol['parent']['order']:
            b['not_started'].remove(config);save(batch/'batch.json',b)
            in_flight=True
            row=run_one(batch,config,manifest,protocol)
            in_flight=False
            b['configs'].append(row)
            receipt=strict((batch/row['uuid']/'receipt.json').read_text())
            if 'child_pid' in receipt:b['native_child_spawn_count']+=1
            save(batch/'batch.json',b)
            if not row['accepted']:break
        b['state']='COMPLETE_EXPECTED_OUTPUTS' if len(b['configs'])==3 and all(x['accepted'] for x in b['configs']) else 'FAILED_OR_INCOMPLETE'
    except Exception as exc:
        import traceback
        b.update(state='FAILED_OR_INCOMPLETE',error=str(exc),traceback=traceback.format_exc())
    finally:
        observed=0; readable=True
        for p in batch.glob('*/receipt.json'):
            try:
                r=strict(p.read_text())
                if type(r.get('child_pid')) is int and r['child_pid']>0:observed+=1
            except Exception:readable=False
        b['observed_child_receipts']=observed
        b['spawn_count_complete']=not in_flight and readable
        b['native_child_spawn_count']=observed if b['spawn_count_complete'] else None
        b['finished_utc']=now();save(batch/'batch.json',b)
    print(json.dumps({'output':str(batch),'state':b['state'],'native_child_spawn_count':b['native_child_spawn_count']}))
    return 0 if b['state']=='COMPLETE_EXPECTED_OUTPUTS' else 1

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output-parent',required=True);a=p.parse_args();raise SystemExit(main(a.output_parent))
