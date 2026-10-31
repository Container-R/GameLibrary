"""Run only after code review approval; always use a fresh external source copy."""
import sys, os, json, uuid, subprocess, gzip, base64
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT/'summary.json'
SUMMARY.unlink(missing_ok=True)
if sys.flags.optimize:
    raise SystemExit('optimized runner rejected before tool entry')
from common import N, IDENTITY, SOURCES, sha, files, identities, input_bytes, commands
from reader import read, need
from isolation import prepare_environment, validate_environment

def main():
    out = ROOT/'evidence'/str(uuid.uuid4()); out.mkdir(parents=True,exist_ok=False)
    receipt = {'status':'RUNNING','uuid':out.name,'processes':[],'source_sha256':files(ROOT),
               'identity_before':{},'artifacts':{},'archives':{},'original_process_directory':str(out)}
    def save(): (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    save()
    try:
        receipt['identity_before'] = identities(); save()
        need(receipt['identity_before'] == IDENTITY,'tool identity mismatch')
        need(receipt['source_sha256']['isolation.py'] == 'bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970','helper identity')
        envroot = out/'environment'; envroot.mkdir()
        env, selected = prepare_environment(os.environ,envroot)
        receipt['selected_environment'] = selected; save()
        (out/'input.pcm').write_bytes(input_bytes())
        for name, argv in commands(out).items():
            validate_environment(env,envroot)
            process = {'name':name,'argv':argv,'timeout_seconds':20,'status':'ATTEMPTED'}
            receipt['processes'].append(process); save()
            stdout = stderr = b''
            try:
                result = subprocess.run(argv,env=env,cwd=out,capture_output=True,timeout=20,check=False)
                stdout,stderr = result.stdout,result.stderr
                process.update(status='RETURNED',returncode=result.returncode)
            except subprocess.TimeoutExpired as e:
                stdout = e.stdout or b''; stderr = e.stderr or b''
                process.update(status='TIMEOUT',error=repr(e))
                raise
            except OSError as e:
                process.update(status='LAUNCH_ERROR',error=repr(e)); raise
            finally:
                for stream, data in (('stdout',stdout),('stderr',stderr)):
                    if isinstance(data,str): data = data.encode()
                    (out/f'{name}.{stream}').write_bytes(data)
                    process[stream+'_sha256'] = sha(data)
                save()
            need(result.returncode == 0,'nonzero '+name)
            need(stderr == b'','unexpected stderr '+name)
            if name == 'version':
                need(stdout.startswith(b'ffmpeg version 7.1.5-0+deb13u1 '),'version self report')
            else:
                need(stdout == b'','unexpected stdout '+name)
        parsed = read((out/'encoded.opus').read_bytes())
        decoded = (out/'decoded.pcm').read_bytes()
        need(len(decoded) == N*4 and parsed['presented_frames'] == N,'presented count')
        need(parsed['final_granule']-N == parsed['header']['preskip'],'granule overcount')
        need(parsed['coded_frames']-parsed['header']['preskip']-N == parsed['tail_trim'],'packet overcount')
        (out/'parsed.json').write_text(json.dumps(parsed,indent=2)+'\n')
        for name in ('input.pcm','encoded.opus','decoded.pcm','parsed.json'):
            data = (out/name).read_bytes()
            receipt['artifacts'][name] = {'bytes':len(data),'sha256':sha(data)}
            if name.endswith('.json'): continue
            encoded = base64.b64encode(gzip.compress(data,mtime=0))
            chunks = []
            for i,start in enumerate(range(0,len(encoded),65536)):
                chunk = encoded[start:start+65536]; path=f'{name}.gz.b64.{i:03d}'
                (out/path).write_bytes(chunk)
                chunks.append({'path':path,'bytes':len(chunk),'sha256':sha(chunk)})
            receipt['archives'][name] = chunks
        receipt['identity_after'] = identities()
        need(receipt['identity_after'] == receipt['identity_before'],'identity changed')
        need(files(ROOT) == receipt['source_sha256'],'source changed')
        receipt.update(status='PASS',native_media_processes=2,version_processes=1)
        save()
        # This consumer reparses bytes; it does not authenticate process execution.
        from consumer import verify
        verify(ROOT,out)
        SUMMARY.write_text(json.dumps({'status':'PASS','evidence':str(out.relative_to(ROOT)),
                                      'receipt_sha256':sha((out/'receipt.json').read_bytes())},indent=2)+'\n')
        print(json.dumps({'status':'PASS','uuid':out.name,'presented_frames':N,
                          'granule':parsed['final_granule'],'coded_frames':parsed['coded_frames']}))
    except BaseException as e:
        receipt.update(status='FAIL',error=repr(e)); save(); raise
if __name__ == '__main__': main()
