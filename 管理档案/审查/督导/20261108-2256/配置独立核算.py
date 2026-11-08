import itertools as it, re, json
from pathlib import Path
p=Path(__file__).resolve().parents[4]
# Direct construction by legal P,V,U triples, independently of author predicate.
pvu=[('desktop','compact','100'),('desktop','compact','125'),('desktop','wide','100'),('desktop','wide','125'),('desktop','wide','150'),('handheld','compact','100'),('handheld','compact','125')]
legal=[a+(t,c) for a in pvu for t in ['normal','large'] for c in ['0','5']]
rows=[]
for line in (p/'GameLibrary/项目管理与测试/质量保证/测试设计/游戏UI配置回归的约束建模与组合覆盖.md').read_text().splitlines():
 if re.match(r'^\| \d+ \|',line): rows.append(tuple(x.strip() for x in line.split('|')[2:-1]))
pairs=list(it.combinations(range(5),2)); utc=(2,3,4)
def project(rs,g):return {tuple(r[i] for i in g) for r in rs}
def coverage(rs):return {'pairs':sum(len(project(rs,g)) for g in pairs),'utc':len(project(rs,utc)),'missing_utc':sorted(project(legal,utc)-project(rs,utc))}
def greedy(groups,pool):
 req={(g,v) for g in groups for v in project(pool,g)}; selected=[]
 while req:
  best=max(pool,key=lambda r:len({(g,tuple(r[i] for i in g)) for g in groups}&req))
  selected.append(best);req-={(g,tuple(best[i] for i in g)) for g in groups}
 return selected
# itertools product ordering matches value-domain order stated in article.
domains=[['desktop','handheld'],['compact','wide'],['100','125','150'],['normal','large'],['0','5']]
pool=[r for r in it.product(*domains) if r in legal]
out={'legal':len(legal),'pair_counts':{''.join('PVUTC'[i] for i in g):len(project(legal,g)) for g in pairs},'rows_all_legal':all(r in legal for r in rows),'full':coverage(rows),'first8':coverage(rows[:8]),'minus1':coverage(rows[1:]),'minus12':coverage(rows[:-1]),'pair_greedy_equals_first8':greedy(pairs,pool)==rows[:8],'mixed_greedy_equals12':greedy(pairs+[utc],pool)==rows,'PU_handheld150_witnesses':[r for r in legal if r[0]=='handheld' and r[2]=='150']}
# More severe removal: row3 uniquely carries handheld large and handheld C5.
out['minus3']=coverage(rows[:2]+rows[3:]);out['minus3_missing_pairs']=[[''.join('PVUTC'[i] for i in g),v] for g in pairs for v in sorted(project(legal,g)-project(rows[:2]+rows[3:],g))]
print(json.dumps(out,ensure_ascii=False,indent=2))
