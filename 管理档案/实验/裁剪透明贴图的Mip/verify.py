from fractions import Fraction as F
import json

def source(counts):
    n = int(len(counts) ** .5)
    assert n*n == len(counts)
    rows = []
    for y in range(n):
        pair = [[int(p < k) for p in range(4)] for k in counts[y*n:(y+1)*n]]
        rows += [[i for b in pair for i in b[:2]], [i for b in pair for i in b[2:]]]
    return rows

def box(rows):
    n = len(rows)
    return [F(sum(rows[y+i][x+j] for i in range(2) for j in range(2)),4)
            for y in range(0,n,2) for x in range(0,n,2)]

def mask(values, threshold=F(13,20), scale=F(1)):
    return [int(min(F(1),v*scale) >= threshold) for v in values]

def coverage(values, **kwargs):
    m = mask(values, **kwargs)
    return str(F(sum(m),len(m)))

base = source([3]*3 + [2]*3 + [1]*9 + [0])
mip = box(base)
tie = box(source([3,1,1,1]))
a = [F(3,4), F(0), F(0), F(0)]
b = a[::-1]
out = {
    'base':coverage(sum(base, [])),
    'plain':coverage(mip),
    'scaled':coverage(mip,scale=F(7,5)),
    'scaled_lower_cutoff':coverage(mip,scale=F(7,5),threshold=F(3,10)),
    'tie_base':coverage(sum(source([3,1,1,1]), [])),
    'tie_attainable':sorted({coverage(tie,scale=s) for s in [F(0),F(1),F(13,5)]}),
    'same_coverage_different_positions':[mask(a),mask(b)],
}
assert list(out.values()) == ['3/8','3/16','3/8','15/16','3/8',['0','1','1/4'],[[1,0,0,0],[0,0,0,1]]]
print(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2))
