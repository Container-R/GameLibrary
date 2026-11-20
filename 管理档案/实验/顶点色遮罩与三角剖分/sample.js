"use strict";
// Exact arithmetic on a doubled sample grid: square corners are at 0/200,
// sample centers are all odd integers. No image, renderer or mesh optimizer.
const corners=[[0,0,1],[200,0,0],[200,200,1],[0,200,0]];
const white=[[0,1,2],[0,2,3]],black=[[0,1,3],[1,2,3]];
function area(a,b,c){return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);}
function evaluate(p,mesh){
 const matches=[];
 for(const tri of mesh){
  const [a,b,c]=tri.map(i=>corners[i]);
  const t=area(a,b,c),u=area(p,b,c),v=area(a,p,c),w=area(a,b,p);
  if(u>=0&&v>=0&&w>=0){
   if(t!==40000||u+v+w!==t)throw Error("area");
   matches.push(u*a[2]+v*b[2]+w*c[2]);
  }
 }
 if(!matches.length||!matches.every(v=>v===matches[0]))throw Error("coverage/internal edge");
 return matches[0]; // denominator 40000
}
function classify(n){return n*1000>=503*40000;}
let whiteOn=0,blackOn=0,paired=0,absSum=0,margin=Infinity;
let leftOn=0,rightOn=0,stripPaired=0,overlap=0;
for(let y=1;y<200;y+=2)for(let x=1;x<200;x+=2){
 const w=evaluate([x,y],white),b=evaluate([x,y],black);
 if(w!==40000-200*Math.abs(x-y)||b!==200*Math.abs(x+y-200))throw Error("formula disagrees");
 whiteOn+=Number(classify(w));blackOn+=Number(classify(b));
 paired+=Number(classify(w)!==classify(b));absSum+=Math.abs(w-b);
 margin=Math.min(margin,Math.abs(w*1000-503*40000),Math.abs(b*1000-503*40000));
 const L=x>=40&&x<80,R=x>=90&&x<130;
 leftOn+=Number(L);rightOn+=Number(R);stripPaired+=Number(L!==R);overlap+=Number(L&&R);
}
const center=[evaluate([100,100],white),evaluate([100,100],black)].map(v=>v/40000);
const diagonal={center,whiteOn,blackOn,paired,raw_mae:absSum/(40000*10000),
                closest_threshold_margin:margin/(40000*1000)};
const strips={leftOn,rightOn,stripPaired,overlap};
if(JSON.stringify(diagonal)!=='{"center":[1,0],"whiteOn":7450,"blackOn":2450,"paired":5000,"raw_mae":0.3334,"closest_threshold_margin":0.003}')throw Error("diagonal");
if(JSON.stringify(strips)!=='{"leftOn":2000,"rightOn":2000,"stripPaired":4000,"overlap":0}')throw Error("strip");
console.log(JSON.stringify({scope:"Numerical cell-center samples only, not pixels, renderer, simplifier, production asset or perceptual test",
  threshold:0.503,sample_grid:[100,100],diagonal,strips},null,2));
