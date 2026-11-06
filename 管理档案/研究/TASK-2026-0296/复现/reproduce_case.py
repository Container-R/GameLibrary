#!/usr/bin/env python3
"""Original deterministic teaching case. Standard library only; writes beside this file.
No network, installs, inherited code or optimization solver. SVG previews are rendered
separately with the already installed Inkscape. This script does not approve a schedule.
"""
from pathlib import Path
from itertools import combinations
import json
import html

OUT = Path(__file__).resolve().parent
TASKS = {
 'A': {'name':'确认路线与接收约定','d':.5,'pred':[],'resource':'L'},
 'B': {'name':'交出货箱锚点与导出样件','d':1,'pred':['A'],'resource':'T'},
 'C': {'name':'制作装卸动画','d':3,'pred':['B'],'resource':'N'},
 'D': {'name':'完成码头环境与碰撞','d':4,'pred':['A'],'resource':'T'},
 'E': {'name':'实现推车与交付状态','d':1.5,'pred':['A'],'resource':'P'},
 'F': {'name':'实现检查点复位','d':1,'pred':['E'],'resource':'P'},
 'G': {'name':'检查动画输入','d':.5,'pred':['C'],'resource':'Q'},
 'H': {'name':'整合三路输入','d':1,'pred':['D','F','G'],'resource':'P'},
 'I': {'name':'生成并登记候选构建','d':.5,'pred':['H'],'resource':'V'},
 'J': {'name':'目标设备走查','d':.5,'pred':['I'],'resource':'Q'},
 'K': {'name':'核对证据并接收','d':.25,'pred':['J'],'resource':'L'},
}

def cpm(tasks):
    pending=set(tasks); order=[]
    for k,t in tasks.items():
        assert t['d'] >= 0 and all(p in tasks for p in t['pred'])
    while pending:
        ready=sorted(k for k in pending if set(tasks[k]['pred']) <= set(order))
        if not ready: raise ValueError('cycle')
        for k in ready: order.append(k); pending.remove(k)
    rows={}; succ={k:[] for k in tasks}
    for k in order:
        t=tasks[k]; es=max([rows[p]['EF'] for p in t['pred']],default=0)
        rows[k]={'ES':es,'EF':es+t['d']}
        for p in t['pred']: succ[p].append(k)
    finish=max(r['EF'] for r in rows.values())
    for k in reversed(order):
        r=rows[k]; r['LF']=min([rows[s]['LS'] for s in succ[k]],default=finish)
        r['LS']=r['LF']-tasks[k]['d']; r['TF']=r['LS']-r['ES']
        r['FF']=min([rows[s]['ES'] for s in succ[k]],default=finish)-r['EF']
    return finish,rows

def all_paths(tasks, k='K'):
    if not tasks[k]['pred']: return [([k],tasks[k]['d'])]
    return [(p+[k],d+tasks[k]['d']) for a in tasks[k]['pred'] for p,d in all_paths(tasks,a)]

def with_change(k,d):
    ts={i:dict(t) for i,t in TASKS.items()};ts[k]['d']=d; return ts

def with_order(first, second, change=None):
    ts={k:dict(v,pred=list(v['pred'])) for k,v in TASKS.items()}
    ts[second]['pred'].append(first)  # Chosen resource order, not an input requirement.
    if change:
        k,d=change; ts[k]['d']=d
    return ts

def validate(tasks, intervals, blackouts=None):
    assert set(tasks)==set(intervals)
    for k,(s,e) in intervals.items():
        assert e-s==tasks[k]['d'], (k,s,e,tasks[k]['d'])
        assert s >= 0
        for p in tasks[k]['pred']: assert s>=intervals[p][1], ('FS',p,k)
        for u,v in (blackouts or {}).get(tasks[k]['resource'],[]):
            assert e<=u or v<=s, ('blackout',k,u,v)
    for a,b in combinations(intervals,2):
        if tasks[a]['resource']==tasks[b]['resource']:
            s,e=intervals[a];u,v=intervals[b]
            assert e<=u or v<=s, ('resource',a,b)
    return True

BASE={ 'A':[0,.5],'B':[.5,1.5],'C':[1.5,4.5],'D':[1.5,5.5],
 'E':[.5,2],'F':[2,3],'G':[4.5,5],'H':[5.5,6.5],'I':[6.5,7],
 'J':[7,7.5],'K':[7.5,7.75] }
LONG_FIRST={ 'A':[0,.5],'B':[4.5,5.5],'C':[5.5,8.5],'D':[.5,4.5],
 'E':[.5,2],'F':[2,3],'G':[8.5,9],'H':[9,10],'I':[10,10.5],
 'J':[10.5,11],'K':[11,11.25] }
