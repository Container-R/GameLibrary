"""Orthographic profile fixture. Not mesh rendering or a Kharak reconstruction."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).parent
# x,z in metres. Two chunks meet at x=0; profile has a ridge peak there.
ref=[(-4,0),(-2,1),(0,2),(2,1),(4,0)]
cases={
 'ridge_shift':([(-4,0),(-2,1),(0,1.5),(1,2),(2,1.5),(4,0)],None),
 'chunk_gap':([(-4,0),(-2,1),(0,2)],[(0,1.8),(2,1),(4,0)]),
 'rule_shift':(ref,None)
}
fig,axes=plt.subplots(2,3,figsize=(12,6),dpi=150)
observed=[]
for row,scale in enumerate([40,10]):
 for col,(name,(left,right)) in enumerate(cases.items()):
  ax=axes[row,col]
  project=lambda pts:([320+x*scale for x,z in pts],[150-z*scale for x,z in pts])
  ax.plot(*project(ref),'--',color='#536675',label='reference render',linewidth=2)
  ax.plot(*project(left),color='#df6a26',label='candidate render',linewidth=1.4)
  if right: ax.plot(*project(right),color='#df6a26',linewidth=1.4)
  if name=='rule_shift':
   ax.axvline(320,color='#536675',linestyle=':',label='baseline rule ridge')
   ax.axvline(320+scale,color='#913cb0',label='candidate rule ridge')
  ax.set(xlim=(120,520),ylim=(170,40),title=f'{name}; {scale} px/m',xlabel='screen x (px)',ylabel='screen y (px)')
  ax.grid(alpha=.2);ax.legend(fontsize=6)
  observed.append({'case':name,'scale_px_per_m':scale,'metric':{'ridge_shift':'horizontal peak displacement','chunk_gap':'vertical seam endpoint gap','rule_shift':'horizontal rule ridge displacement'}[name],'value_px':scale*({'ridge_shift':max(left,key=lambda p:p[1])[0]-max(ref,key=lambda p:p[1])[0],'chunk_gap':abs(left[-1][1]-right[0][1]) if right else 0,'rule_shift':1}[name])})
assert [round(v['value_px'],6) for v in observed]==[40,8,40,10,2,10]
fig.tight_layout();fig.savefig(R/'comparisons.png');plt.close(fig)
# Pure 2D rule example: shot crosses original x=0 ridge but not shifted x=1 ridge.
shot=(-.5,.5)
cross=lambda ridge: shot[0]<ridge<shot[1]
assert cross(0) and not cross(1)
assert cases['rule_shift'][0]==ref
out={'projection':'orthographic side profile; u=320+s*x,v=150-s*z','units':'metres and pixels','results':observed,'shot_x_interval':shot,'baseline_blocks':cross(0),'shifted_blocks':cross(1),'rule_shift_render_identical':True,'height_rule_example':{'baseline_height_m':2,'stale_height_m':1.5,'advantage_threshold_m':1.75,'baseline_has_advantage':2>=1.75,'stale_has_advantage':1.5>=1.75}}
(R/'observed.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
