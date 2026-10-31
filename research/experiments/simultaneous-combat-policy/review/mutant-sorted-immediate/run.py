"""Read-only runner: output JSON to stdout; never overwrites an archived summary.
No assert or optimization-dependent control flow. No network or subprocesses.
"""
import copy
import hashlib
import itertools
import json
import platform
from pathlib import Path
import sys

from model import immediate, simultaneous

ROOT = Path(__file__).resolve().parent
CONTRACT_SHA = '509e8144472248bfd6d69dbe2dc320d8f24d805382e8ae9b3404cf790b74b5df'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    raw = (ROOT / 'contract.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == CONTRACT_SHA, 'pre-frozen contract changed')
    contract = json.loads(raw)
    commands = [tuple(c) for c in contract['commands']]
    tick = contract['tick']
    traces = []
    disagreements = []
    next_tick_checks = 0
    for case in contract['cases']:
        expected = {'hp': case['expected_hp'], 'events': case['expected_events']}
        for actors in itertools.permutations(contract['actors']):
            for ordered_commands in itertools.permutations(commands):
                hp = {a: case['initial_hp'][a] for a in actors}
                original = copy.deepcopy(hp)
                result = simultaneous(hp, ordered_commands, tick)
                require(result == expected, f'simultaneous oracle mismatch: {case["name"]}')
                naive = immediate(hp, ordered_commands, tick)
                canonical = immediate(hp, ordered_commands, tick, canonical_sort=True)
                require(hp == original, 'caller state mutated')
                if case['name'] == 'both-alive':
                    attacker, action, target = ordered_commands[0]
                    naive_expected = {'hp': {attacker: 1, target: 0},
                                      'events': [[tick, 'damage', attacker, action, target], [tick, 'death', target]]}
                    sorted_expected = {'hp': {'A': 1, 'B': 0},
                                       'events': [[tick, 'damage', 'A', 'hit-A', 'B'], [tick, 'death', 'B']]}
                    require(naive == naive_expected, 'immediate counterexample not as predicted')
                    require(canonical == sorted_expected, 'stable counterexample not as predicted')
                    require(naive != expected and canonical != expected, 'negative control unexpectedly satisfies policy')
                    disagreements.append({'actors': actors, 'commands': ordered_commands})
                    follow = simultaneous(result['hp'], ordered_commands, tick + 1)
                    require(follow == {'hp': {'A': 0, 'B': 0}, 'events': []}, 'dead actors act on next tick')
                    next_tick_checks += 1
                else:
                    require(naive == expected and canonical == expected, 'initially-dead boundary changed')
                traces.append({'case': case['name'], 'actor_insertion_order': actors,
                               'command_order': ordered_commands, 'simultaneous': result,
                               'immediate': naive, 'canonical_immediate': canonical})
    require(len(traces) == 12 and len(disagreements) == 4 and next_tick_checks == 4, 'enumeration count changed')
    output = {'status': 'PASS', 'scope': 'finite original policy, not universal combat semantics',
              'python': platform.python_version(), 'platform': platform.platform(),
              'optimization': sys.flags.optimize, 'contract_sha256': CONTRACT_SHA,
              'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                for name in ('model.py', 'run.py')},
              'enumerated_inputs': len(traces), 'simultaneous_oracle_matches': len(traces),
              'each_immediate_policy_disagrees_with_simultaneous_on': len(disagreements),
              'initially_dead_inputs': 8, 'next_tick_checks': next_tick_checks, 'traces': traces}
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
