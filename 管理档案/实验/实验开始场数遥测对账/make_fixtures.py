"""Teaching fixtures. Hidden narratives live only in oracle/, never analyzer input."""
import copy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')

def base(t_count=3):
    assignment=[{'player':a+str(i),'arm':a,'assigned_at':0} for a in ('C','T') for i in (1,2)]
    accepted=[]
    for p in assignment:
        for n in range(1,(3 if p['arm']=='C' else t_count)+1):
            accepted.append({'id':p['player']+'-'+str(n),'player':p['player'],'start_at':n*10})
    received=[dict(r,arm=r['player'][0],received_at=r['start_at']+1,epoch='install1',seq=int(r['id'].split('-')[1])) for r in accepted]
    return {'contract':{'target_start':'server_accept','authority_complete':True,'start_window':[0,60],'snapshot':100},
            'assignment':assignment,'accepted':accepted,'received':received,
            'query':{'mode':'all_assigned','qualifying_players':[]}}

def project_click_world(world):
    # Server only observes accepted requests. Client click upload may disappear.
    # This experiment's observed stream contains start telemetry, not click logs.
    d = base()
    d['contract']['target_start'] = 'client_click'
    d['observation_stream_id'] = 'stream-09'
    d['accepted'] = [copy.deepcopy(e['accept_record']) for e in world['clicks'] if e['accept_record'] is not None]
    d['received'] = [copy.deepcopy(e['start_receipt']) for e in world['clicks'] if e['start_receipt'] is not None and e['start_receipt']['received_at'] <= d['contract']['snapshot']]
    return d

def click_worlds():
    d=base()
    first={'clicks':[{'click_id':'click-'+a['id'], 'player':a['player'], 'click_at':a['start_at']-1,
                     'click_epoch':'original', 'click_seq':int(a['id'].split('-')[1]),
                     'accept_record':copy.deepcopy(a),'start_receipt':copy.deepcopy(r)}
                    for a,r in zip(d['accepted'],d['received'])]}
    second=copy.deepcopy(first)
    for i,(p,epoch,seq) in enumerate([('T2','unseen-install',1),('T1','original',4),('T1','original',5)]):
        second['clicks'].append({'click_id':'unseen-'+str(i),'player':p,'click_at':40+i,
                                'click_epoch':epoch,'click_seq':seq,
                                'accept_record':None,'start_receipt':None})
    return {'09':first,'10':second}

def main():
    cases={}
    cases['01']=base(2)
    cases['02']=base(); cases['02']['received']=[r for r in cases['02']['received'] if r['id']!='T1-2']
    cases['03']=base(); cases['03']['query']={'mode':'post_treatment_prompt_seen','qualifying_players':['C1','C2','T1']}
    late=base()
    for r in late['received']:
        if r['id']=='T1-2':r['received_at']=150
    cases['04']=copy.deepcopy(late); cases['04']['received']=[r for r in late['received'] if r['received_at']<=100]
    cases['05']=late; cases['05']['contract']['snapshot']=200
    cases['06']=base(); cases['06']['received'].append(copy.deepcopy(cases['06']['received'][-1]))
    cases['07']=base(); cases['07']['received'][-1]['arm']='C'
    cases['08']=base(); cases['08']['received']=[r for r in cases['08']['received'] if r['player']!='T2']
    worlds=click_worlds()
    cases['09']=project_click_world(worlds['09'])
    cases['10']=project_click_world(worlds['10'])
    save(ROOT/'oracle'/'click-worlds.json',worlds)
    cases['11']=base(); cases['11']['contract']['authority_complete']=False
    cases['12']=copy.deepcopy(cases['11'])
    for key,data in cases.items():
        data['observation_stream_id'] = 'stream-' + ({'05':'04','10':'09','12':'11'}.get(key,key))
    for key,data in cases.items():save(ROOT/'inputs'/('case-'+key+'.json'),data)
    save(ROOT/'oracle'/'hidden-worlds.json',{
      '01':'T has fewer server-accepted starts. No causal mechanism asserted.',
      '02':'T1-2 permanently lost before raw receipt.',
      '03':'T2 excluded by post-treatment prompt qualification.',
      '04':'T1-2 is delayed until 150; future arrival is not supplied to analyzer at snapshot 100.',
      '05':'Same source history as 04, later snapshot.',
      '06':'Exact duplicate transmission.', '07':'T2-3 incorrectly tagged C; actual assignment remains T.',
      '08':'All T2 start telemetry lost; server anchors survive.',
      '09':{'client_clicks':12,'additional_unseen':[]},
      '10':{'client_clicks':15,'additional_unseen':['T2 click rejected before server, whole epoch absent','T1 click rejected before server, unseen tail','T1 another unseen tail click']},
      '11':{'server_accepts':12,'unseen_authority_records':[]},
      '12':{'server_accepts':15,'unseen_authority_records':['three T2 starts absent from authority and client pipeline']}})
    save(ROOT/'oracle'/'expected.json',{'01':{'T_target':4},'02':{'missing':['T1-2']},'03':{'excluded':['T2']},'06':{'duplicates':['T2-3']},'07':{'reject':'assignment_label_conflict'},'08':{'missing':['T2-1','T2-2','T2-3']},'identical_pairs':[['02','04'],['09','10'],['11','12']]})

if __name__=='__main__':main()
