"""Integer-frame item-puzzle reference model, not an engine or network test.

Snapshot is state AFTER frame 1; correction replaces inputs for frames 2..5.
Event identity is (frame, actor, kind, local ordinal). This fixture has at most
one event of a given kind per frame. Identity/payload changes, irreversible
transient compensation, actual sound playback, and network delivery are NOT
modeled. Presentation records are reversible bookkeeping, not heard sounds.
"""
from dataclasses import dataclass, asdict
from copy import deepcopy
import json

@dataclass
class State:
    frame: int = 0
    coins: int = 0
    torch_origin: int = 0
    beam_origin: int = 0
    glow_origin: int = 0

def event(frame, kind):
    return f'{frame}:player-1:{kind}:0'

def step(state, frame, actions):
    assert frame == state.frame + 1
    s = deepcopy(state)
    s.frame = frame
    events = []
    for action in actions:
        if action == 'light_torch':
            s.torch_origin = frame
        elif action == 'land':
            events.append(event(frame, 'landing'))
        elif action == 'take_coin':
            s.coins += 1
            events.append(event(frame, 'coin_chime'))
        elif action == 'beam_on':
            s.beam_origin = frame
        elif action == 'glow_on':
            s.glow_origin = frame
        else:
            raise ValueError(action)
    return s, events

def active(state):
    return {event(origin, kind) for kind, origin in [
        ('torch_loop', state.torch_origin), ('beam_loop', state.beam_origin),
        ('glow_loop', state.glow_origin)] if origin}

def run(snapshot, inputs, last=5):
    s = deepcopy(snapshot)
    journal = []
    states = []
    for frame in range(s.frame + 1, last + 1):
        s, events = step(s, frame, inputs.get(frame, []))
        journal.extend(events)
        states.append(asdict(s))
    return s, journal, states

prefix, prefix_events = step(State(), 1, ['light_torch'])
assert prefix_events == []
predicted = {2: ['land'], 3: ['beam_on']}
corrected = {2: ['land'], 3: ['take_coin'], 4: ['glow_on']}
old, old_journal, old_states = run(prefix, predicted)
new, new_journal, new_states = run(prefix, corrected)
assert prefix == State(frame=1, torch_origin=1)  # restore never mutates snapshot
assert old.coins == 0 and new.coins == 1
assert old.frame == new.frame == 5
landing = event(2, 'landing')
coin = event(3, 'coin_chime')
torch = event(1, 'torch_loop')
beam = event(3, 'beam_loop')
glow = event(4, 'glow_loop')
assert old_journal == [landing] and new_journal == [landing, coin]

# Original predicted events have already reached the presentation registry.
# Eager replay repeats unchanged events and never retracts old continuous work.
eager_calls = old_journal + new_journal
eager_active = active(old) | active(new)
# Suppress-all avoids duplicates but never discovers newly introduced events;
# the preexisting presentation state is left untouched.
suppressed_calls = list(old_journal)
suppressed_active = active(old)

# Collect a complete replacement suffix first. Keep only its corrected logical
# event registry, but keep a separate delivery ledger so unchanged effects are
# not replayed. Continuous effects are reconciled from the COMPLETE final state,
# including pre-rollback origins, not merely from suffix start events.
delivered = set(old_journal)
registered_suffix = list(new_journal)
new_calls = [key for key in new_journal if key not in delivered]
delivered.update(new_calls)
existing_active = active(old)
desired_active = active(new)
stopped = existing_active - desired_active
started = desired_active - existing_active
retained = existing_active & desired_active
reconciled_active = (existing_active - stopped) | started
assert new_calls == [coin]
assert eager_calls.count(landing) == 2
assert coin not in suppressed_calls
assert beam in eager_active and beam in suppressed_active
assert stopped == {beam} and started == {glow} and retained == {torch}
assert reconciled_active == {torch, glow}
assert registered_suffix.count(landing) == registered_suffix.count(coin) == 1
# Same corrected result delivered again is a no-op for both mechanisms.
repeat_calls = [key for key in new_journal if key not in delivered]
repeat_stops = reconciled_active - desired_active
repeat_starts = desired_active - reconciled_active
assert not repeat_calls and not repeat_stops and not repeat_starts
# Looking only at the last corrected frame loses the new intermediate transient.
_, final_frame_events = step(State(**new_states[-2]), 5, corrected.get(5, []))
assert final_frame_events == [] and coin in new_journal

report = {
    'scope': 'Deterministic integer item puzzle; simulated presentation registry only; no engine, audio, transport, timing or concurrency test',
    'identity_contract': '(integer frame, stable actor, event kind, local ordinal); same identity has same payload here',
    'rollback': {'snapshot_after_frame': 1, 'replacement_suffix_inclusive': [2, 5], 'snapshot': asdict(prefix)},
    'predicted': {'inputs': predicted, 'states': old_states, 'transient_journal': old_journal, 'active_at_frame_5': sorted(active(old))},
    'corrected': {'inputs': corrected, 'states': new_states, 'transient_journal': new_journal, 'active_at_frame_5': sorted(active(new))},
    'eager_replay': {'delivered_calls': eager_calls, 'active': sorted(eager_active), 'failure': 'unchanged landing replayed; wrong predicted beam survives'},
    'suppress_all_replay': {'delivered_calls': suppressed_calls, 'active': sorted(suppressed_active), 'failure': 'intermediate coin chime and new glow missing; wrong beam survives'},
    'reconcile': {'registered_corrected_suffix': registered_suffix, 'new_transient_calls': new_calls, 'stopped': sorted(stopped), 'started': sorted(started), 'retained_without_restart': sorted(retained), 'active': sorted(reconciled_active), 'repeat_new_calls': repeat_calls, 'repeat_starts': sorted(repeat_starts), 'repeat_stops': sorted(repeat_stops)},
    'limits': ['Already heard incorrect one-shots cannot be undone by registry replacement.', 'Production identities must distinguish changed semantic events; payload updates need an explicit policy.', 'No claim of exactly-once delivery across crashes or external consumers.', 'Continuous state here is binary existence; phase, position and parameter reconciliation are not modeled.', 'No event retention/confirmation window, overlapping corrections or lifecycle garbage collection modeled.']
}
print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
