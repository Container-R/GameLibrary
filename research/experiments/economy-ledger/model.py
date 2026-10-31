"""Original illustrative single-player economy ledger, no external dependencies.
Coins are integers; this is not observed player behaviour or a production save system.
"""
from dataclasses import dataclass, field
import json

@dataclass
class Ledger:
    balance: int = field(default=0, init=False)
    entries: list = field(default_factory=list, init=False)
    seen: set = field(default_factory=set, init=False)

    def post(self, event_id, amount, kind):
        # kind is descriptive metadata, not an enforced source/sink policy.
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError('event_id must be a nonempty string')
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError('whole coins only')
        if event_id in self.seen:
            raise ValueError('duplicate economic event')
        if self.balance + amount < 0:
            raise ValueError('insufficient coins')
        self.balance += amount
        self.entries.append((event_id, amount, kind))
        self.seen.add(event_id)

    def assert_conservation(self):
        assert self.balance == sum(amount for _, amount, _ in self.entries)


def simulate(encounters=6, sessions=10, reward=12, cost=4,
             welcome=100, upgrade_price=240):
    if any(not isinstance(v,int) or isinstance(v,bool) or v < 0 for v in
           (encounters,sessions,reward,cost,welcome,upgrade_price)):
        raise ValueError('parameters must be nonnegative integers')
    if upgrade_price == 0:
        raise ValueError('upgrade price must be positive')
    ledger = Ledger()
    bought_at = None
    snapshots = []
    ledger.post('welcome', welcome, 'one-time-source')
    for session in range(1, sessions+1):
        for encounter in range(encounters):
            # Hypothetical contract: win -> reward -> required same-encounter service fee.
            ledger.post(f'{session}:{encounter}:reward', reward, 'recurring-source')
            ledger.post(f'{session}:{encounter}:service', -cost, 'recurring-sink')
        # Purchase only at session boundary, and at most once.
        if bought_at is None and ledger.balance >= upgrade_price:
            ledger.post('upgrade', -upgrade_price, 'one-time-sink')
            bought_at = session
        ledger.assert_conservation()
        snapshots.append(ledger.balance)
    return {'bought_at_session':bought_at,'balance':ledger.balance,
            'snapshots':snapshots,'ledger':ledger}


def summary():
    cases = {}
    for name, params in [
        ('baseline_6_encounters', {}),
        ('light_3_encounters', {'encounters':3}),
        ('no_welcome', {'welcome':0}),
        ('reward_10', {'reward':10}),
        ('reward_14', {'reward':14}),
        ('price_300', {'upgrade_price':300})]:
        result=simulate(**params)
        cases[name]={k:v for k,v in result.items() if k != 'ledger'}
    return cases

if __name__ == '__main__':
    print(json.dumps(summary(), indent=2))
