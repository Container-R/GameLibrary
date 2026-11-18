function run(frames, mode) {
  const definitions = {1:[{id:"c1",damage:3},{id:"c2",damage:2}], 2:[{id:"c3",damage:1}]};
  let hp=10; const ticks=[], events=[], shown=[]; const seen=new Set();
  for (let step=0;step<3;step++){
    for (const c of (definitions[step] ?? [])) {
      hp-=c.damage;
      events.push({step,id:c.id,damage:c.damage});
    }
    ticks.push([step,hp]);
    for (let frame=0;frame<frames[step];frame++) {
      for (const e of events) {
        const key=mode==="coalesceTick"?e.step:e.id;
        if (seen.has(key)) continue;
        seen.add(key); shown.push(e.id);
        if (mode==="writeback") hp-=e.damage;
      }
    }
  }
  return {ticks, emitted:events.map(e=>e.id), shown, endHP:hp};
}
const A=run([1,2,1],"correct"), B=run([0,0,3],"correct");
const C=run([0,0,3],"coalesceTick"), D=run([0,0,3],"writeback");
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
if (!same(A,B) || !same(A.ticks,C.ticks) || !same(A.emitted,C.emitted) ||
    !same(C.shown,["c1","c3"]) || !same(D.ticks,A.ticks) || D.endHP!==-2 || A.endHP!==4 ||
    !same(D.shown,A.shown)) throw new Error("Unexpected trail");
console.log(JSON.stringify({A,B,C,D},null,2));
