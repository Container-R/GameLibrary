// Resolution only; no discovered package code is executed.
const {createRequire}=require('module');const fs=require('fs');
console.log('node',process.version);
for(const base of [process.cwd()+'/probe.js','/home/agent/.local/lib/node_modules/probe.js','/opt/codex/runtimes/codex-primary-runtime/dependencies/node/lib/node_modules/probe.js']) {
 const r=createRequire(base);
 for(const p of ['inkjs','ink']) {
  try {console.log(JSON.stringify({base,package:p,resolved:r.resolve(p)}));}
  catch(e) {console.log(JSON.stringify({base,package:p,error:e.code}));}
 }
}
const d='/home/agent/.local/lib/node_modules';
console.log('global packages',fs.existsSync(d)?fs.readdirSync(d):'missing');
