import assert from 'node:assert/strict';

const authored = {
  schema: 1, rate: 60, move: 'hammer',
  branches: {
    ground: [
      {key:'hit',kind:'damage',frame:12,valueRule:'base+power@1'},
      {key:'dust',kind:'cue',frame:12,asset:'fx.ground.dust'},
    ],
    air: [
      {key:'hit',kind:'damage',frame:16,valueRule:'base+power@1'},
      {key:'wind',kind:'cue',frame:16,asset:'fx.air.wind'},
    ],
  },
};
const edited = structuredClone(authored);
edited.branches.ground[0].frame=14;
edited.branches.ground[1].frame=15;
const rules={'base+power@1':({base,power})=>base+power};
const assets={'fx.ground.dust':'dust-resource','fx.air.wind':'wind-resource'};
function run(doc, branch, context, timing=Math.ceil, engineRules=rules) {
  assert.equal(doc.schema,1);
  return doc.branches[branch].map(task=>{
    const tick=timing(task.frame*30/doc.rate);
    const id=doc.move+':'+branch+':'+task.key;
    if(task.kind==='damage'){
      if(!Object.hasOwn(engineRules,task.valueRule))throw new Error('Missing rule '+task.valueRule);
      return {id,tick,value:engineRules[task.valueRule](context)};
    }
    if(!Object.hasOwn(assets,task.asset))throw new Error('Missing asset '+task.asset);
    return {id,tick,asset:task.asset};
  });
}
const ctx={base:10,power:4};
const importData=JSON.parse(JSON.stringify(edited));
const after=Object.fromEntries(['ground','air'].map(b=>[b,run(importData,b,ctx)]));
assert.deepEqual(after.ground,[{id:'hammer:ground:hit',tick:7,value:14},{id:'hammer:ground:dust',tick:8,asset:'fx.ground.dust'}]);
assert.deepEqual(after.air,run(authored,'air',ctx));
const unsafeRound=run(importData,'ground',ctx,Math.floor);
assert.equal(unsafeRound[1].tick,7);
assert.notDeepEqual(after.ground,unsafeRound);
const otherContext=run(importData,'ground',{base:10,power:9});
assert.equal(otherContext[0].value,19);
const sameKeyDifferentRule=run(importData,'ground',ctx,Math.ceil,{'base+power@1':({base,power})=>base+2*power});
assert.equal(sameKeyDifferentRule[0].value,18);
assert.notDeepEqual(sameKeyDifferentRule,after.ground);
const badRule=structuredClone(edited);
delete badRule.branches.ground[0].valueRule;
assert.throws(()=>run(JSON.parse(JSON.stringify(badRule)),'ground',ctx),/Missing rule/);
const badAsset=structuredClone(edited);
badAsset.branches.ground[1].asset='unmapped.unreal.path';
assert.throws(()=>run(JSON.parse(JSON.stringify(badAsset)),'ground',ctx),/Missing asset/);
console.log(JSON.stringify({before:run(authored,'ground',ctx),after,otherContext,unsafeRound,sameKeyDifferentRule,missingRuleRejected:true,missingAssetRejected:true},null,2));
