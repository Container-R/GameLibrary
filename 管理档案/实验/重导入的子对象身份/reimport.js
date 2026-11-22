"use strict";
const assert = require("node:assert/strict");
const nativeExport = require("./blender.observed.json");

const id = (n) => "80a06da0-efde-4550-a0af-"+n.toString().padStart(12,"0");
const original = [
  {id:id(1), label:"Metal", use:"outer rail", aliases:["outside-rail"], bytes:"metal:v1"},
  {id:id(2), label:"Glass", use:"window pane", aliases:["window"], bytes:"glass:v1"},
  {id:id(3), label:"Latch", use:"side door", aliases:["side-latch"], bytes:"latch:v1"},
];
const seenAliases = new Map(original.flatMap(x=>x.aliases.map(a=>[a,x.id])));
const key = {
  index: (p,i) => "material:"+i,
  label: (p) => "material:"+p.label,
  stable: (p) => "material:"+p.id,
  content: (p) => "material:"+p.bytes,
};
function build(rows, fn, retired = new Set()) {
  const artifacts = new Map();
  const entryIds = new Set();
  for (const [i,p] of rows.entries()) {
    if (typeof p.id !== "string" || !p.id.trim()) throw new Error("missing source identity");
    if (retired.has(p.id)) throw new Error("retired identity reused");
    if (entryIds.has(p.id)) throw new Error("copied source identity");
    entryIds.add(p.id);
    const k = fn(p,i);
    if (artifacts.has(k)) throw new Error("key collision");
    artifacts.set(k,p);
  }
  return artifacts;
}
function compare(rows, f) {
  const before = build(original,f), after = build(rows,f);
  return [...before].map(([k,first]) => {
    const matched = after.get(k);
    return {expected:first.use,
            observed:matched?.use??null,
            result:!matched?"missing":matched.id===first.id?"same":"wrong"};
  });
}
const changed = [
  {...original[1]},
  {id:id(4), label:"Latch",use:"window clip",aliases:["clip"],bytes:"clip:v1"},
  {...original[0],label:"Exterior Metal",bytes:"metal:v2"},
];
const fields = (rows) => rows.map((p,i)=>({index:i,name:p.label,source_id:p.id}));
assert.deepEqual(nativeExport.before,fields(original));
assert.deepEqual(nativeExport.after,fields(changed));
const output = Object.fromEntries(Object.entries(key).map(([kind,fn])=>[kind,compare(changed,fn)]));
assert.deepEqual(output.index.map(x=>x.result),["wrong","wrong","wrong"]);
assert.deepEqual(output.label.map(x=>x.result),["missing","same","wrong"]);
assert.deepEqual(output.stable.map(x=>x.result),["same","same","missing"]);
assert.deepEqual(output.content.map(x=>x.result),["missing","same","missing"]);
assert.throws(()=>build([...changed,{...changed[0], label:"Glass copy"}],key.stable), /copied source identity/);
assert.throws(()=>build([...changed,original[2]],key.stable,new Set([id(3)])), /retired identity reused/);
assert.throws(()=>build([...changed,{...original[2],id:id(5)}],key.label), /key collision/);
assert.throws(()=>build([{...changed[0],id:undefined}],key.stable), /missing source identity/);
assert.throws(()=>build([{...changed[0],id:"   "}],key.stable), /missing source identity/);
assert.throws(()=>build(nativeExport.without_extras.map((p,i)=>({...changed[i],id:p.source_id})),key.stable), /missing source identity/);
assert.equal(seenAliases.get("side-latch"),id(3));
console.log(JSON.stringify(output,null,2));
