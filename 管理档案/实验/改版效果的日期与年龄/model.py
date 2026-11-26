"""Exact aggregate contrasts in a synthetic account-cohort panel."""
from fractions import Fraction as F

# Entry day, assigned users per arm, control positives, treatment positives.
flat = [(0, 100, [30, 30, 30], [50, 50, 50]),
        (1, 300, [90, 90], [102, 102])]
fading = [(0, 100, [30, 30, 30], [50, 40, 35]),
          (1, 300, [90, 90], [102, 96])]

def calendar(panel, day):
    rows = [(n, t[day-start]-c[day-start])
            for start,n,c,t in panel if 0 <= day-start < len(c)]
    return F(sum(d for _,d in rows), sum(n for n,_ in rows))

def common_age(panel, age):
    # Both cohorts can be observed at ages 0 and 1.
    assert all(age < len(c) for _,_,c,_ in panel)
    estimates = [F(t[age]-c[age], n) for _,n,c,t in panel]
    return sum(estimates, F(0))/len(estimates)

for title, panel, expected in [
    ('flat', flat, ([F(1,5), F(2,25), F(2,25)], [F(3,25), F(3,25)])),
    ('fading', fading, ([F(1,5), F(11,200), F(11,400)], [F(3,25), F(3,50)])),
]:
    got=([calendar(panel,d) for d in range(3)], [common_age(panel,a) for a in range(2)])
    assert got==expected, got
    print(title, 'calendar', *(str(x) for x in got[0]),
          'age with common cohort weights', *(str(x) for x in got[1]))

# Complete cells only: the keys are (entry date, measurement date).
# Synthetic percentage-point lift against a 50% control in each cell.
date_effect = {(cohort, day): F(2-day, 10)
               for cohort in (0, 1) for day in (cohort, cohort+1)}
age_effect = {(cohort, day): F(3-2*(day-cohort), 20)
              for cohort in (0, 1) for day in (cohort, cohort+1)}
for title, cells, expected_shared in [
    ('date_only', date_effect, [F(1,10), F(1,10)]),
    ('age_only', age_effect, [F(1,20), F(3,20)]),
]:
    age_curve = [(cells[0,age]+cells[1,age+1])/2 for age in (0, 1)]
    shared_date = [cells[cohort,1] for cohort in (0, 1)]
    assert age_curve == [F(3,20), F(1,20)] and shared_date == expected_shared
    print(title, 'age', *(str(x) for x in age_curve),
          'shared date early/late', *(str(x) for x in shared_date))

# Per block: treatment successes/assigned and control successes/assigned.
ramp = [(8,10,63,90), (27,90,2,10)]
within = [F(ty,tn)-F(cy,cn) for ty,tn,cy,cn in ramp]
ty,tn,cy,cn = [sum(col) for col in zip(*ramp)]
pooled = (F(ty,tn), F(cy,cn))
standardized = sum(within, F(0))/len(within)
assert within == [F(1,10)]*2 and pooled == (F(7,20), F(13,20))
assert standardized == F(1,10)
print('ramp pooled T/C', *(str(x) for x in pooled), 'standardized lift', standardized)
