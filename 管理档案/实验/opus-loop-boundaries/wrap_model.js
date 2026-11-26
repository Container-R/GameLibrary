function mixPulls(begin, end, pulls, defer=false) {
 let src=begin; const output=[], events=[];
 for(let block=0;block<pulls.length;block++){
   let left=pulls[block], offset=0;
   if(src===end){src=begin;events.push([block,offset,output.length]);}
   while(left>0){
     const n=Math.min(left,end-src);
     for(let i=0;i<n;i++) output.push(src+i);
     src+=n; left-=n;offset+=n;
     if(left>0&&src===end){
       if(defer){while(left-->0)output.push(null);break}
       src=begin;events.push([block,offset,output.length]);
     }
   }
 }
 return {output,events};
}
const begin=62513,end=63214,period=end-begin;
function check(b,e,blocks){
 const r=mixPulls(b,e,blocks);
 if(r.output.length!==blocks.reduce((x,y)=>x+y,0)) throw Error("output length");
 if(!r.output.every((x,i)=>x===b+i%(e-b))) throw Error("source mapping");
 return r;
}
const a=check(begin,end,[512,512,512,512,512]);
const b=mixPulls(begin,end,[512,512,512,512,512],true);
const tiny=check(10,13,[11,4]);
const exact=check(begin,end,[701,701]);
const variable=check(begin,end,[479,128,2048,1]);
const report={
  period,goodEvents:a.events,badEvents:b.events,badSecondBlockGap:b.output.slice(512,1024).filter(x=>x===null).length,
  boundary:a.output.slice(698,705),tinyOutput:tiny.output,exactEvents:exact.events,
  variableTotal:variable.output.length
};
if(report.badSecondBlockGap!==323 || a.events[0].join()!=="1,189,701" || b.events[0].join()!=="2,0,1024")throw Error("unexpected controls");
console.log(JSON.stringify(report));
