'use strict';
const fs=require('fs'),path=require('path'),os=require('os'),crypto=require('crypto');
const {chromium}=require('playwright');
const root=__dirname;
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex');
const expected={
 'control':[['pointerdown','source'],['pointermove','destination'],['pointerup','destination']],
 'captured-up':[['pointerdown','source'],['gotpointercapture','source'],['pointermove','source'],['pointerup','source'],['lostpointercapture','source']],
 'explicit-release':[['pointerdown','source'],['gotpointercapture','source'],['pointermove','source'],['lostpointercapture','source'],['pointermove','destination'],['pointerup','destination']]
};
(async()=>{
 const result={protocol_id:'pointer-capture-routing-v1',inputs:{},runtime:{node:process.version,playwright:require('playwright/package.json').version,browser:null},cases:[],status:'FAIL',errors:[]};
 for(const f of ['PROTOCOL.md','fixture.html','runner.cjs'])result.inputs[f]=sha(f);
 let browser,context,temp,stage='arguments';
 try{
  if(process.argv.length!==3)throw new Error('BROWSER_ARGUMENT_REQUIRED');
  temp=fs.mkdtempSync(path.join(os.tmpdir(),'pointer-capture-isolated-'));
  for(const n of ['home','config','cache','tmp'])fs.mkdirSync(path.join(temp,n));
  stage='browser-launch';
  browser=await chromium.launch({executablePath:process.argv[2],headless:true,chromiumSandbox:true,timeout:15000,env:{PATH:process.env.PATH,HOME:path.join(temp,'home'),XDG_CONFIG_HOME:path.join(temp,'config'),XDG_CACHE_HOME:path.join(temp,'cache'),TMPDIR:path.join(temp,'tmp'),LANG:'C.UTF-8'}});
  result.runtime.browser=browser.version();
  context=await browser.newContext({viewport:{width:400,height:200},deviceScaleFactor:1});
  await context.route('**/*',route=>route.abort());
  for(const name of Object.keys(expected)){
   stage='case-'+name;
   const page=await context.newPage();page.setDefaultTimeout(5000);const pageErrors=[];page.on('pageerror',()=>pageErrors.push('PAGE_ERROR'));
   await page.setContent(fs.readFileSync(path.join(root,'fixture.html'),'utf8'),{waitUntil:'load'});
   const setup=await page.evaluate(()=>({viewport:{width:innerWidth,height:innerHeight},rects:['source','destination'].map(id=>{const r=document.getElementById(id).getBoundingClientRect();return {id,x:r.x,y:r.y,width:r.width,height:r.height}})}));
   const requiredSetup={viewport:{width:400,height:200},rects:[{id:'source',x:20,y:20,width:100,height:100},{id:'destination',x:220,y:20,width:100,height:100}]};
   if(JSON.stringify(setup)!==JSON.stringify(requiredSetup))throw new Error('SETUP_MISMATCH');
   await page.mouse.move(50,60);await page.evaluate(n=>window.begin(n),name);await page.mouse.down({button:'left'});await page.mouse.move(250,60,{steps:1});
   if(name==='explicit-release'){await page.evaluate(()=>window.releaseCapture());await page.mouse.move(260,60,{steps:1});}
   await page.mouse.up({button:'left'});
   const observation=await page.evaluate(()=>({events:window.trace,capture_errors:window.captureErrors}));
   const errors=[];const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
   if(!eq(setup,{viewport:{width:400,height:200},rects:[{id:'source',x:20,y:20,width:100,height:100},{id:'destination',x:220,y:20,width:100,height:100}]}))errors.push('SETUP_MISMATCH');
   if(!eq(observation.events.map(e=>[e.type,e.target]),expected[name]))errors.push('EVENT_SEQUENCE_MISMATCH');
   const ids=new Set(observation.events.map(e=>e.pointerId));if(ids.size!==1||[...ids].some(x=>!Number.isInteger(x)||x<0))errors.push('POINTER_ID_MISMATCH');
   if(observation.events.some(e=>e.isTrusted!==true))errors.push('UNTRUSTED_EVENT');
   const down=observation.events.filter(e=>e.type==='pointerdown');if(down.length!==1||down[0].hit!=='source'||down[0].x!==50||down[0].y!==60||down[0].buttons!==1||down[0].button!==0)errors.push('DOWN_MISMATCH');
   const moves=observation.events.filter(e=>e.type==='pointermove');const xs=name==='explicit-release'?[250,260]:[250];
   if(!eq(moves.map(e=>[e.x,e.y,e.buttons,e.hit]),xs.map(x=>[x,60,1,'destination'])))errors.push('MOVE_MISMATCH');
   const up=observation.events.filter(e=>e.type==='pointerup');if(up.length!==1||up[0].x!==(name==='explicit-release'?260:250)||up[0].y!==60||up[0].buttons!==0||up[0].button!==0||up[0].hit!=='destination')errors.push('UP_MISMATCH');
   if(observation.capture_errors.length||pageErrors.length)errors.push('EVENT_HANDLER_ERROR');
   result.cases.push({name,setup,...observation,page_errors:pageErrors,errors,status:errors.length?'FAIL':'PASS'});
   await page.close();if(errors.length)throw new Error('CASE_FAILED');
  }
  stage='complete';result.status='PASS';
 }catch(e){result.errors.push({stage,category:e.message==='CASE_FAILED'?'CASE_FAILED':stage==='browser-launch'?'BROWSER_LAUNCH_FAILED':'EXECUTION_FAILED'});}
 finally{if(context)await context.close().catch(()=>{});if(browser)await browser.close().catch(()=>{});if(temp)fs.rmSync(temp,{recursive:true,force:true});}
 process.stdout.write(JSON.stringify(result,null,2)+'\n');process.exitCode=result.status==='PASS'?0:1;
})();
