// Original direct rule regression; planMove is byte-identical to the final article block.
import assert from 'node:assert/strict';
function planMove(m, s, targetId) {
  const reject = reason => ({ accepted: false, reason });
  const item = m.items[s.itemId], source = m.slots[s.sourceId];
  if (!m.open || m.inventoryId !== s.inventoryId || m.epoch !== s.epoch)
    return reject('背包已失效');
  if (!item || item.slot !== s.sourceId ||
      item.version !== s.sourceVersion || source?.item !== s.itemId)
    return reject('来源物品已变化');
  if (typeof targetId !== 'string' || targetId.length === 0)
    return reject('没有新目标格');
  const target = m.slots[targetId];
  if (!target || targetId === s.sourceId) return reject('没有新目标格');
  if (!target.enabled || target.item !== null || !target.accepts.includes(item.type))
    return reject('目标不接纳');

  return { accepted: true, nextModel: {
    ...m,
    slots: { ...m.slots,
      [s.sourceId]: { ...source, item: null },
      [targetId]: { ...target, item: s.itemId } },
    items: { ...m.items,
      [s.itemId]: { ...item, slot: targetId, version: item.version + 1 } }
  } };
}

const make = () => ({open:true,inventoryId:'bag-main',epoch:20,
  slots:Object.fromEntries(['A','B','null','undefined','0',''].map(id=>[id,
    {item:id==='A'?'sword-17':null,enabled:true,accepts:['weapon']} ])),
  items:{'sword-17':{slot:'A',version:5,type:'weapon'}}});
const session = {inventoryId:'bag-main',epoch:20,itemId:'sword-17',sourceId:'A',sourceVersion:5};
const definitions=[
 ['no-hit-null',null,false],['undefined-is-not-id',undefined,false],
 ['number-is-not-id',0,false],['empty-is-not-id','',false],
 ['actual-string-null','null',true],['actual-string-undefined','undefined',true],
 ['actual-string-zero','0',true],['normal-B','B',true],
 ['same-source','A',false],['occupied-B','B',false,m=>{m.slots.B.item='axe'}],
 ['changed-source-version','B',false,m=>{m.items['sword-17'].version=6}],
 ['wrong-inventory','B',false,m=>{m.inventoryId='other'}]
];
const rows=[];
for(const [id,target,expected,mutate] of definitions){
 const m=make();mutate?.(m);const before=JSON.stringify(m);
 const r=planMove(m,session,target);
 assert.equal(r.accepted,expected,id);assert.equal(JSON.stringify(m),before,id+' mutated input');
 if(r.accepted){assert.equal(r.nextModel.items['sword-17'].slot,target);assert.equal(typeof target,'string');
   assert.equal(r.nextModel.slots.A.item,null);assert.equal(r.nextModel.slots[target].item,'sword-17');}
 rows.push({id,targetType:typeof target,targetLabel:target===undefined?'undefined (value)':JSON.stringify(target),expectedAccepted:expected,accepted:r.accepted,inputUnchanged:true,
   finalItemSlot:r.accepted?r.nextModel.items['sword-17'].slot:m.items['sword-17'].slot});
}
console.log(JSON.stringify({kind:'article-rule-regression',runtime:process.version,rows,
 limits:'Runs the literal rule block, not DOM hit testing, browser capture or native input.'},null,2));
