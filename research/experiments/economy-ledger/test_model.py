import unittest
from model import Ledger, simulate

class EconomyTests(unittest.TestCase):
    def test_opening_stock_requires_entry(self):
        x=Ledger()
        self.assertEqual(x.balance,0)
        x.post('opening',100,'opening-stock')
        x.assert_conservation()
        self.assertEqual(x.entries,[('opening',100,'opening-stock')])

    def test_constructor_state_injection_disallowed(self):
        for kwargs in ({'balance':100},{'entries':[('opening',100,'source')]},
                       {'seen':{'opening'}}):
            with self.subTest(kwargs=kwargs), self.assertRaises(TypeError):
                Ledger(**kwargs)

    def test_malformed_event_id_is_atomic(self):
        x=Ledger();x.post('opening',10,'opening-stock')
        for event_id in (None,False,1,[],{},'', '   '):
            before=(x.balance,list(x.entries),set(x.seen))
            with self.subTest(event_id=event_id), self.assertRaises(ValueError):
                x.post(event_id,1,'source')
            self.assertEqual((x.balance,x.entries,x.seen),before)

    def test_malformed_parameters_rejected(self):
        for name in ('encounters','sessions','reward','cost','welcome','upgrade_price'):
            for value in (True,False,1.5,'1',None,-1):
                with self.subTest(name=name,value=value), self.assertRaises(ValueError):
                    simulate(**{name:value})
        with self.assertRaises(ValueError):simulate(upgrade_price=0)

    def test_bool_currency_rejected_without_mutation(self):
        x=Ledger()
        for amount in (True,False):
            with self.assertRaises(TypeError):x.post('bad',amount,'source')
        self.assertEqual((x.balance,x.entries,x.seen),(0,[],set()))

    def test_baseline_threshold_and_stock(self):
        r=simulate()
        self.assertEqual(r['bought_at_session'],3)
        self.assertEqual(r['balance'],340)
        self.assertEqual(r['snapshots'][:3],[148,196,4])

    def test_one_time_events_do_not_recur(self):
        events=simulate()['ledger'].entries
        self.assertEqual(sum(e[0]=='welcome' for e in events),1)
        self.assertEqual(sum(e[0]=='upgrade' for e in events),1)

    def test_duplicate_rejected_without_mutation(self):
        x=Ledger();x.post('welcome',100,'source')
        with self.assertRaises(ValueError):x.post('welcome',100,'source')
        self.assertEqual((x.balance,len(x.entries)),(100,1))

    def test_insufficient_balance_is_atomic(self):
        x=Ledger();x.post('initial',3,'source')
        before=(x.balance,list(x.entries),set(x.seen))
        with self.assertRaises(ValueError):x.post('spend',-4,'sink')
        self.assertEqual((x.balance,x.entries,x.seen),before)

    def test_failed_spend_can_retry_same_id_after_funding(self):
        x=Ledger();x.post('initial',3,'source')
        with self.assertRaises(ValueError):x.post('spend',-4,'sink')
        x.post('topup',1,'source');x.post('spend',-4,'sink')
        self.assertEqual(x.balance,0)
        self.assertEqual(sum(e[0]=='spend' for e in x.entries),1)
        x.assert_conservation()

    def test_integer_currency_rejects_fraction(self):
        with self.assertRaises(TypeError):Ledger().post('bad',0.5,'source')

    def test_conservation_all_cases(self):
        for n in (0,1,3,6,12):
            r=simulate(encounters=n)
            r['ledger'].assert_conservation()
            self.assertTrue(all(v>=0 for v in r['snapshots']))

    def test_cohort_mean_does_not_predict_completion(self):
        heavy=simulate(encounters=6,sessions=5)
        light=simulate(encounters=3,sessions=5)
        actual_completed=sum(x['bought_at_session'] is not None for x in (heavy,light))
        mean_net_per_session=((12-4)*6+(12-4)*3)//2
        mean_affordable_at=next(s for s in range(1,6) if 100+s*mean_net_per_session>=240)
        self.assertEqual((actual_completed,mean_affordable_at),(1,4))

    def test_sensitivity_not_universal_balance(self):
        self.assertEqual(simulate(reward=10)['bought_at_session'],4)
        self.assertEqual(simulate(reward=14)['bought_at_session'],3)
        self.assertEqual(simulate(upgrade_price=300)['bought_at_session'],5)
        self.assertEqual(simulate(welcome=0)['bought_at_session'],5)

if __name__=='__main__':unittest.main(verbosity=2)
