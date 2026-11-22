import assert from 'node:assert/strict';
import { MessageFormat } from 'messageformat';
import { DraftFunctions } from 'messageformat/functions';
const rows = [
  ['private','*','PRIVATE'],
  ['*','one','ONE'],
  ['*','*','DEFAULT']
];
const selectors = [
  '.input {$mode :string}',
  '.input {$slots :string}'
].join('\n');
function source(order, variants, transpose=false) {
  return selectors + '\n.match ' + order + '\n' +
    variants.map(([mode,slots,label]) => (transpose ? [slots,mode] : [mode,slots]).join(' ') + ' {{' + label + '}}').join('\n');
}
const a=source('$mode $slots',rows);
const rowOrder=source('$mode $slots',[...rows].reverse());
const selectorOrder=source('$slots $mode',rows,true);
const formattingOnly = a.replace('.input {$slots :string}', '.input {$slots :datetime}');
const incompleteFirst = a.replace('private *', 'private many');
for (const [id, msg, params, expected, diagnostics, options] of [
  ['overlap', a, {mode:'private', slots:'one'}, 'PRIVATE', []],
  ['rows reversed', rowOrder, {mode:'private', slots:'one'}, 'PRIVATE', []],
  ['selectors swapped', selectorOrder, {mode:'private', slots:'one'}, 'ONE', []],
  ['first key alone not enough', incompleteFirst, {mode:'private', slots:'one'}, 'ONE', []],
  ['same text, missing slots', a, {mode:'private'}, 'PRIVATE', ['unresolved-variable']],
  ['valid catchall', a, {mode:'public',slots:'many'}, 'DEFAULT', []],
  ['catchall, missing slots', a, {mode:'public'}, 'DEFAULT', ['unresolved-variable']],
  ['formatting-only selector', formattingOnly, {mode:'private',slots:new Date('2026-01-01T00:00:00Z')}, 'PRIVATE', ['bad-selector'], {functions:DraftFunctions}],
  ['formatting-only selector not registered', formattingOnly, {mode:'private',slots:new Date('2026-01-01T00:00:00Z')}, 'PRIVATE', ['unknown-function','bad-selector']]
]) {
  const errors=[];
  const variant=new MessageFormat('en',msg,options).format(params,e=>errors.push([e.type??e.name,e.message]));
  assert.equal(variant,expected,id);
  assert.deepEqual(errors.map(([type])=>type),diagnostics,id);
  console.log(JSON.stringify({id,variant,errors}));
}
const raw = a.replace('{{PRIVATE}}', '{{仅邀请加入：{$room}}}');
const rawErrors=[];
const rawText=new MessageFormat('zh',raw).format({mode:'private', slots:'one'},e=>rawErrors.push(e.type));
assert.deepEqual(rawErrors,['unresolved-variable']);
console.log(JSON.stringify({id:'raw active branch adds missing room',text:rawText,errors:rawErrors}));
let constructorType;
try { new MessageFormat('en',a.replace('* * {{DEFAULT}}','')); } catch (e) { constructorType=e.type??e.name; }
assert.equal(constructorType,'missing-fallback');
console.log(JSON.stringify({id:'constructor without catchall',type:constructorType}));
