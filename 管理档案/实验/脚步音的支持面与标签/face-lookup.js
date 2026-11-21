"use strict";
const faces = [
  {face:10, surface:"metal", p:[[-1,-1],[0,-1],[0,1]]},
  {face:11, surface:"metal", p:[[-1,-1],[0,1],[-1,1]]},
  {face:20, surface:"stone", p:[[0,-1],[1,-1],[1,1]]},
  {face:21, surface:"stone", p:[[0,-1],[1,1],[0,1]]},
];
const signed = ([x,z],[a,b],[c,d]) => (c-a)*(z-b)-(d-b)*(x-a);
const contains = (q,p) => p.every((a,i)=>signed(q,a,p[(i+1)%3])>1e-9);
const results = [0,3].flatMap(tx => [-.2,.2].map((x,i)=>{
  const world=[tx+x,0], local=[world[0]-tx,world[1]];
  const matches=faces.filter(f=>contains(local,f.p));
  if(matches.length!==1) throw Error("ambiguous fixture");
  const f=matches[0];
  return {tx,foot:i===0?"L":"R",x:world[0],collider:"platform",shape:7,
    faceId:f.face,withoutFace:-1,objectTag:"generic",withFace:f.surface,
    localZone:local[0]<0?"metal":"stone",worldZone:world[0]<0?"metal":"stone"};
}));
const verify=(a,b)=>{if(JSON.stringify(a)!==JSON.stringify(b))throw Error("bad control")};
verify(results.map(r=>[r.faceId,r.withFace,r.localZone,r.worldZone]),[
  [10,"metal","metal","metal"],[21,"stone","stone","stone"],
  [10,"metal","metal","stone"],[21,"stone","stone","stone"],
]);
console.log(JSON.stringify(results,null,2));
