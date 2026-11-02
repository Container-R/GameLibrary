"""Post-hoc reserved-handle check for frozen eight-line EnTT v2/v3 observations.
Not an original execution input, native test, or arbitrary EnTT validity oracle.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKER_SHA = '788f72e5e978b90a14047822cd28d023e49c7495d75119cc856525a8cc78d732'
ORACLE_SHA = '90169423b365a0a3a553462caff0be05ebb6672de6f58758959b9a5c139497cf'

class SupplementError(ValueError):
    pass

def need(ok, message):
    if not ok:
        raise SupplementError(message)

def bound_files():
    checker = ROOT / 'frozen_checker.py'
    oracle = ROOT / 'frozen_oracle.json'
    for path, sha in [(checker,CHECKER_SHA),(oracle,ORACLE_SHA)]:
        need(hashlib.sha256(path.read_bytes()).hexdigest()==sha,'frozen_dependency_changed')
    return checker,oracle

def check(raw):
    checker,oracle = bound_files()
    spec = importlib.util.spec_from_file_location('bound_entt_eight_line_checker',checker)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = module.check(raw,oracle)
    stages = records[4:]
    # These values originated as ordinary created entities, even when now stale.
    for i,row in enumerate(stages):
        fields = ['source','seed']
        if i > 0:
            fields += ['mapped_now','mapped_initial']
        for field in fields:
            handle = row[field]  # Original consumer already checked schema and split.
            need(handle['index'] != 0xfffff,'reserved_null_index:'+row['stage']+':'+field)
            need(handle['version'] != 0xfff,'reserved_tombstone_version:'+row['stage']+':'+field)
    # Preserve the protocol's actual null sentinel and missing initial observation.
    need(stages[0]['mapped_now']=={'full':0xffffffff,'index':0xfffff,'version':0xfff},'prepared_null')
    need(stages[0]['mapped_initial'] is None,'prepared_unobserved')
    return records

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('observations',nargs='+',type=Path)
    args=parser.parse_args()
    results=[]
    try:
        for path in args.observations:
            raw=path.read_bytes()
            check(raw)
            results.append({'sha256':hashlib.sha256(raw).hexdigest(),'supplementary_content_check':'PASS'})
    except (OSError,ValueError,TypeError,KeyError) as exc:
        # No input path or raw exception text in public-facing output.
        print(json.dumps({'status':'REJECTED','error_type':type(exc).__name__,'native_invocations':0}))
        return 1
    print(json.dumps({'status':'PASS','kind':'posthoc_supplement_not_execution_receipt',
                      'records':results,'native_invocations':0}))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