UPDATE={ 'A':[0,.5],'B':[.5,1.5],'C':[1.5,5.5],'D':[1.5,5.5],
 'E':[.5,2],'F':[2,3],'G':[5.5,6],'H':[6,7],'I':[7,7.5],
 'J':[8.5,9],'K':[9,9.25] }
BACKUP=dict(UPDATE, J=[7.5,8],K=[8,8.25],U=[6,6.25])

def selftest():
    f,r=cpm(TASKS); assert f==7.25
    assert max(d for _,d in all_paths(TASKS))==f
    assert r['E']['TF']==r['F']['TF']==2 and r['E']['FF']==0 and r['F']['FF']==2
    assert r['D']['TF']==.5 and r['G']['TF']==0
    assert cpm(with_change('C',2.5))[0]==6.75
    assert cpm(with_change('C',2))[0]==6.75
    assert validate(TASKS,BASE) and validate(TASKS,LONG_FIRST)
    for order,plan in [(('B','D'),BASE),(('D','B'),LONG_FIRST)]:
        sf,sr=cpm(with_order(*order))
        assert {k:[v['ES'],v['EF']] for k,v in sr.items()}==plan
    assert cpm(with_order('B','D',('C',2.5)))[0]==7.75
    assert cpm(with_order('B','D',('D',3.5)))[0]==7.25
    assert cpm(with_order('B','D',('D',3)))[0]==7.25
    # The dependency-only schedule intentionally double-books T. Ensure detection.
    try: validate(TASKS,{k:[v['ES'],v['EF']] for k,v in r.items()})
    except AssertionError as err: assert err.args[0][0]=='resource'
    else: raise AssertionError('did not detect double booking')
    cycle={k:dict(v) for k,v in TASKS.items()};cycle['A']['pred']=['K']
    try: cpm(cycle)
    except ValueError: pass
    else: raise AssertionError('did not detect cycle')
    bad=dict(BASE,B=[0,1])
    try: validate(TASKS,bad)
    except AssertionError as err: assert err.args[0][0]=='FS'
    else: raise AssertionError('did not detect missing input')
    upd=with_change('C',4);assert validate(upd,UPDATE,{'Q':[(7.5,8.5)]})
    # Completed actuals and starts are immutable; C and D each have 1 day remaining at 4.5.
    for k in ['A','B','E','F']: assert UPDATE[k]==BASE[k]
    for k in ['C','D']: assert UPDATE[k][0]==BASE[k][0] and UPDATE[k][1]-4.5==1
    backup={k:dict(v) for k,v in upd.items()}
    backup['J']=dict(backup['J'],resource='Q2',pred=['I','U'])
    backup['U']={'name':'替补 QA 交接','d':.25,'pred':['G'],'resource':'Q'}
    assert validate(backup,BACKUP,{'Q':[(7.5,8.5)]})
    # U uses both Q and Q2; explicitly check the second resource as well.
    assert BACKUP['U'][1]<=BACKUP['J'][0]
    assert BACKUP['U']==[6,6.25] and BACKUP['J']==[7.5,8]
    # Delaying E by 2 days uses the shared float; another 2-day delay before F slips 2.
    shared=dict(BASE,E=[2.5,4],F=[6,7],H=[7,8],I=[8,8.5],J=[8.5,9],K=[9,9.25])
    assert validate(TASKS,shared)
    return f,r

def svg_open(w,h,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
      f'<title>{html.escape(title)}</title>', '<rect width="100%" height="100%" fill="#fff"/>',
      '<style>text{font-family:"Noto Sans CJK SC",sans-serif;fill:#152638} .small{font-size:15px}</style>']

