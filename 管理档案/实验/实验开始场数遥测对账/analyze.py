"""Observable-only reconciliation. No fixture generator or oracle imports."""
import json
from pathlib import Path
import sys


def analyze(d):
    c = d['contract']
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    require(c['target_start'] in ('server_accept', 'client_click'), 'unknown target mode')
    require(type(c['authority_complete']) is bool, 'invalid completeness contract')
    require(d['query']['mode'] in ('all_assigned', 'post_treatment_prompt_seen'), 'unknown query mode')
    lo, hi = c['start_window']
    require(0 <= lo < hi <= c['snapshot'], 'invalid window or immature snapshot')
    roster = {r['player']: r['arm'] for r in d['assignment']}
    require(len(roster) == len(d['assignment']), 'duplicate member')
    require(all(r['arm'] in ('C','T') and r['assigned_at'] == 0 for r in d['assignment']), 'invalid assignment')
    require(set(d['query']['qualifying_players']) <= set(roster), 'unknown qualifying member')
    anchors = {r['id']: r for r in d['accepted']}
    require(len(anchors) == len(d['accepted']), 'duplicate authority id')
    require(all(r['player'] in roster and lo <= r['start_at'] < hi and r['start_at'] <= c['snapshot'] for r in anchors.values()), 'invalid authority identity/time')
    raw = d['received']
    payloads, sequences = {}, {}
    for r in raw:
        require(lo <= r['start_at'] < hi and r['start_at'] <= r['received_at'] <= c['snapshot'], 'invalid receipt time')
        require(type(r['seq']) is int and r['seq'] > 0 and bool(r['epoch']), 'invalid sequence')
        payload = tuple(r[k] for k in ('player','arm','start_at','epoch','seq'))
        require(r['id'] not in payloads or payloads[r['id']] == payload, 'conflicting duplicate')
        payloads[r['id']] = payload
        key = (r['player'],r['epoch'],r['seq'])
        require(key not in sequences or sequences[key] == r['id'], 'sequence collision')
        sequences[key] = r['id']
    parsed, rejects, duplicates = {}, [], []
    for r in sorted(raw, key=lambda r: (r['received_at'], r['id'])):
        reason = None
        if r['player'] not in roster:
            reason = 'unknown_player'
        elif r['arm'] != roster[r['player']]:
            reason = 'assignment_label_conflict'
        elif r['id'] not in anchors:
            reason = 'no_authority_match'
        elif any(r[k] != anchors[r['id']][k] for k in ('player', 'start_at')):
            reason = 'authority_payload_conflict'
        if reason:
            rejects.append({'id': r['id'], 'reason': reason})
        elif r['id'] in parsed:
            if any(r[k] != parsed[r['id']][k] for k in ('player', 'arm', 'start_at', 'epoch', 'seq')):
                raise ValueError('conflicting duplicate')
            duplicates.append(r['id'])
        else:
            parsed[r['id']] = r
    eligible = {p for p in roster if d['query']['mode'] == 'all_assigned' or p in d['query']['qualifying_players']}
    final = {k: r for k, r in parsed.items() if r['player'] in eligible}
    raw_ids = {r['id'] for r in raw}
    seqs = {}
    for r in parsed.values():
        seqs.setdefault((r['player'], r['epoch']), set()).add(r['seq'])
    gaps = {p + '/' + ep: sorted(set(range(min(s), max(s)+1)) - s) for (p,ep), s in seqs.items()}
    players = []
    for p, arm in roster.items():
        accepted_n = sum(r['player'] == p for r in anchors.values())
        known = c['target_start'] == 'server_accept' and c['authority_complete']
        players.append({'player':p, 'arm':arm, 'in_final_members':p in eligible,
                        'authority_observed':accepted_n,
                        'target_N':accepted_n if known else None,
                        'target_status':'known' if known else 'unknown',
                        'parsed_observed':sum(r['player']==p for r in parsed.values()),
                        'final_observed':sum(r['player']==p for r in final.values())})
    groups = {}
    for arm in ('C','T'):
        ps = [p for p in players if p['arm']==arm]
        groups[arm] = {'assigned':len(ps), 'final_members':sum(p['in_final_members'] for p in ps),
                       'target_N':sum(p['target_N'] for p in ps) if all(p['target_N'] is not None for p in ps) else None,
                       'authority_observed':sum(p['authority_observed'] for p in ps),
                       'final_observed':sum(p['final_observed'] for p in ps)}
    return {'groups':groups,'players':players,
            'anchor_not_received_at_snapshot':sorted(set(anchors)-raw_ids),
            'received_not_parsed':rejects,'duplicate_copies_removed':duplicates,
            'parsed_not_final':sorted(set(parsed)-set(final)),
            'members_excluded':sorted(set(roster)-eligible),
            'parsed_sequence_gaps':gaps,
            'sequence_coverage':'Stage: parsed after validation and deduplication. Gaps may arise in transport OR rejection during parsing; inspect received_not_parsed and raw receipt IDs. Only internal endpoints; no assertion about absent epochs or tails.',
            'target_semantics':c['target_start']}

if __name__ == '__main__':
    print(json.dumps(analyze(json.loads(Path(sys.argv[1]).read_text())),ensure_ascii=False,indent=2,sort_keys=True))
