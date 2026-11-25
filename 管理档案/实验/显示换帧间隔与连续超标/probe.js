// Synthetic single-stream display fixture. Run: node probe.js
// Time unit is one 60 Hz tick; milliseconds are only formatted at output.
const ms = ticks => (ticks*50/3).toFixed(3);
const check = (ok, why) => { if (!ok) throw new Error(why); };
function spans(events) {
  return events.slice(1).map(([endFrame,end],i) => {
    const [frame,start]=events[i];
    check(end>start,"timestamps must increase in one continuous stream");
    return {frame,endFrame,start,end,ticks:end-start};
  });
}
function episodes(xs,budget) {
  const out=[];
  let current=null;
  for (const x of xs) {
    if (x.ticks>budget) {
      if (current && current.end===x.start) {
        current.end=x.end; current.frames++;
      } else { current={start:x.start,end:x.end,frames:1}; out.push(current); }
    } else current=null;
  }
  return out;
}
function trace(longAt) {
  const events=[["0",0]];
  for (let i=0;i<600;i++) events.push([String(i+1),events[i][1]+(longAt.includes(i)?3:1)]);
  return spans(events);
}
const scattered=trace([45,145,245,345,445,545]), clustered=trace([295,296,297,298,299,300]);
const sort=xs=>xs.map(x=>x.ticks).sort((a,b)=>a-b);
check(String(sort(scattered))===String(sort(clustered)),"same distribution");
for(const [name,xs] of [["scattered",scattered],["clustered",clustered]]) {
  const sorted=sort(xs), p99=sorted[Math.ceil(xs.length*99/100)-1];
  const es=episodes(xs,2), durations=es.map(x=>x.end-x.start);
  check(es.length===(name==="scattered"?6:1),"episode count");
  console.log(name+": total="+ms(xs.at(-1).end)+"ms, p99="+ms(p99)+"ms, max="+ms(sorted.at(-1))+"ms, episodes="+es.length+", longest="+ms(Math.max(...durations))+"ms");
}
const ids=Array.from("ABCDEF"), submitted=ids.map((f,i)=>[f,i-.5]);
const full=ids.map((f,i)=>[f,i]), displayed=[["A",0],["B",1],["E",4],["F",5]];
check(spans(submitted).every(x=>x.ticks===1),"flat submission");
check(spans(full).every(x=>x.ticks===1),"full display control");
const s=spans(displayed), b=s[1];
const overlap=Math.max(0,Math.min(b.end,5)-Math.max(b.start,2));
check(b.frame==="B"&&b.endFrame==="E"&&b.ticks===3&&overlap===2,"hold attribution");
const naive=spans(displayed.filter(([,t])=>t>=2&&t<5));
check(naive.length===0,"naive filter misses hold");
console.log("submit: 1,1,1,1,1 ticks; shown: "+s.map(x=>x.ticks).join(",")+" ticks; hold "+b.frame+" ends at "+b.endFrame);
console.log("marker [2,5): overlap="+ms(overlap)+"ms, filter-first intervals="+naive.length);
const thirty=spans([["W",0],["X",2],["Y",4],["Z",6]]);
check(thirty.filter(x=>x.ticks>1).length===3&&thirty.filter(x=>x.ticks>2).length===0,"intentional cadence");
console.log("30fps on 60Hz: overruns at 1 tick=3; at 2 ticks=0");