def network():
    # Layout is logical, not a time scale. All arrows are input FS links.
    xy={'A':(28,180),'B':(230,60),'C':(445,60),'G':(660,60),
        'D':(445,180),'E':(230,300),'F':(445,300),'H':(875,180),
        'I':(1090,180),'J':(1090,300),'K':(875,420)}
    out=svg_open(1320,555,'货运码头：只有输入依赖的网络')
    out+=['<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#506578"/></marker></defs>',
      '<text x="28" y="30" font-size="22">货运码头内部可玩区：输入依赖（FS）</text>']
    w,h=190,72
    for k,t in TASKS.items():
        x,y=xy[k]
        for p in t['pred']:
            a,b=xy[p]
            if p=='I' and k=='J': coords=f'M {a+w/2},{b+h} L {x+w/2},{y}'
            elif p=='J' and k=='K': coords=f'M {a+w/2},{b+h} L {a+w/2},{y+h/2} L {x+w},{y+h/2}'
            else:
                mid=(a+w+x)/2
                coords=f'M {a+w},{b+h/2} L {mid},{b+h/2} L {mid},{y+h/2} L {x},{y+h/2}'
            out.append(f'<path d="{coords}" fill="none" stroke="#506578" stroke-width="2" marker-end="url(#arr)"/>')
    for k,t in TASKS.items():
        x,y=xy[k];color='#fff0ce' if k in ['B','D'] else '#eaf3f9'
        names={'A':'路线与接收约定','B':'锚点与导出样件','C':'装卸动画','D':'码头环境与碰撞','E':'推车与交付状态','F':'检查点复位','G':'动画输入检查','H':'三路整合','I':'候选构建','J':'目标设备走查','K':'核对证据与接收'}
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{color}" stroke="#8da3b3"/>',
          f'<text x="{x+10}" y="{y+29}" font-size="17">{k} {names[k]}</text>',
          f'<text x="{x+10}" y="{y+55}" font-size="15">{t["d"]:g} 工作日 · {t["resource"]}</text>']
    out+=['<text x="28" y="468" font-size="16">黄色 B、D 同属技术美术 T，但二者没有输入先后关系。</text>',
      '<text x="28" y="495" font-size="16">为解决资源冲突而选择 B→D 或 D→B，另记为资源顺序。</text>',
      '<text x="28" y="523" class="small">原创教学假设；方框不按持续时间缩放；接收终点为 K 完成。角色及判据见正文活动表。</text>','</svg>']
    return '\n'.join(out)

def timeline():
    out=svg_open(1320,620,'两种资源顺序的可行安排')
    out += ['<text x="24" y="30" font-size="23">两种资源可行安排：工作时间区间 [开始, 结束)</text>']
    x0,scale=160,94
    for off,plan,title in [(85,BASE,'先做 B：接收 7.75'),(370,LONG_FIRST,'先做 D：接收 11.25')]:
        out.append(f'<text x="24" y="{off-20}" font-size="18">{title}</text>')
        for t in range(13):
            x=x0+t*scale
            if t<=12:
                out += [f'<line x1="{x}" y1="{off}" x2="{x}" y2="{off+188}" stroke="#dce3e8"/>',
                  f'<text x="{x}" y="{off-4}" text-anchor="middle" class="small">{t}</text>']
        for row,res in enumerate(['L','T','N','P','Q','V']):
            y=off+row*31
            out.append(f'<text x="28" y="{y+22}" font-size="16">{res} '+{'L':'设计负责人','T':'技术美术','N':'动画师','P':'程序','Q':'QA','V':'构建人员'}[res]+'</text>')
            for k,(s,e) in plan.items():
                if TASKS[k]['resource']!=res: continue
                x=x0+s*scale;w=(e-s)*scale
                color='#f0bc60' if k in ['B','D'] else '#7bb8d9'
                out += [f'<rect x="{x}" y="{y+4}" width="{w}" height="24" fill="{color}" stroke="#fff"/>',
                  f'<text x="{x+w/2}" y="{y+22}" font-size="14" text-anchor="middle">{k}</text>']
    out+=['<text x="24" y="601" font-size="15">纵轴为单人资源；横轴为工作日边界。同一行无重叠才可行。假设全员在所示窗口可用，不含返工。</text>','</svg>']
    return '\n'.join(out)

if __name__=='__main__':
    finish,rows=selftest()
    results={'dependency_only_finish':finish,'cpm':rows,'paths':all_paths(TASKS),
      'compress_C':{str(d):cpm(with_change('C',d))[0] for d in [3,2.5,2]},
      'resource_B_D_changes':{f'{k}={d}':cpm(with_order('B','D',(k,d)))[0] for k,d in [('C',2.5),('D',3.5),('D',3)]},
      'short_first':BASE,'long_first':LONG_FIRST,'status_4_5':UPDATE,'backup_Q2':BACKUP,
      'status_4_5_Q_blackout':[7.5,8.5], 'checks':'selftests passed; resource checks passed; no optimization or probability claim'}
    (OUT/'case-data.json').write_text(json.dumps(TASKS,ensure_ascii=False,indent=2)+'\n')
    (OUT/'calculation-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    (OUT/'dependency-network.svg').write_text(network())
    (OUT/'resource-timeline.svg').write_text(timeline())
    print(json.dumps(results,ensure_ascii=False,indent=2))
