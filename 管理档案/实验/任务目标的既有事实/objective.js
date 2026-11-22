"use strict";
const key="R";
function fresh(){return {activeAt:null,through:0,held:false,ever:false,scopeComplete:true,
  firstAfter:false,receipt:false,sceneCount:0};}
function objective(s){
  if(s.activeAt===null)return null;
  return {have:s.held,found:s.ever||(!s.scopeComplete?null:false),after:s.firstAfter};
}
function apply(s,e){
  if(e.seq<=s.through)return "covered";
  if(e.seq!==s.through+1)throw Error("missing events");
  s.through=e.seq;
  switch(e.type){
    case "activate": if(s.activeAt===null)s.activeAt=e.seq;break;
    case "collect":
      if(e.item!==key)break;
      s.held=true;s.ever=true;
      if(s.activeAt!==null && e.seq>s.activeAt)s.firstAfter=true;
      break;
    case "consume": if(e.item===key)s.held=false;break;
    case "present":
      if(e.item===key&&s.activeAt!==null&&s.held&&!s.receipt){s.held=false;s.receipt=true;s.sceneCount++;}
  }
  return "applied";
}
const e=(seq,type,item=key,tick=0)=>({seq,type,item,tick});
function run(events,state=fresh()){for(const x of events)apply(state,x);return state;}
const rows={};
rows.beforeAndSpent=objective(run([e(1,"collect"),e(2,"consume"),e(3,"activate")]));
rows.sameTickBefore=objective(run([e(1,"collect",key,20),e(2,"activate",key,20)]));
rows.sameTickAfter=objective(run([e(1,"activate",key,20),e(2,"collect",key,20)]));
rows.nonTarget=objective(run([e(1,"activate"),e(2,"collect","similar-item")]));
const legacy={...fresh(),through:27,scopeComplete:false};
rows.oldSaveUnknown=objective(run([e(28,"activate")],legacy));
const persistent=run([e(1,"collect"),e(2,"activate")]);
rows.adoptExistingWithoutScene=[objective(persistent),persistent.sceneCount];
const wrong=run([e(1,"collect"),e(2,"activate"),e(3,"present","similar-item")]);
rows.wrongPresent=[wrong.held,wrong.receipt,wrong.sceneCount];
const ahead=JSON.parse(JSON.stringify(persistent));
const duplicateBefore=apply(ahead,e(1,"collect"));
run([e(3,"present")],ahead);
const reloaded=JSON.parse(JSON.stringify(ahead));
const duplicateAfter=apply(reloaded,e(3,"present"));
rows.afterReload=[duplicateBefore,duplicateAfter,objective(reloaded),reloaded.receipt,reloaded.sceneCount];
const want={
 beforeAndSpent:{have:false,found:true,after:false},
 sameTickBefore:{have:true,found:true,after:false},
 sameTickAfter:{have:true,found:true,after:true},
 nonTarget:{have:false,found:false,after:false},
 oldSaveUnknown:{have:false,found:null,after:false},
 adoptExistingWithoutScene:[{have:true,found:true,after:false},0],
 wrongPresent:[true,false,0],
 afterReload:["covered","covered",{have:false,found:true,after:false},true,1]
};
if(JSON.stringify(rows)!==JSON.stringify(want))throw Error(JSON.stringify(rows));
console.log(JSON.stringify(rows,null,2));
