"""Explicit relocated historical registry verification; never execute archive code.

Does not edit historical registry, document fields, or digest declarations.
A retired check is NOT a pass. This adapter alone does not sanitize archives.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
from verify import IntegrityError, strict_json, verify


def relative(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or any(ord(c)<32 for c in value):
        raise IntegrityError('invalid relative mapping path')
    if PurePosixPath(value).is_absolute() or any(p in ('', '.', '..') for p in value.split('/')):
        raise IntegrityError('unnormalized relative mapping path')
    return value


def adapt(registry, policy):
    if not isinstance(policy, dict) or type(policy.get('version')) is not int or policy['version'] != 1:
        raise IntegrityError('relocation policy version required')
    count=policy.get('expected_checks')
    if type(count) is not int or count <= 0:
        raise IntegrityError('positive expected_checks required')
    checks=registry.get('checks') if isinstance(registry,dict) else None
    if not isinstance(checks,list) or len(checks)!=count:
        raise IntegrityError('registry count mismatch')
    ids=[c.get('id') for c in checks if isinstance(c,dict)]
    if len(ids)!=count or any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=count:
        raise IntegrityError('unique nonempty check IDs required')
    mappings=policy.get('prefixes')
    if not isinstance(mappings,dict) or not mappings:
        raise IntegrityError('explicit nonempty prefix mapping required')
    for a,b in mappings.items():relative(a);relative(b)
    keys=list(mappings)
    if any(a!=b and (a.startswith(b+'/') or b.startswith(a+'/')) for a in keys for b in keys):
        raise IntegrityError('overlapping source prefixes')
    values=list(mappings.values())
    if len(set(values))!=len(values) or any(a!=b and a.startswith(b+'/') for a in values for b in values):
        raise IntegrityError('overlapping destination prefixes')
    retired=policy.get('retired_checks',{})
    if not isinstance(retired,dict) or not set(retired)<=set(ids) or any(not isinstance(v,str) or not v.strip() for v in retired.values()):
        raise IntegrityError('retired checks need known IDs and reasons')
    def remap(path):
        relative(path)
        for a,b in mappings.items():
            if path==a or path.startswith(a+'/'):return b+path[len(a):]
        return path # Explicitly unmoved repository inputs retain their relative location.
    active=[]
    for item in checks:
        if item['id'] in retired:continue
        c=copy.deepcopy(item)
        for key in ('document','target','left','right','log','parsed'):
            if key in c:c[key]=remap(c[key])
        if 'files' in c:
            if not isinstance(c['files'],dict):raise IntegrityError('invalid manifest files')
            c['files']={k:remap(v) for k,v in c['files'].items()}
        active.append(c)
    return {'checks':active},retired


def run(root, registry_bytes, policy):
    expected=policy.get('registry_sha256')
    if not isinstance(expected,str) or hashlib.sha256(registry_bytes).hexdigest()!=expected:
        raise IntegrityError('historical registry bytes differ from declared identity')
    adapted,retired=adapt(strict_json(registry_bytes.decode('utf-8')),policy)
    report=verify(root,adapted) if adapted['checks'] else {'checks':[],'passed':0,'failed':0}
    report.update(scope='Relocated declared bytes only; no execution, authenticity, sanitization or semantic certification',
                  retired=[{'id':k,'reason':v,'status':'not_revalidated'} for k,v in retired.items()],
                  original_check_count=policy['expected_checks'])
    report['complete']=not retired and report['failed']==0
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--registry',required=True,type=Path)
    parser.add_argument('--policy',required=True,type=Path)
    args=parser.parse_args()
    try:
        report=run(args.root.resolve(),args.registry.read_bytes(),strict_json(args.policy.read_text()))
    except (ValueError,KeyError,TypeError,OSError):
        print(json.dumps({'status':'configuration_error','complete':False}))
        return 1 # Do not echo potentially sensitive source field values or paths.
    # Existing verifier details can contain input values: omit details from public stdout.
    report['checks']=[{'id':c['id'],'status':c['status']} for c in report['checks']]
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if report['failed'] else (2 if report['retired'] else 0)

if __name__=='__main__':raise SystemExit(main())
