"use strict";
// x=0 is the shared world seam. u is atlas texel-center coordinates.
const sample=(a,u)=>{const i=Math.floor(u), f=u-i;return a[i]*(1-f)+a[i+1]*f;};
const round=x=>Number(x.toFixed(4));
function row(name,atlas,uL,uR){
  const l=sample(atlas,uL),r=sample(atlas,uR);
  return {name,atlas,edge_uv_texel_centers:[uL,uR],left:round(l),right:round(r),jump:round(r-l)};
}
const cases=[
  row("same baked value, neighboring chart contaminates only left", [0.6,0.2,0.6,0.6], 0.25, 2.75),
  row("same baked value, own values copied into gutters", [0.6,0.6,0.6,0.6], 0.25, 2.75),
  row("the two baked edge values disagree despite own gutters", [0.48,0.48,0.66,0.66], 0.25, 2.75),
  row("synthetic continuous chart uses same sampling position on seam", [0.48,0.54,0.6,0.66], 1.5, 1.5)
];
const expected=[[0.5,0.6,0.1],[0.6,0.6,0],[0.48,0.66,0.18],[0.57,0.57,0]];
if(JSON.stringify(cases.map(x=>[x.left,x.right,x.jump]))!==JSON.stringify(expected))throw Error("fixture mismatch");
console.log(JSON.stringify(cases,null,2));
