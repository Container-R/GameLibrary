"""Run only after code review approval; always use a fresh external source copy."""
import sys, os, json, uuid, subprocess, gzip, base64, struct, signal
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SUMMARY = ROOT/'summary.json'
SUMMARY.unlink(missing_ok=True)
if sys.flags.optimize:
    raise SystemExit('optimized runner rejected before tool entry')
from common import N, IDENTITY, SOURCES, sha, files, identities, input_bytes, commands
from reader import read, need
from isolation import prepare_environment, validate_environment

def utc(): return datetime.now(timezone.utc).isoformat()

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
        base_env = {'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
        receipt['base_environment'] = base_env
        env, selected = prepare_environment(base_env,envroot)
        receipt['selected_environment'] = selected; save()
        (out/'input.pcm').write_bytes(input_bytes())
        original = (out/'input.pcm').read_bytes()
        need(len(original) == 374636, 'original byte count before tools')
        for i, (left, right) in enumerate(struct.iter_unpack('<hh', original)):
            need((left, right) == (128*(i%96-48), 96*(i%80-40)), 'original formula before tools')
        for name, argv in commands(out).items():
            validate_environment(env,envroot)
            process = {'name':name,'argv':argv,'timeout_seconds':20,'status':'ATTEMPTED','attempted_utc':utc()}
            receipt['processes'].append(process); save()
            stdout = stderr = b''
            try:
                child = subprocess.Popen(argv,env=env,cwd=out,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
                process['pid'] = child.pid; save()
                stdout,stderr = child.communicate(timeout=20)
                process.update(status='RETURNED',returncode=child.returncode,returned_utc=utc())
            except subprocess.TimeoutExpired as e:
                stdout = e.stdout or b''; stderr = e.stderr or b''
                process.update(status='TIMEOUT',error=repr(e),returned_utc=utc())
                try:
                    os.killpg(child.pid,signal.SIGKILL)
                    process['cleanup_signal'] = 'SIGKILL own process group'
                except ProcessLookupError:
                    process['cleanup_signal'] = 'process group already absent'
                except OSError as cleanup_error:
                    process['cleanup_error'] = repr(cleanup_error)
                try:
                    stdout,stderr = child.communicate(timeout=5)
                    process['cleanup_returncode'] = child.returncode
                except (subprocess.TimeoutExpired,OSError) as cleanup_error:
                    process['cleanup_wait_error'] = repr(cleanup_error)
                raise
            except OSError as e:
                process.update(status='LAUNCH_ERROR',error=repr(e),returned_utc=utc()); raise
            finally:
                for stream, data in (('stdout',stdout),('stderr',stderr)):
                    if isinstance(data,str): data = data.encode()
                    (out/f'{name}.{stream}').write_bytes(data)
                    process[stream+'_sha256'] = sha(data)
                save()
            need(child.returncode == 0,'nonzero '+name)
            need(stderr == b'','unexpected stderr '+name)
            if name == 'version':
                need(stdout.startswith(b'ffmpeg version 7.1.5-0+deb13u1 '),'version self report')
            else:
                need(stdout == b'','unexpected stdout '+name)
            if name == 'encode':
                encoded_bytes = (out/'encoded.opus').read_bytes()
                receipt['encoded_before_parse'] = {'bytes':len(encoded_bytes),'sha256':sha(encoded_bytes)}; save()
                parsed = read(encoded_bytes)
                need(parsed['presented_frames'] == N,'container count before decode')
                (out/'parsed.json').write_text(json.dumps(parsed,indent=2)+'\n')
                receipt['encoded_subset_gate'] = 'PASS'; save()
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
        receipt['source_after'] = files(ROOT)
        need(receipt['source_after'] == receipt['source_sha256'],'source changed')
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
