"use strict";
const records=[
 {id:"A",origin:-6,area:[-6,4],warn:100,hit:110,end:114,disclosed:true},
 {id:"B",origin:3,area:[3,7],warn:103,hit:116,end:120,disclosed:true},
 {id:"C",origin:2,area:[2,5],warn:101,hit:108,end:120,disclosed:false}
];
const decorations=Array.from({length:20},(_,i)=>"dust-"+i);
function renderSet(t,cam){
  return records.filter(r=>r.disclosed&&r.warn<=t&&t<r.end).flatMap(r=>{
    const clipped=[Math.max(r.area[0],cam[0]),Math.min(r.area[1],cam[1])];
    if(clipped[0]>=clipped[1])return [];
    return [{id:r.id,area:clipped,phase:t<r.hit?"warning":"active",impact:r.hit,left:Math.max(0,r.hit-t),startBurst:false}];
  });
}
const matrix=[105,106,109,110,114,116,120].map(t=>[t,renderSet(t,t===105?[8,16]:[0,8])]);
const recovered=matrix[1][1];
const origins=new Map(records.map(r=>[r.id,r.origin]));
const byOrigin=recovered.filter(x=>0<=origins.get(x.id)&&origins.get(x.id)<8);
const totalSlots=4,keep=2;
const decorationFirst=[...decorations,...recovered.map(x=>x.id)].slice(0,totalSlots);
const criticalFirst=[...recovered.slice(0,keep).map(x=>x.id),...decorations].slice(0,totalSlots);
const grid=Array.from({length:7},(_,n)=>recovered.filter(x=>x.area[0]<=n&&n<x.area[1]).map(x=>x.impact));
const wrongEarly=grid.flatMap((times,i)=>times.includes(110)?[]:[i]);
const wrongLate=grid.flatMap((times,i)=>times.includes(116)?[]:[i]);
const output={matrix,byOrigin:byOrigin.map(x=>x.id),decorationFirst,criticalFirst,grid,wrongEarly,wrongLate};
if(matrix[0][1].length||recovered.length!==2||byOrigin.map(x=>x.id).join()!=="B"||
   grid[3].join()!=="110,116"||wrongEarly.join()!=="4,5,6"||wrongLate.join()!=="0,1,2"||
   matrix[3][1].map(x=>x.phase).join()!=="active,warning"||
   matrix[4][1].map(x=>x.id).join()!=="B"||matrix[6][1].length||
   decorationFirst.some(x=>!x.startsWith("dust"))||criticalFirst.slice(0,2).join()!=="A,B")
  throw Error(JSON.stringify(output));
console.log(JSON.stringify(output,null,2));
