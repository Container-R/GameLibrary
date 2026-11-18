import assert from 'node:assert/strict';
const initial={game:{Space:'dodge',KeyF:'interact'},menu:{Space:'confirm'}};
function setup(){
 let active={revision:1,byContext:structuredClone(initial)},held=new Set(),waitingRelease=new Set();
 let seen=[];
 const hint=(context,action)=>({revision:active.revision,key:Object.keys(active.byContext[context]).find(k=>active.byContext[context][k]===action)});
 const input=(context,key,type)=>{
  if(type==='up'){held.delete(key);waitingRelease.delete(key);return null;}
  if(held.has(key)||waitingRelease.has(key))return null;
  held.add(key);
  const action=active.byContext[context][key]??null;
  if(action)seen.push([active.revision,context,key,action]);
  return action;
 };
 const apply=(context,from,to,choice='reject')=>{
  const table=active.byContext[context];
  if(!table[from]||from===to|| (table[to]&&choice!=='swap'))return false;
  const candidate=structuredClone(active.byContext);
  const t=candidate[context]; const a=t[from]; const b=t[to];delete t[from];t[to]=a;
  if(b)t[from]=b;
  for(const k of held)waitingRelease.add(k);
  active={revision:active.revision+1,byContext:candidate};
  return true;
 };
 return {hint,input,apply,seen};
}
const s=setup();
const before=s.hint('game','dodge');
assert.equal(s.input('game','Space','down'),'dodge');
assert.equal(s.apply('game','Space','KeyF'),false);
const rejected=s.hint('game','dodge');
assert.deepEqual(rejected,before);
assert.equal(s.apply('game','Space','KeyF','swap'),true);
const after=s.hint('game','dodge'), menu=s.hint('menu','confirm');
assert.deepEqual(after,{revision:2,key:'KeyF'});
assert.deepEqual(menu,{revision:2,key:'Space'});
const repeated=s.input('game','Space','down'); assert.equal(repeated,null);
s.input('game','Space','up');
assert.equal(s.input('game','Space','down'),'interact');
s.input('game','Space','up');
assert.equal(s.input('menu','Space','down'),'confirm');
assert.equal(s.input('game','KeyF','down'),'dodge');
console.log(JSON.stringify({before,rejected,after,menu,repeated,received:s.seen},null,2));
