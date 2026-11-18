"""Original static directed graph teaching fixture; no engine dependencies."""
from collections import deque
import json


def route(graph, start, end, blocked=None):
    if start == blocked or end == blocked:
        return None
    parents = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == end:
            result = []
            while node is not None:
                result.append(node)
                node = parents[node]
            return result[::-1]
        for other in graph[node]:
            if other != blocked and other not in parents:
                parents[other] = node
                queue.append(other)
    return None


def check(graph, start, end, required):
    # Fail configuration separately; never label it a topology success.
    if len({start, end, required}) != 3:
        raise ValueError('S, E, R must be distinct')
    if any(n not in graph for n in (start, end, required)):
        raise ValueError('missing endpoint or required node')
    if any(v not in graph for values in graph.values() for v in values):
        raise ValueError('edge endpoint absent from graph')
    original = route(graph, start, end)
    if original is None:
        return dict(status='unreachable', original=None, bypass=None)
    bypass = route(graph, start, end, required)
    return dict(status='bypass' if bypass else 'mandatory', original=original, bypass=bypass)


base = {'S': ['A'], 'A': ['R', 'T'], 'T': ['A'], 'R': ['E'], 'E': []}
bypass = {**base, 'A': ['R', 'T', 'E']}
unreachable = {**base, 'R': []}
# Only E->A is added; treating the directed graph as undirected is wrong.
reverse = {**base, 'E': ['A']}
# R is reachable but is not on any successful route.
dead_supply = {**bypass, 'R': []}
results = {}
for name, graph, expected in [
    ('base', base, 'mandatory'), ('bypass', bypass, 'bypass'),
    ('unreachable', unreachable, 'unreachable'),
    ('reverse_edge', reverse, 'mandatory'),
    ('dead_end_supply', dead_supply, 'bypass')]:
    answer = check(graph, 'S', 'E', 'R')
    assert answer['status'] == expected, (name, answer)
    for label in ('original', 'bypass'):
        path = answer[label]
        if path:
            assert path[0] == 'S' and path[-1] == 'E'
            assert all(v in graph[u] for u, v in zip(path, path[1:]))
            if label == 'bypass':
                assert 'R' not in path
    results[name] = {'graph': graph, **answer}
# Distinct semantic predicate, deliberately not inferred from topology.
results['wrong_room'] = {'topology': check(base, 'S', 'E', 'R')['status'],
                         'required_role': 'supply', 'actual_role': 'combat',
                         'role_accepted': 'supply' == 'combat'}
assert results['wrong_room']['role_accepted'] is False
print(json.dumps(results, ensure_ascii=False, indent=2))
